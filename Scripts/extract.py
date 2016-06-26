"""
Parse a bunch of snapshots of the blockchain and dump the contents into a CSV file.
"""
import sys
sys.path.append("./../Analysis")
import os
os.environ['ETH_BLOCKCHAIN_ANALYSIS_DIR'] = './../Analysis/'
from ParsedBlocks import ParsedBlocks
from TxnGraph import TxnGraph
import tqdm

if __name__ == "__main__":
    max_block = 1700000
    resolution = 1000

    t = TxnGraph(1, 1000)
    for i in tqdm.tqdm(range(max_block//resolution)):
        blocks = ParsedBlocks(t)
        t.extend(1000)
