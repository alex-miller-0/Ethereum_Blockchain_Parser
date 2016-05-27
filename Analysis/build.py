"""
Build a TxnGraph object and gather the data from it.

TODO Get the price data from:
https://poloniex.com/public?command=returnChartData&currencyPair=BTC_ETH&start=1435699200&end=9999999999&period=300
"""

from parse import ParsedBlocks
from TxnGraph import TxnGraph

if __name__ == "__main__":
    t = TxnGraph(0, 400000, load=True)
    blocks = ParsedBlocks(t)
