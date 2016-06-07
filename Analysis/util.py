"""Util functions for Analysis process."""
import os


def set_env():
    """Set the analysis environment directory."""
    if 'ETH_BLOCKCHAIN_ANALYSIS_DIR' in os.environ:
        return os.environ['ETH_BLOCKCHAIN_ANALYSIS_DIR']
    else:
        return "./"
