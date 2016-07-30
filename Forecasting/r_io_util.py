"""A util file for I/O related to R."""
import subprocess
import pandas as pd
import numpy as np
import os

def R_push_csv(endog, exog):
    """Save current endog and exog dfs to CSV files in the R directory."""
    np.savetxt("R/endog.csv", endog, delimiter=",")
    np.savetxt("R/exog.csv", exog, delimiter=",")
    return


def R_pull_csv():
    """Read from the CSV produced by R and return the prediction."""
    return pd.read_csv("R/tmp.csv")['pred'][0]


def R_predict(p, d, q):
    """Run Rscript to produce a pointwise prediction given CSV files."""
    subprocess.call(["Rscript", "R/arima.R", str(p), str(d), str(q)])


def R_cleanup():
    """Delete all CSV files in the R directory."""
    dir = os.path.dirname(os.path.realpath(__file__))
    for file in os.listdir("R"):
        if file.endswith(".csv"):
            try:
                os.remove(os.path.join(dir, file))
            except:
                pass
