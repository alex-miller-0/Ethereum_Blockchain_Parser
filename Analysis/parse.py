from ChainAnalysis.TxnGraph import TxnGraph
from ChainAnalysis.tags import tags
# Parse the network graphs at each timestamp
# Time period is every X blocks
#
# For each time period, look at aggregate stats
#   Iterate over all edges in the graph snapshot and calculate:
#
#   - Total number of transactions in the network
#   - Sum of all transaction amounts
#   - Sum of all outflow from exchanges (suggests people entering long term)
#   - Sum of all inflow to exchanges (suggests people exiting)
#   - Number of transactions to contracts (with data)
#   - Number of transactions to crowdsale wallets (no data)
#   - Number of transactions to peers, but with data (i.e. sending altcoins)
#   - Number of p2p transactions
#   - Number of new addresses
#   - Distribution of wealth (mean, std) across addresses that are NOT:
#       A) Exchanges
#       B) Mining pools
#       C) Crowdsale wallets/contract addresses
#
#   Lastly, we also want to get the price of ETH (in USD) at the
#   timestamp listed in the LAST block of the block range.


class ParsedBlocks(object):
    def __init__(self, txn_graph, run=True):

        # Bookkeeping
        self.start_block = txn_graph.start_block
        self.end_block = txn_graph.end_block
        self.start_timestamp = txn_graph.start_timestamp
        self.end_timestamp = txn_graph.end_timestamp

        # Relevent metrics
        self.transaction_sum = 0
        self.transaction_count = 0
        self.exchange_out_sum = 0
        self.exchange_in_sum = 0
        # TODO also make a hash map of all contract addresses (i.e. all addresses that have )
        # TODO can do this by calling geth rpc with e.g. curl -X POST --data '{"jsonrpc":"2.0","method":"eth_getCode","params":["0xf70d67f47444dd538ab95ddc14ab15b1908cb0d9", "latest"],"id":1}'
        self.contract_txns_w_data = 0
        self.crowdsale_txns_no_data = 0
        self.all_peer_txns = 0
        self.peer_txns_w_data = 0
        self.new_addresses = 0
        # The wealth will be represented in a list and before
        #   saving to a DB, the mean/std will be calculated
        self.wealth = list()
        self.wealth_mean = 0
        self.wealth_std = 0

        if run:
            self._run()

    # PRIVATE

    def _run(self):
        tags = tags
        # Iterates over a bunch of Edge instances (i.e. transactions)
        for e in txn_graph.graph.edges():

            amount = txn_graph.edgeWeight[e]

            # The edgeWeight of this edge is the amount of the transaction
            self.transaction_count += 1
            self.transaction_sum += amount

            # If the source of the txn is an exchange...
            if tags[e.source()] == 1:
                exchange_out_sum += amount
            elif tags[e.target()] == 1:
                exchange_in_sum += amount

            # If the
