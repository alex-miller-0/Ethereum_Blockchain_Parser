"""Interace to parse aggregate data from snapshots of the Ethereum network."""

import tags
from ContractMap import ContractMap
import prices
import os


class ParsedBlocks(object):
    """
    Build a set of aggregate data from a snapshot (using a TxnGraph).

    Description:
    ------------
    Parse the network graphs at each timestamp.
    Time period is every X blocks.
    For each time period, look at aggregate stats.

    Iterate over all edges in the graph snapshot and calculate:
        - Total number of transactions in the network
        - Sum of all transaction amounts
        - Sum of all outflow from exchanges; suggests people entering long term
        - Sum of all inflow to exchanges (suggests people exiting)
        - Number of transactions to contracts (with data)
        - Number of transactions to crowdsale wallets (no data)
        - Number of transactions to peers, but with data, i.e. sending altcoins
        - Number of p2p transactions
        - Number of new addresses
        - Distribution of wealth (mean, std) across addresses that are NOT:

    Tagged addresses consitute:
    A: Exchanges
    B: Mining pools
    C: Crowdsale wallets/contract addresses

    Also tagged are all contract addresses to which data has been sent.

    Lastly, we also want to get the price of ETH (in USD) at the
    timestamp listed in the LAST block of the block range.

    Parameters:
    -----------
    txn_graph: TxnGraph instance (with a prebuilt graph)
    run: boolean, optional. Calculate the data when instantiated.

    """

    def __init__(self, txn_graph, run=True, csv_file="blockchain.csv"):
        """Initialize the graph, address hash maps, and data fields."""
        self.txn_graph = txn_graph
        self.csv_file = csv_file

        # Global data:
        # -------------
        # Tagged addresses (exchanges, mining pools, contracts)
        # 1: Exchanges, 2: Crowdsale contracts, 3: mining pools, 0: Other
        self.tags = tags.tags
        # 1: Contracts, 0: Other
        self.contracts = ContractMap(load=True).addresses

        # Snapshot specific data:
        # ------------------------
        # Bookkeeping
        self.start_block = txn_graph.start_block
        self.end_block = txn_graph.end_block
        self.start_timestamp = txn_graph.start_timestamp
        self.end_timestamp = txn_graph.end_timestamp

        # Historical prices
        self.price = self._getPrice()

        # Relevent metrics:
        # -----------------
        self.data = {
            "timestamp_start": self.start_timestamp,
            "timestamp_end": self.end_timestamp,
            "block_start": self.start_block,
            "block_end": self.end_block,
            "transaction_sum": 0,
            "transaction_count": 0,
            "exchange_out_sum": 0,
            "exchange_out_count": 0,
            "exchange_in_sum": 0,
            "exchange_in_count": 0,
            "contract_txn_sum": 0,
            "contract_txn_count": 0,
            "crowdsale_txn_sum": 0,
            "crowdsale_txn_count": 0,
            "p2p_txn_sum": 0,
            "p2p_txn_count": 0,
            "peer_txns_w_data": 0,
            "new_addresses": 0,
            "peer_wealth_mean": 0,
            "peer_wealth_std": 0
        }
        self.peer_wealth = list()
        self.headers = None
        if run:
            self._setHeaders()
            self.parse()
            self.saveData()

    # PRIVATE METHODS

    def _setHeaders(self):
        """Get the headers that will be used in the CSV data file."""
        self.headers = [key for key in self.data]

    def _getData(self):
        """Return a list of the data in the order of the headers."""
        return [str(self.data[h]) for h in self.headers]

    def _startCSV(self):
        """Create a CSV file if none exists."""
        with open(self.csv_file, "w") as f:
            f.write(', '.join(self.headers)+'\n')

    def _getPrice(self):
        """Get the average of price between these two blocks."""
        return prices.getPrice(
            prices.loadRaw(),
            "weightedAverage",
            self.start_timestamp,
            self.end_timestamp
        )

    def _isPeer(self, addr):
        """
        Determine if a vertex corresponds to a peer address.

        This means it is not a contract, crowdsale, exchange, or mining pool.
        """
        if not self.contracts[addr] and not self.tags[addr]:
            return True
        return False

    # PUBLIC METHODS

    def parse(self):
        """Iterate through the graph to calculate metrics of interest."""
        if not self.headers:
            self._setHeaders()

        vWeights = self.txn_graph.graph.vertex_properties["weight"]
        eWeights = self.txn_graph.graph.edge_properties["weight"]

        # Iterate over vertices (i.e. addresses)
        for v in self.txn_graph.graph.vertices():
            if self._isPeer(v):
                self.peer_wealth.append(vWeights[v])

        # Iterates over a bunch of Edge instances (i.e. transactions)
        address_prop = self.txn_graph.graph.vertex_properties["address"]
        for e in self.txn_graph.graph.edges():
            to_addr = address_prop[e.target()]
            from_addr = address_prop[e.source()]

            amount = eWeights[e]
            # The edgeWeight of this edge is the amount of the transaction
            self.data["transaction_count"] += 1
            self.data["transaction_sum"] += amount

            # If the target/source of the txn is an exchange:
            if self.tags[from_addr] == 1:
                self.data["exchange_out_sum"] += amount
                self.data["exchange_out_count"] += 1
            elif self.tags[to_addr] == 1:
                self.data["exchange_in_sum"] += amount
                self.data["exchange_in_count"] += 1

            # If the target is a crowdsale wallet:
            if self.tags[to_addr] == 2:
                self.data["crowdsale_txn_sum"] += amount
                self.data["crowdsale_txn_count"] += 1

            # If the target is a contract:
            if self.contracts[to_addr]:
                self.data["contract_txn_sum"] += amount
                self.data["contract_txn_count"] += 1

            # If source and target are both peer nodes
            if self._isPeer(to_addr) and self._isPeer(from_addr):
                self.data["p2p_txn_sum"] += amount
                self.data["p2p_txn_count"] += 1

    def saveData(self):
        """Save the data to a line in the CSV file."""
        if not os.path.isfile(self.csv_file):
            self._startCSV()
        with open(self.csv_file, "a") as f:
            f.write(', '.join(self._getData())+'\n')