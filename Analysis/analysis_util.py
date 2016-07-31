"""Util functions for Analysis process."""
import os


def set_env():
    """Set the analysis environment directory."""
    env = {
            "mongo": ".",      # Where the mongo data is stored
            "txn_data": "./data"    # Where the TxnGraphs are stored
        }
    if 'BLOCKCHAIN_MONGO_DATA_DIR' in os.environ:
        env["mongo"] = os.environ['BLOCKCHAIN_MONGO_DATA_DIR']

    if 'BLOCKCHAIN_DATA_DIR' in os.environ:
        env["tnx_data"] = os.environ['BLOCKCHAIN_DATA_DIR']

    return env
