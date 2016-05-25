from parse import ParsedBlocks
from TxnGraph import TxnGraph

if __name__=="__main__":
    t = TxnGraph(0, 400000, load=True)
    blocks = ParsedBlocks(t)
