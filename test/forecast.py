"""Test workflow of forecasting model."""
import sys
sys.path.append("../Forecasting")
import model


def test_forecast():
    """Optimize an ARIMA model and predict a few data points."""
    START = 5
    END = 10
    print("Forecasting...")
    f = model.Forecast('../Forecasting/blockchain.csv')
    f.optimizeARIMA(
        range(5), range(5), range(5), f.endog, f.exog
    )
    pred = f.predictARIMA(START, END)
    assert len(pred) == (END - START)
