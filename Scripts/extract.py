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
    t = TxnGraph(0, 10000)
    for i in tqdm.tqdm(range(150)):
        blocks = ParsedBlocks(t)
        t.extend(10000)
