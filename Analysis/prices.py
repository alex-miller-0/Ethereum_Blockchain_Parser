"""Make a request to Poloniex for historical price data and parse it."""

import requests
from collections import defaultdict
import tqdm
import pickle


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
    with open(".raw_prices.p", "wb") as output:
        pickle.dump(data, output)
        output.close()


def loadRaw():
    """Load raw data."""
    with open(".raw_prices.p", "rb") as input:
        return pickle.load(input)


def parseData(data, field):
    """Parse the data into a defaultdict given a list of data and a field."""
    datadict = defaultdict(dict)
    for d in data:
        datadict[d["date"]] = d[field]
    return datadict


if __name__ == "__main__":
    # polo_data = getData()
    # saveRaw(polo_data)
    polo_data = loadRaw()
    price_data = parseData(polo_data, "weightedAverage")
    print(len(price_data))
