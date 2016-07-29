"""Simulate a trading bot by predicting a series of values using train/test sets."""
from model import Forecast
import numpy as np


def simulate():
    """
    This bot will perform the following steps.

    1. Load data, pipeline, and split it into training and test sets.
    2. Train an optimized ARIMA model on the training data.
    3. Make a series of point forecasts and store the predictions in a list.
        Prediction requires exogenous variables, so append the next data point
        to both the endogenous and exogenous variables in the Forecast object
        before making the next prediction.
    """
    print("Loading data...")
    f = Forecast('blockchain.csv')

    # Define an index on which to split (like 80% of the way)
    ixSplit = 0.8 * f.endog.shape[0]
    print("yay")
    # Define training and test sets
    train_endog = f.endog[:ixSplit]
    train_exog = f.exog[:ixSplit]
    test_endog = f.endog[ixSplit:]
    test_exog = f.exog[ixSplit:]

    # Determine an ARIMA model
    #print("Determining model...")
    #ix = [0, 1, 2]
    #f.optimizeARIMA(ix, ix, ix, train_endog, train_exog)

    # Make a series of predictions
    print("Making predictions...")
    preds = list()
    #for i in range(len(test_exog)):
    for i in range(5):
        # Make the prediction
        pred = f.predictARIMA_R()
        preds.append(pred)

        # Append the model's data with the first data in the test arrays
        # Note that np.delete is analagous to pop, but -1 indicates the first
        # item in the array.
        f.exog = np.append(f.exog, np.delete(test_exog, -1, axis=0), axis=0)
        f.endog = np.append(f.endog, np.delete(test_endog, -1, axis=0), axis=0)

        # Refit the model
        # f.model = f.fitARIMAsm(f.p, f.d, f.q, f.endog, f.exog)

    print(preds)


if __name__ == "__main__":
    simulate()
