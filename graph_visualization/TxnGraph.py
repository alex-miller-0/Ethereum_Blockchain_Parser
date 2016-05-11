# This will create a snapshot of the ethereum network
# Each snapshot must start at some time t0 (start_block) and end at time tf (end_block).
# It will include all nodes that sent or received a transaction between t0 and tf.
import pickle
from graph_tool.all import *
import pymongo
import tqdm

class TxnGraph():
    def __init__(self, *args, **kwargs):
        self.f_pickle = None
        self.f_snapshot = None
        self.start_block = args[0]
        self.end_block = args[1]
        self.nodes = dict()     # A lookup table mapping ethereum address --> graph node
        self.edges = list()
        self.graph = None
        self.popularity = list() # A list of {address: {in_degree: <int>, out_degree: <int>}} sorted by in_degree + out_degree
        self.init()

    # Initialization script
    def init(self):
        self.f_pickle = "pickles/%s_%s.p"%(self.start_block, self.end_block)
        self.f_snapshot = "snapshots/%s_%s.png"%(self.start_block, self.end_block)

    # Draw the graph
    def draw(self, **kwargs):
        w = kwargs["w"] if "w" in kwargs else 5000
        h = kwargs["h"] if "h" in kwargs else 5000
        graph_draw(self.graph, output_size=(w, h), output=self.f_snapshot, bg_color=[1,1,1,1])

    # Define what "popularity" means
    def getPopularity(self, in_deg, out_deg):
        return in_deg + out_deg


    # Create a popularity table. This will map an address to its popularity
    def buildPopularity(self):
        tmp_pop = list()
        for k, v in self.nodes.items():
            # The temporary tuple
            tmp = (k, {"in_deg": v.in_degree(), "out_deg": v.out_degree(), "popularity": 0})
            tmp[1]["popularity"] = self.getPopularity(tmp[1]["in_deg"], tmp[1]["out_deg"])

            # Add the tuple to the ordered list
            tmp_pop.append(tmp)

        # Sort the popularity list and add it to the object instance
        self.popularity = sorted(tmp_pop, key=lambda t: t[1]["popularity"])


    # Take a snapshot of the graph of transactions
    def snap(self):
        # Make a new graph
        self.Graph = Graph()

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
                    self.edges.append(self.graph.add_edge(from_v, to_v))

        self.draw()
        self.buildPopularity()
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
