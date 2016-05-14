from ChainAnalysis.TxnGraph import TxnGraph
import os
import multiprocessing

# Build and snap a graph based on a tuple of form (start_block, end_block)
def build(blocks, overwrite=True):
    path_exists = os.path.exists("visualization/snapshots/%s_%s.png"%(blocks[0], blocks[1]))
    if overwrite or not path_exists:
        print("Start=%s, End=%s; Building graph."%(blocks[0], blocks[1]))
        tmp = TxnGraph(blocks[0], blocks[1])
        tmp.draw()
        tmp.save()

# Build and snapshot the graphs on multiple cores
POOL = multiprocessing.Pool(maxtasksperchild=500)
def run_pool(f, iterator):
    POOL.map(f, iterator)

if __name__=="__main__":
    # Form a list of snapshots to take
    nodes = list(map(lambda i: (50000*i-50000, 50000*i), range(10)))
    # Build and snap in the multicore pool
    run_pool(build, nodes)
