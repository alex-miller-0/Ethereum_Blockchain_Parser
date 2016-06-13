"""Util functions for Analysis process."""
import os


def set_env():
    """Set the analysis environment directory."""
    if 'BLOCKCHAIN_MONGO_DATA_DIR' in os.environ:
        return os.environ['BLOCKCHAIN_MONGO_DATA_DIR']
    else:
        return "./"
