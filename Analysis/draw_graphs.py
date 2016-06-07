from ChainAnalysis.TxnGraph import TxnGraph
import os
import multiprocessing

# Build and snap a graph based on a tuple of form (start_block, end_block)
def build(blocks, old_graph):
    path_exists = os.path.exists("data/snapshots/")
    assert path_exists, "No path exists to store the snapshots."

    print("Start=%s, End=%s; Building graph."%(blocks[0], blocks[1]))

    if old_graph:
        previous = {"graph": old_graph, "end_block": blocks[0]}
    else:
        previous = None
    tmp = TxnGraph(blocks[0], blocks[1], previous=previous)
    tmp.draw()
    return tmp.graph, blocks[1]




if __name__=="__main__":
    # Take a bunch of snapshots based on the resolution.
    # Between each snapshot, pass the previous graph object and the previous
    # end_block number as the start_block in the new snapshot.
    resolution = 100000

    block_max = 1000000
    tmp_graph = None
    tmp_last_block = 0
    for i in range(block_max//resolution):
        tmp_graph, tmp_last_block = build(
            (tmp_last_block, resolution*i), tmp_graph
        )
