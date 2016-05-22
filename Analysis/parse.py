from TxnGraph import TxnGraph
import tags
from ContractMap import ContractMap



class ParsedBlocks(object):
    '''
    INPUT:
    TxnGraph instance (with a snapshot)

    DESCRIPTION:
    Parse the network graphs at each timestamp.
    Time period is every X blocks.
    For each time period, look at aggregate stats.

    Iterate over all edges in the graph snapshot and calculate:
        - Total number of transactions in the network
        - Sum of all transaction amounts
        - Sum of all outflow from exchanges (suggests people entering long term)
        - Sum of all inflow to exchanges (suggests people exiting)
        - Number of transactions to contracts (with data)
        - Number of transactions to crowdsale wallets (no data)
        - Number of transactions to peers, but with data (i.e. sending altcoins)
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
    '''
    def __init__(self, txn_graph, run=True):
        self.txn_graph = txn_graph

        # Tagged addresses (exchanges, mining pools, contracts)

        # 1: Exchanges, 2: Crowdsale contracts, 3: mining pools, 0: Other
        self.tags = tags.tags
        # 1: Contracts, 0: Other
        self.contracts = ContractMap(load=True).addresses

        # Bookkeeping
        self.start_block = txn_graph.start_block
        self.end_block = txn_graph.end_block
        self.start_timestamp = txn_graph.start_timestamp
        self.end_timestamp = txn_graph.end_timestamp

        # Relevent metrics
        self.transaction_sum = 0
        self.transaction_count = 0
        self.exchange_out_sum = 0
        self.exchange_out_count = 0
        self.exchange_in_sum = 0
        self.exchange_in_count = 0
        self.contract_txn_sum = 0
        self.contract_txn_count = 0
        self.crowdsale_txn_sum = 0
        self.crowdsale_txn_count = 0
        self.p2p_txn_sum = 0
        self.p2p_txn_count = 0

        self.peer_txns_w_data = 0
        self.new_addresses = 0

        # The wealth will be represented in a list and before
        #   saving to a DB, the mean/std will be calculated
        self.peer_wealth = list()
        self.peer_wealth_mean = 0
        self.peer_wealth_std = 0

        if run:
            self._parse()

    # PRIVATE

    def _isPeer(self, v):
        '''
        Determine if a vertex corresponds to a peer address
        (i.e. not a contract, crowdsale, exchange, mining pool)
        '''
        if not self.contracts[v] and not self.tags[v]:
            return True
        return False

    def _parse(self):
        '''
        Iterate through edges and vertices to calculate metrics of interest.
        '''
        vWeights = self.txn_graph.graph.vertex_properties["weight"]
        eWeights = self.txn_graph.graph.edge_properties["weight"]

        # Iterate over vertices (i.e. addresses)
        for v in self.txn_graph.graph.vertices():
            if self._isPeer(v):
                self.peer_wealth.append(vWeights[v])

        # Iterates over a bunch of Edge instances (i.e. transactions)
        for e in self.txn_graph.graph.edges():
            amount = eWeights[e]
            # The edgeWeight of this edge is the amount of the transaction
            self.transaction_count += 1
            self.transaction_sum += amount

            # If the target/source of the txn is an exchange:
            if self.tags[e.source()] == 1:
                self.exchange_out_sum += amount
                self.exchange_out_count += 1
            elif self.tags[e.target()] == 1:
                self.exchange_in_sum += amount
                self.exchange_in_count += 1

            # If the target is a crowdsale wallet:
            if self.tags[e.target()] == 2:
                self.crowdsale_txn_sum += amount
                self.crowdsale_txn_count += 1

            # If the target is a contract:
            if self.contracts[e.target()]:
                self.contract_txn_sum += amount
                self.contract_txn_count += 1

            # If source and target are both peer nodes
            if self._isPeer(e.target()) and self._isPeer(e.source()):
                self.p2p_txn_sum += amount
                self.p2p_txn_count += 1
