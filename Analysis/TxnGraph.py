# This will create a snapshot of the ethereum network.
# Each snapshot must start at some time t0 (start_block) and end at time
#  tf (end_block). It will include all nodes that sent or received a
#  transaction between t0 and tf.
#import pickle
import six.moves.cPickle as pickle
from graph_tool.all import *
import pymongo
import os, subprocess, signal
import copy
from tags import tags
DIR = "data"

class TxnGraph(object):
    '''
    Create a graph out of transactions stored in a mongo collection.
    Images can be drawn with draw().
    Graphs can be saved with save() or loaded with load(start_block, end_block).

    INPUT:
        start_block <int>              # The lower bound of the block range to
                                       # be analysed.
        end_block <int>                # The upper range of the block range to
                                       # be analysed.
        previous <dict>                # Previous graph and its end_block
        snap <bool> (default=True)     # Build the graph upon instantiation.
        save <bool> (default=True)     # Save the graph automatically
        load <bool> (default=False)    # Skip building the graph and load a
                                       # different graph from disk.
    OUTPUT:
        None

    Usage:
    Initialize with a previous graph:

        g = TxnGraph(previous={graph: <Graph>, end_block: <int>})

    Draw the image (saved by default to DIR/snapshots/a_b.png, where
    a=start_block, b=end_block):

        g.draw()
    '''

    # PRIVATE

    def __init__(self,
                *args,
                snap=True,
                save=True,
                load=False,
                previous=None,
                **kwargs):

        self.f_pickle = None
        self.f_snapshot = None
        self.start_block = args[0] if len(args) > 0 else 0
        self.end_block = args[1] if len(args) > 1 else 1

        self.start_timestamp = None
        self.end_timestamp = None

        # A lookup table mapping ethereum address --> graph node
        self.nodes = dict()
        self.edges = list()
        # A graph_tool Graph object
        self.graph = None
        # Store the graph separately in a file
        self.f_graph = None
        # PropertyMap of edges weighted by eth value of transaction
        self.edgeWeights = None
        # PropertyMap of vertices weighted by eth value they hold
        # at the time of the end_block.
        self.vertexWeights = None
        # Record big exchange addresses
        self.exchanges = list()
        # Record all contracts
        self.contracts = list()


        self._init(snap, save, load, previous)

    def _init(self, snap, save, load, previous):
        self.graph = Graph()

        # Accept a previous graph as an argument
        if previous:
            a_str = "previous is of form {'graph': <Graph>, 'end_block': <int>}"
            assert "graph" in previous, a_str
            self.graph = previous["graph"]
            assert "end_block" in previous, a_str
            self.start_block = previous["end_block"]


        # Set file paths
        self.f_pickle = "%s/pickles/%s_%s.p"%(
            DIR, self.start_block, self.end_block
        )

        self.f_graph = "%s/graphs/%s_%s.gt"%(
            DIR, self.start_block, self.end_block
        )

        self.f_snapshot = "%s/snapshots/%s_%s.png"%(
            DIR, self.start_block, self.end_block
        )

        # Load a previous graph
        if load:
            self.load(self.start_block, self.end_block)

        else:
            # Take a snapshot
            if snap:
                self.snap()

            # Save this graph automatically
            if save:
                self.save()

    def _getMongoClient(self):
        try:
            # Try a connection to mongo and force a findOne request.
            # See if it makes it through.
            client = pymongo.MongoClient(serverSelectionTimeoutMS=1000)
            transactions = client["blockchain"]["transactions"]
            test = client.find_one({"number": {"$gt": 1}})
            popen = None
        except Exception as err:
            # If not, open up a mongod subprocess
            cmd = "(mongod --dbpath %s > %s/mongo.log 2>&1) &"%(
                os.environ["BLOCKCHAIN_MONGO_DATA_DIR"],
                os.environ["BLOCKCHAIN_ANALYSIS_LOGS"])

            popen = subprocess.Popen(cmd, shell=True)
            client = pymongo.MongoClient(serverSelectionTimeoutMS=1000)
            transactions = client["blockchain"]["transactions"]
        return transactions, popen


    def _updateTimestamps(self, client):
        start = client.find_one({"number": self.start_block})
        end = client.find_one({"number": self.end_block})
        self.start_timestamp = start["timestamp"]
        self.end_timestamp = end["timestamp"]
        return client


    # PUBLIC

    def snap(self):
        '''
        INPUT: None
        OUTPUT: None

        Take a snapshot of the graph of transactions.
        This essentially builds a graph with addresses (vertices) and
        transactions (edges). It also adds a PropertyMap of <double>s to the
        graph corresponding to transaction amounts (i.e. weights).
        '''

        # Set up the mongo client
        client, popen = self._getMongoClient()

        # Update timestamps
        client = self._updateTimestamps(client)

        # Add PropertyMaps
        self.edgeWeights = self.graph.new_edge_property("double")
        self.vertexWeights = self.graph.new_vertex_property("double")

        # Get a cursor containing all of the blocks between the start/end blocks
        blocks = client.find(
            {"number":{"$gt": self.start_block, "$lt": self.end_block}},
            sort=[("number", pymongo.ASCENDING)]
        )
        for block in blocks:
            if block["transactions"]:
                # Loop through all of the transactions in the current block
                # Add all the nodes to a global set (self.nodes)
                for txn in block["transactions"]:
                    # Graph vetices will be referenced temporarily, but the
                    #   unique addresses will persist in self.nodes
                    to_v = None; from_v = None

                    # Exclude self referencing transactions
                    if txn["to"] == txn["from"]:
                        continue

                    # Set the "to" vertex
                    if txn["to"] not in self.nodes:
                        to_v = self.graph.add_vertex()
                        self.nodes[txn["to"]] = to_v
                        # If there is data, this is going to a contract
                        if txn["data"] != "0x":
                            self.contracts.append(txn["to"])
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

                    # Update edgeWeights
                    if self.edgeWeights[newEdge] is not None:
                        self.edgeWeights[newEdge] += txn["value"]
                    else:
                        self.edgeWeights[newEdge] = 0
                    # Update vertexWeights
                    if self.vertexWeights[to_v] is not None:
                        self.vertexWeights[to_v] += txn["value"]
                    else:
                        self.vertexWeights[to_v] = 0
                    if self.vertexWeights[from_v] is not None:
                        # We shouldn't need to worry about overspending
                        # as the ethereum protocol should not let you spend
                        # more ether than you have!
                        self.vertexWeights[from_v] -= txn["value"]
                    else:
                        self.vertexWeights[from_v] = 0

        # Kill the mongo client if it was spawned in this process
        if popen:
            ## TODO get this to work
            popen.kill()

    def save(self):
        '''
        INPUT: None
        OUTPUT: None

        Save a pickle of the TxnGraph and save the graph_tool Graph object
        separately.
        '''
        # Dont save empty graphs
        if len(self.nodes) == 0:
            return
        # We cannot save any of the graph_tool objects so we need to stash
        # them in a temporary object
        tmp = {
            "nodes": self.nodes,
            "edges": self.edges,
            "edgeWeights": self.edgeWeights,
            "vertexWeights": self.vertexWeights,
            "graph": self.graph
        }
        # Empty the graph_tool objects
        self.nodes = dict()
        self.edges = list()
        self.edgeWeights = None
        self.vertexWeights = None

        # Save the graph to a file
        self.graph.save(self.f_graph, fmt="gt")
        self.graph = None

        # Save the rest of this object to a pickle
        with open(self.f_pickle, "wb") as output:
            pickle.dump(self.__dict__, output)
            output.close()

        # Reload from tmp
        self.nodes = tmp["nodes"]
        self.edges = tmp["edges"]
        self.edgeWeights = tmp["edgeWeights"]
        self.vertexWeights = tmp["vertexWeights"]
        self.graph = tmp["graph"]

    def load(self, start_block, end_block):
        '''
        INPUT start_block <int>, end_block <int>
        OUTPUT None

        Load a pickle of a different TxnGraph object as well as a saved Graph
        object as TxnGraph.graph.
        This can be called upon instantiation with load=True OR can be called
        any time by passing new start/end block params.
        '''

        self.f_pickle = "%s/pickles/%s_%s.p"%(DIR, start_block, end_block)
        self.f_graph = "%s/graphs/%s_%s.gt"%(DIR, start_block, end_block)
        self.f_snapshot = "%s/snapshots/%s_%s.png"%(DIR, self.start_block, self.end_block)

        # Load the graph from file
        tmp_graph = load_graph(self.f_graph)

        # Load the object from a pickle
        with open(self.f_pickle, "rb") as input:
            tmp = pickle.load(input)
            self.__dict__.update(tmp)
            self.graph = tmp_graph
            input.close()




    # Draw the graph
    def draw(self, **kwargs):
        '''
        INPUT: w <int> (optional, default=5000), h <int> (optional, default=5000)
        OUTPUT: None

        Draw the graph and save to a .png file indexed by the start and
        end block of the TxnGraph
        '''
        w = kwargs["w"] if "w" in kwargs else 1920*2
        h = kwargs["h"] if "h" in kwargs else 1080*2

        # We want the vertices to be sized proportional to the number of
        # transactions they are part of
        #deg = self.graph.degree_property_map("total")
        deg = copy.deepcopy(self.vertexWeights)
        # Don't draw an empty graph
        if not self.graph.num_vertices():
            print("Nothing to draw!")
            return

        # Testing to allow negative numbers
        deg.a = abs(deg.a)**0.5


        # For some reason this works
        #(TODO figure out how to scale this consistently)
        #deg.a = deg.a**0.5

        # We want the largest node to be roughly 10%
        # of the width of the image (somewhat arbitrary)
        scale = (0.03*w)/max(deg.a)
        deg.a = deg.a*scale

        # For some reason this doesn't work
        #deg.a = deg.a*scale # For some reason this blows up the output

        # Set K=scale because we want the average edge length
        # to be the size of the largest node
        pos = random_layout(self.graph, shape=(w, h), dim=2)

        # Draw the graph
        graph_draw(self.graph,
            pos=pos,
            vertex_size=deg,
            vertex_fill_color=deg,
            #edge_pen_width=scaledEdgeWeights,
            #edge_control_points=control, # some curvy edges
            pen_width=0,
            bg_color=[1,1,1,1],
            output=self.f_snapshot,
            output_size=(w,h),
            fit_view=True
            )