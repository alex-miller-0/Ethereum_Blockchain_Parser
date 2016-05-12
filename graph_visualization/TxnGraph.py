# This will create a snapshot of the ethereum network
# Each snapshot must start at some time t0 (start_block) and end at time tf (end_block).
# It will include all nodes that sent or received a transaction between t0 and tf.
import pickle
from graph_tool.all import *
import pymongo
import tqdm

class TxnGraph():
    def __init__(self, *args, snap=True, **kwargs):
        self.f_pickle = None
        self.f_snapshot = None
        self.start_block = args[0]
        self.end_block = args[1]
        self.nodes = dict()         # A lookup table mapping ethereum address --> graph node
        self.edges = list()
        self.graph = None           # A graph_tool Graph object
        self.edgeWeights = None     # This will be a PropertyMap of edges weighted by eth value of transaction
        self.init(snap)

    # Initialization script
    def init(self, snap):
        self.f_pickle = "pickles/%s_%s.p"%(self.start_block, self.end_block)
        self.f_snapshot = "snapshots/%s_%s.png"%(self.start_block, self.end_block)
        if snap:
            self.snap()

    # Draw the graph
    def draw(self, **kwargs):
        w = kwargs["w"] if "w" in kwargs else 1920*2
        h = kwargs["h"] if "h" in kwargs else 1080*2

        # We want the vertices to be sized proportional to the number of transactions they are part of
        deg = self.graph.degree_property_map("total")

        # For some reason this works (TODO figure out how to scale this consistently)
        deg.a = deg.a**0.5

        # We want the largest node to be roughly 10% of the width of the image (somewhat arbitrary)
        scale = (0.1*w)/max(deg.a)
        deg.a = deg.a*scale


        # For some reason this doesn't work
        #deg.a = deg.a*scale # For some reason this blows up the output

        # Set K=scale because we want the average edge length to be the size of the largest node
        pos = sfdp_layout(self.graph, p=2, C=5, K=5*scale)#, eweight=a.edgeWeights, vweight=deg, C=10.)

        # Draw the graph
        graph_draw(self.graph,
            pos=pos,
            vertex_size=deg,
            vertex_fill_color=deg,
            #edge_pen_width=scaledEdgeWeights,
            #edge_control_points=control, # some curvy edges
            bg_color=[1,1,1,1],
            output=self.f_snapshot,
            output_size=(w,h),
            fit_view=True
        )
        #graphviz_draw(self.graph,
        #    pos=pos,
        #    vsize=deg,
        #    vcolor=deg,
        #    output=self.f_snapshot,
        #    size=(w, h),
        #    overlap=False
        #)

    # Take a snapshot of the graph of transactions
    def snap(self):
        # Make a new graph
        self.graph = Graph()
        self.edgeWeights = self.graph.new_edge_property("double")

        client = pymongo.MongoClient()["blockchain"]["transactions"]
        # Get a cursor containing all of the blocks between the start/end blocks
        blocks = client.find({"number":{"$gt": self.start_block, "$lt": self.end_block}}, sort=[("number", pymongo.ASCENDING)])
        for block in blocks:
            if block["transactions"]:
                # Loop through all of the transactions in the current block
                # Add all the nodes to a global set (self.nodes)
                for txn in block["transactions"]:
                    # Graph vetices will be referenced temporarily, but the unique
                    #   addresses will persist in self.nodes
                    to_v = None; from_v = None

                    # Exclude self referencing transactions
                    if txn["to"] == txn["from"]:
                        continue

                    # Set the "to" vertex
                    if txn["to"] not in self.nodes:
                        to_v = self.graph.add_vertex()
                        self.nodes[txn["to"]] = to_v
                    else:
                        to_v = self.nodes[txn["to"]]

                    # Set the "from" vertex
                    if txn["from"] not in self.nodes:
                        from_v = self.graph.add_vertex()
                        self.nodes[txn["from"]] = from_v
                    else:
                        from_v = self.nodes[txn["from"]]

                    # Add a directed edge
                    newEdge = self.graph.add_edge(from_v, to_v)
                    self.edges.append(newEdge)
                    self.edgeWeights[newEdge] = txn["value"]


        self.draw()
        client.kill

    # Save a pickle of this object
    def save(self):
        with open(self.f_pickle, "wb") as output:
            pickle.dump(self.__dict__, output)
            output.close()

    # Load a pickle of another object
    def load(self, start_block, end_block):
        new_f_pickle = "pickles/%s_%s.p"%(start_block, end_block)
        with open(new_f_pickle, "rb") as input:
            tmp = pickle.load(input)
            self.__dict__.update(tmp)
            input.close()
