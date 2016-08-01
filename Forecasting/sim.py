"""Simulate a trading bot by predicting a series of values using train/test sets."""
from model import Forecast
import numpy as np
import copy
from multiprocessing import Pool

def simulate(p=1, d=0, q=0):
    """
    This bot will perform the following steps.

    1. Load data, pipeline, and split it into training and test sets.
    2. Train an optimized ARIMA model on the training data.
    3. Make a series of point forecasts and store the predictions in a list.
        Prediction requires exogenous variables, so append the next data point
        to both the endogenous and exogenous variables in the Forecast object
        before making the next prediction.
    """
    #print("Loading data...")
    f = Forecast('blockchain.csv')

    # Define an index on which to split (like 80% of the way)
    ixSplit = int(0.8 * f.endog.shape[0])

    # Define training and test sets
    train_endog = f.endog[:ixSplit]
    train_exog = f.exog[:ixSplit]
    test_endog = f.endog[ixSplit:]
    test_exog = f.exog[ixSplit:]

    # Update the instance
    f.endog = train_endog
    f.exog = train_exog

    # Copy test exogenous variables to compare with the predictions
    endog_expected = copy.deepcopy(test_endog)

    # Make a series of predictions
    #print("Making predictions...")
    preds = list()
    for i in range(len(test_exog)):
        # Make the prediction
        pred = f.predictARIMA_R(p, d, q, endog=f.endog, exog=f.exog)
        preds.append(pred)
        # Append the model's data with the first data in the test arrays
        # Note that np.delete is analagous to pop, but -1 indicates the first
        # item in the array.
        f.exog = np.append(f.exog, [test_exog[0]], axis=0)
        test_exog = np.delete(test_exog, 0, axis=0)
        f.endog = np.append(f.endog, [test_endog[0]], axis=0)
        test_endog = np.delete(test_endog, 0)

    return preds, endog_expected


def decisionRule():
    """Decide whether to buy, sell, or hold."""
    pass


def score_simulation(preds, endog_expected):
    """Score a simulation based on mean squared error."""
    MSE = 0
    for i in range(len(preds)):
        MSE += (preds[i] - endog_expected[i])**2
    return MSE


def test_f(gen):
    p = gen[0][0]
    d = gen[0][1]
    q = gen[0][2]
    try:
        preds, exog_expected = simulate(p, d, q)
        score = score_simulation(preds, exog_expected)
    except:
        score = 0
    return (score, p, d, q)


if __name__ == "__main__":
    POOL = Pool(maxtasksperchild=500)
    p_range = range(5)
    d_range = range(5)
    q_range = [0] * 5
    gen = list()
    for _p in p_range:
        for _d in d_range:
            gen.append((_p, _d, 0))
    _gen = zip(gen)
    x = POOL.map(test_f, _gen)
    print("Done")
    print(x)
    # [(0, 0, 0, 0), (0, 0, 1, 0), (0, 0, 2, 0), (0, 0, 3, 0), (0, 0, 4, 0), (29.292981789631671, 1, 0, 0), (0, 1, 1, 0), (0, 1, 2, 0), (0, 1, 3, 0), (0, 1, 4, 0), (0, 2, 0, 0), (0, 2, 1, 0), (0, 2, 2, 0), (0, 2, 3, 0), (0, 2, 4, 0), (0, 3, 0, 0), (0, 3, 1, 0), (54.253053572867898, 3, 2, 0), (0, 3, 3, 0), (0, 3, 4, 0), (0, 4, 0, 0), (0, 4, 1, 0), (0, 4, 2, 0), (0, 4, 3, 0), (250.45917084881501, 4, 4, 0)]
