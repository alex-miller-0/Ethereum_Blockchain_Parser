"""Stream updates to the blockchain from geth to mongo."""
import sys
import os
sys.path.append("Preprocessing/Crawler")
from Crawler import Crawler
sys.path.append("Analysis")
from TxnGraph import TxnGraph
from ParsedBlocks import ParsedBlocks
sys.path.append("Scripts")
from extract import syncCSV
import tqdm


def syncMongo(c):
    """Sync mongo with geth blocks."""
    gethBlock = c.highestBlockEth()
    mongoBlock = c.highestBlockMongo()
    counter = 0
    if gethBlock > mongoBlock:
        print("Syncing Mongo...")
        for i in range(gethBlock-mongoBlock):
            c.add_block(mongoBlock+i)
        counter += 1
        if counter >= 100:
            print("Successfully parsed {} blocks.".format(counter))
            print("Currently at block {} of {}".format(mongoBlock, gethBlock))
            counter = 0

if __name__ == "__main__":
    # Print success every N iterations
    n = 100

    # Initialize a crawler that will catch the mongodb up
    c = Crawler()
    syncMongo(c)

    # Initialize a TxnGraph and save it every N blocks
    N = 1000
    t = None

    # Global vars
    CSVFILE = "Scripts/blockchain.csv"
    STEP = 1000

    # Sync with the CSV file
    if os.path.exists(CSVFILE):
        prev_max_block = syncCSV(CSVFILE)

    # Catch the CSV data up
    _highestBlockMongo = c.highestBlockMongo()

    if prev_max_block + STEP <= _highestBlockMongo:
        t = TxnGraph(1, prev_max_block+STEP)
        for i in tqdm.tqdm(range(_highestBlockMongo//STEP)):
            if t.end_block > prev_max_block:
                blocks = ParsedBlocks(t)
                t.extend(STEP)
            else:
                t.end_block += STEP

    while True:
        # Sync
        syncMongo(c)

        # Initialize TxnGraph if it doesn't exist yet
        if not t:
            t = TxnGraph(1, c.highestBlockMongo())

        # Do the next iteration of the TxnGraph if applciable
        if t.end_block + STEP <= c.highestBlockMongo():
            t.extend(STEP)

        # Print an update at a certain resolution
        if not t.end_block % 10000:
            print("Streaming at block {}".format(t.end_block))
