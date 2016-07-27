"""
Parse a bunch of snapshots of the blockchain and dump contents into a CSV file.
"""
import sys
sys.path.append("./../Analysis")
import os
os.environ['ETH_BLOCKCHAIN_ANALYSIS_DIR'] = './../Analysis/'
from ParsedBlocks import ParsedBlocks
from TxnGraph import TxnGraph
import tqdm

def syncCSV(filename):
    """Resume populating the CSV file."""
    block = 0
    with open(filename, "r") as f:
        for line in f:
            data = line.split(",")
            try:
                if int(data[0]) > block:
                    block = int(data[0])
            except:
                pass
    return block


if __name__ == "__main__":
    max_block = 1600000
    resolution = 1000
    CSVFILE = "blockchain.csv"
    STEP = 1000
    prev_max_block = 0

    if os.path.exists(CSVFILE):
        prev_max_block = syncCSV(CSVFILE)

    # Always start at block 1 because the data is cumulative.
    # Resume at previous block + 1000
    t = TxnGraph(1, prev_max_block + STEP)
    for i in tqdm.tqdm(range(max_block//resolution)):

        if t.end_block > prev_max_block:
            blocks = ParsedBlocks(t)
            t.extend(STEP)
        else:
            t.end_block += STEP
