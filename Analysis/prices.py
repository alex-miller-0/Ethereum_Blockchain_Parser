"""Make a request to Poloniex for historical price data and parse it."""

import requests
from collections import defaultdict
import tqdm
import pickle
import os
DIR = os.environ['ETH_BLOCKCHAIN_ANALYSIS_DIR']

def getData(period=300):
    """Get data from Poloniex API given a period. Returns a list."""
    base = "https://poloniex.com/public?command=returnChartData"
    pair = "USDT_ETH"
    start = 1405699200
    end = 9999999999
    period = period

    req_str = "{}&currencyPair={}&start={}&end={}&period={}".format(
        base, pair, start, end, period
    )
    data = requests.get(req_str)
    return data.json()


def saveRaw(data):
    """Save the raw data to a local pickle file."""
    with open("{}.raw_prices.p".format(DIR), "wb") as output:
        pickle.dump(data, output)
        output.close()


def loadRaw():
    """Load raw data."""
    with open("{}.raw_prices.p".format(DIR), "rb") as input:
        return pickle.load(input)


def getPrice(data, field, timestamp, period=300):
    """Get the closing price of the date closest to the timestamp."""
    for d in data:
        # This loops through dates in order so we want the one right before
        # the provided timestamp.
        if timestamp - d["date"] <= 300:
            return d[field]

if __name__ == "__main__":
    # polo_data = getData()
    # saveRaw(polo_data)
    # polo_data = loadRaw()
    pass
