"""
Build a TxnGraph object and gather the data from it.

TODO Get the price data from:
https://poloniex.com/public?command=returnChartData&currencyPair=BTC_ETH&start=1435699200&end=9999999999&period=300
"""

from ParsedBlocks import ParsedBlocks
from TxnGraph import TxnGraph
import tqdm

if __name__ == "__main__":
    t = TxnGraph(0, 10000)
    for i in tqdm.tqdm(range(50)):
        blocks = ParsedBlocks(t)
        t.extend(10000)
