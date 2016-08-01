"""Forecast given timeseries data."""
from pipeline import *
from sklearn.cross_validation import train_test_split
from statsmodels.tsa import arima_model


class Forecast(object):
    """
    A forecasting model. Given timeseries data, make predictions.

    Input:
    ------
    filename: path for the CSV file containing data.

    Methods:
    --------
    split(test_size): split data for cross validation with a given test_size.
    predict(n): predict whether to buy, sell, or hold at block n.
    """

    def __init__(self, filename, USD=100, ETH=1000):
        """Initialize the model with a filename and asset quantities."""
        self.USD = USD
        self.ETH = ETH
        self.p = 0
        self.d = 0
        self.q = 0
        self.model = None
        self._getData(parse_df(filename))

    def _getData(self, filename):
        """Run through the pipeline and load the data."""
        endog, exog, self.end_blocks = pipeline(filename)
        self.endog = endog
        self.exog = exog

    def _pointPredict(self):
        """Predict the next value of the ARIMA model."""
        _last = self.model.nobs
        _next = _last + 1
        _lastExog = self.exog[-1:]
        pred = self.model.predict(_last, _next, exog=_lastExog)
        return pred

    def fitARIMAsm(self, p, d, q, _endog, _exog):
        """Fit an ARIMA model give a set of parameters. Returns model."""
        endog = np.array(_endog)
        exog = np.array(_exog)
        model = arima_model.ARIMA(
            endog,
            order=(p, d, q),
            exog=exog).fit(
                transparams=False
            )
        return model

    def optimizeARIMAsm(self, Ap, Ad, Aq, endog, exog):
        """
        Find an optimal ARIMA model given lists of p, d, and q.

        Split the data to test/train sets and then find the best model.

        Optimization criterion is AIC.
        """
        best_model = None
        best_aic = None
        for p in Ap:
            for d in Ad:
                for q in Aq:
                    # Replace the model if AIC is lower
                    try:
                        _model = self._fitARIMA(p, d, q, endog, exog)
                        if not best_aic:
                            print("Updaing model ({}, {}, {})".format(p, d, q))
                            best_model = _model
                            best_aic = _model.aic
                            self.p = p
                            self.d = d
                            self.q = q
                        elif _model.aic < best_aic:
                            print("Updaing model ({}, {}, {})".format(p, d, q))
                            best_model = _model
                            best_aic = _model.aic
                            self.p = p
                            self.d = d
                            self.q = q
                    except:
                        pass

        # Reset the global model
        self.model = best_model

    def predictARIMAsm(self, start, end, exog=None, dynamic=False):
        """
        Make a series of n predictions given an ARIMA model.

        By default, the predictions will be made on top of self.endog_train

        Note that extra lagged exogenous time slices may need to be passed
        depending on the p level. (Pass end-start + p exogenous slices)
        """
        if exog == None:
            exog = self.exog[start:end]

        prediction = self.model.predict(
            start, end, exog=self.exog[start:end], dynamic=dynamic
        )
        return prediction

    # Predictions in R
    #####################

    def predictARIMA_R(self, p, d, q, endog=None, exog=None):
        """
        Pointwise prediction using forecast package in R.
        """
        # Define endog and exog vars
        if endog is None:
            endog = self.endog
        if exog is None:
            exog = self.exog

        # Use at most 100 points to predict the future
        if len(endog) > 300:
            endog = endog[-300:]
        if len(exog) > 300:
            exog = exog[-300:]

        # Pipe data through R and use its Arima model
        R_push_csv(endog, exog)
        R_predict(p, d, q)
        pred = R_pull_csv()
        R_cleanup()

        return pred
