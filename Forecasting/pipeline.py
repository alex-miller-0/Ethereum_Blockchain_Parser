"""A pipeline taking in data from a CSV and formatting it for forecasting."""
import copy
import numpy as np
import pandas as pd
from r_io_util import *


def pipeline(df):
    """
    Process a dataframe for forecasting.

    Input:
    ------
    df: Pandas dataframe containing both exogenous and endogenous variables.

    Output:
    -------
    endog (numpy array), exog (numpy array), ts (numpy array): arrays
        representing timeseries data of:
        price, exogenous features, end, respectively.

    Note that block_end replaces the traditional timestamp.
    """
    diff_cols = [
        "contract_txn_count",
        "contract_txn_sum",
        "crowdsale_txn_count",
        "crowdsale_txn_sum",
        "exchange_in_count",
        "exchange_in_sum",
        "exchange_out_count",
        "exchange_out_sum",
        "num_addr",
        "p2p_txn_count",
        "p2p_txn_sum",
        # "peer_txns_w_data",
        "transaction_count",
        "transaction_sum",
        "priceUSD"
    ]
    # Get the time domain (i.e. block_end)
    block_end = np.array(df["block_end"])

    # Do single lag differencing
    lag = 1
    df = difference(df, diff_cols, lag=lag)

    # Split into endog and exog
    endog, exog = endog_exog(df, diff_cols, lag=lag)

    return np.array(endog), np.array(exog), block_end


def endog_exog(df, cols, lag=1):
    """
    Convert dataframe into endog and exog numpy arrays.

    Since everything is differenced, remove the first item in each array.
    """
    diff_cols = ["d_{}_{}".format(lag, col) for col in cols]
    exog = df[diff_cols][1:]
    endog = df["d_{}_priceUSD".format(lag)][1:]

    return endog, exog


def difference(df, cols, lag=1):
    """
    Perform differencing on some columns in a dataframe.

    Input:
    ------
    df: pandas dataframe containing the timeseries data.
    cols: list of strings indicating which columns to difference
    """
    df2 = copy.deepcopy(df)

    # Difference based on the lag provided.
    for i in range(1, len(df2["block_end"])):
        for L in cols:
            curr = df2.loc[i, L]
            prev = df2.loc[i-lag, L]
            df2.loc[i, "d_{}_{}".format(lag, L)] = curr - prev

    return df2


def parse_df(filename):
    """Given a filename, load the data into a dataframe."""
    df = pd.read_csv(filename)
    return df
