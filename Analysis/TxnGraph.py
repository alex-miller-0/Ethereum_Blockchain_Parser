"""Create a snapshot of the Ethereum network."""

import six.moves.cPickle as pickle
from graph_tool.all import *
import pymongo
import os
import subprocess
import signal
import copy
from tags import tags
import analysis_util
env = analysis_util.set_env()
DIR = env["mongo"] + "/data"
DATADIR = env["txn_data"]

class TxnGraph(object):
    """
    Create a snapshot of the Ethereum network.

    Description:
    ------------
    Create a snapshot, which contains a graph, out of transactions stored in a
    mongo collection. Each snapshot must start at some time t0 (start_block)
    and end at time tf (end_block). It will include all nodes that sent or
    received a transaction between t0 and tf.


    Parameters:
    -----------
    start_block <int>              # The lower bound of the block range to
                                   # be analysed.
    end_block <int>                # The upper range of the block range to
                                   # be analysed.
    previous <dict>                # Previous graph and its end_block
    snap <bool> (default=True)     # Build the graph upon instantiation.
    save <bool> (default=True)     # Save the graph automatically
    load <bool> (default=False)    # Skip building the graph and load a


    Usage:
    ------
    Initialize with a previous graph:

        g = TxnGraph(previous={graph: <Graph>, end_block: <int>})

    Draw the image (saved by default to DATADIR/snapshots/a_b.png,
    where a=start_block, b=end_block):

        g.draw()

    Save the state of the object (including the graph):

        g.save()

    Load a graph with start_block=a, end_block=b from DATADIR if it exists:

        g.load(a, b)

    """

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
        self.start_block = max(args[0] if len(args) > 0 else 1, 1)
        self.end_block = args[1] if len(args) > 1 else 2

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
        # All addresses (each node has an address)
        self.addresses = None
        # Record big exchange addresses
        self.exchanges = list()
        # Record all contracts
        self.contracts = list()
        # Run
        self._init(snap, save, load, previous)

    def _init(self, snap, save, load, previous):
        self.graph = Graph()

        # Accept a previous graph as an argument
        if previous:
            a_str = "prev is of form {'graph': <Graph>, 'end_block': <int>}"
            assert "graph" in previous, a_str
            self.graph = previous["graph"]
            assert "end_block" in previous, a_str
            self.start_block = previous["end_block"]

        # Set filepaths
        self._setFilePaths()

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

    def _setFilePaths(self, start=None, end=None):
        """Set the file paths based on the start/end block numbers."""
        if not start:
            start = self.start_block
        if not end:
            start = self.end_block

        self.f_pickle = "{}/pickles/{}_{}.p".format(DATADIR, start, end)
        self.f_graph = "{}/graphs/{}_{}.gt".format(DATADIR, start, end)
        self.f_snapshot = "{}/snapshots/{}_{}.png".format(DATADIR, start, end)

    def _getMongoClient(self):
        """Connect to a mongo client (assuming one is running)."""
        try:
            # Try a connection to mongo and force a findOne request.
            # See if it makes it through.
            client = pymongo.MongoClient(serverSelectionTimeoutMS=1000)
            transactions = client["blockchain"]["transactions"]
            test = client.find_one({"number": {"$gt": 1}})
            popen = None
        except Exception as err:
            # If not, open up a mongod subprocess
            cmd = "(mongod --dbpath {} > {}/mongo.log 2>&1) &".format(
                os.environ["BLOCKCHAIN_MONGO_DATA_DIR"],
                os.environ["BLOCKCHAIN_ANALYSIS_LOGS"])

            popen = subprocess.Popen(cmd, shell=True)
            client = pymongo.MongoClient(serverSelectionTimeoutMS=1000)
            transactions = client["blockchain"]["transactions"]

        # Update timestamps
        transactions = self._updateTimestamps(transactions)

        return transactions, popen

    def _updateTimestamps(self, client):
        """Lookup timestamps associated with start/end blocks and set them."""
        start = client.find_one({"number": self.start_block})
        end = client.find_one({"number": self.end_block})
        self.start_timestamp = start["timestamp"]
        self.end_timestamp = end["timestamp"]
        return client

    def _addEdgeWeight(self, newEdge, value):
        """
        Add to the weight of a given edge (i.e. the amount of ether that has
        flown through it). Create a new one if needed.
        """
        if self.edgeWeights[newEdge] is not None:
            self.edgeWeights[newEdge] += value
        else:
            self.edgeWeights[newEdge] = 0

    def _addVertexWeight(self, from_v, to_v, value):
        """
        Add to the weight of a given vertex (i.e. the amount of ether)
        it holds. Create a new weight if needed.
        """
        if self.vertexWeights[to_v] is not None:
            self.vertexWeights[to_v] += value
        else:
            self.vertexWeights[to_v] = 0
        if self.vertexWeights[from_v] is not None:
            # We shouldn't need to worry about overspending
            # as the ethereum protocol should not let you spend
            # more ether than you have!
            self.vertexWeights[from_v] -= value
        else:
            self.vertexWeights[from_v] = 0

    def _addBlocks(self, client, start, end):
        """Add new blocks to current graph attribute."""
        # Get a cursor containing all of the blocks
        # between the start/end blocks
        blocks = client.find(
            {"number": {"$gt": start, "$lt": end}},
            sort=[("number", pymongo.ASCENDING)]
        )
        for block in blocks:
            if block["transactions"]:
                # Loop through all of the transactions in the current block
                # Add all the nodes to a global set (self.nodes)
                for txn in block["transactions"]:

                    # Graph vetices will be referenced temporarily, but the
                    #   unique addresses will persist in self.nodes
                    to_v = None
                    from_v = None

                    # Exclude self referencing transactions
                    if txn["to"] == txn["from"]:
                        continue

                    # Set the "to" vertex
                    if txn["to"] not in self.nodes:
                        to_v = self.graph.add_vertex()
                        self.nodes[txn["to"]] = to_v
                        self.addresses[to_v] = txn["to"]

                        # If there is data, this is going to a contract
                        if "data" in txn:
                            if txn["data"] != "0x":
                                self.contracts.append(txn["to"])
                    else:
                        to_v = self.nodes[txn["to"]]

                    # Set the "from" vertex
                    if txn["from"] not in self.nodes:
                        from_v = self.graph.add_vertex()
                        self.nodes[txn["from"]] = from_v
                        self.addresses[from_v] = txn["from"]
                    else:
                        from_v = self.nodes[txn["from"]]

                    # Add a directed edge
                    newEdge = self.graph.add_edge(from_v, to_v)
                    self.edges.append(newEdge)

                    # Update the weights
                    self._addEdgeWeight(newEdge, txn["value"])
                    self._addVertexWeight(from_v, to_v, txn["value"])
        self._addPropertyMaps()

    def _addPropertyMaps(self):
        """Add PropertyMap attributes to Graph instance."""
        self.graph.vertex_properties["weight"] = self.vertexWeights
        self.graph.vertex_properties["address"] = self.addresses
        self.graph.edge_properties["weight"] = self.edgeWeights

    # PUBLIC
    # ------
    def snap(self):
        """
        Take a snapshot of the graph of transactions.

        Description:
        ------------
        This essentially builds a graph with addresses (vertices) and
        transactions (edges). It also adds a PropertyMap of <double>s to the
        graph corresponding to transaction amounts (i.e. weights). The default
        behavior of this is to initialize a new graph with data between
        start_block and end_block, however it can be used with the 'extend'
        method.

        Parameters:
        -----------
        start <int>, default self.start_block: the absolute block to start with
        end <int>, default self.end_block: the absolute block to end with
        """

        # Set up the mongo client
        client, popen = self._getMongoClient()

        # Add PropertyMaps
        self.edgeWeights = self.graph.new_edge_property("double")
        self.vertexWeights = self.graph.new_vertex_property("double")
        self.addresses = self.graph.new_vertex_property("string")

        # Add blocks to the graph
        self._addBlocks(client, self.start_block, self.end_block)

        # Kill the mongo client if it was spawned in this process
        if popen:
            # TODO get this to work
            popen.kill()

    def save(self):
        """Pickle TxnGraph. Save the graph_tool Graph object separately."""
        if not os.path.exists(DATADIR+"/pickles"):
            os.makedirs(DATADIR+"/pickles")
        if not os.path.exists(DATADIR+"/graphs"):
            os.makedirs(DATADIR+"/graphs")
        if not os.path.exists(DATADIR+"/snapshots"):
            os.makedirs(DATADIR+"/snapshots")

        # We cannot save any of the graph_tool objects so we need to stash
        # them in a temporary object
        tmp = {
            "nodes": self.nodes,
            "edges": self.edges,
            "edgeWeights": self.edgeWeights,
            "vertexWeights": self.vertexWeights,
            "addresses": self.addresses,
            "graph": self.graph
        }
        # Empty the graph_tool objects
        self.nodes = dict()
        self.edges = list()
        self.edgeWeights = None
        self.vertexWeights = None
        self.addresses = None

        # Save the graph to a file (but not if it is empty)
        if len(self.nodes) > 0:
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
        self.addresses = tmp["addresses"]
        self.graph = tmp["graph"]

    def load(self, start_block, end_block):
        """
        Load a TxnGraph.

        Description:
        ------------
        Load a pickle of a different TxnGraph object as well as a saved Graph
        object as TxnGraph.graph. This can be called upon instantiation with
        load=True OR can be called any time by passing new start/end block
        params.

        Parameters:
        -----------
        start_block <int>
        end_block <int>
        """
        self._setFilePaths(start_block, end_block)

        # Load the graph from file
        tmp_graph = load_graph(self.f_graph)

        # Load the object from a pickle
        with open(self.f_pickle, "rb") as input:
            tmp = pickle.load(input)
            self.__dict__.update(tmp)
            self.graph = tmp_graph
            input.close()

    def draw(self, **kwargs):
        """
        Draw the graph.

        Description:
        ------------
        Draw the graph and save to a .png file indexed by the start and
        end block of the TxnGraph

        Parameters:
        -----------
        w <int> (optional, default=5000): width
        h <int> (optional, default=5000): height
        """
        w = kwargs["w"] if "w" in kwargs else 1920*2
        h = kwargs["h"] if "h" in kwargs else 1080*2

        # We want the vertices to be sized proportional to the number of
        # transactions they are part of
        # deg = self.graph.degree_property_map("total")
        deg = copy.deepcopy(self.graph.vertex_properties['weight'])

        # Don't draw an empty graph
        if not self.graph.num_vertices():
            print("Nothing to draw!")
            return

        # Testing to allow negative numbers
        deg.a = abs(deg.a)**0.5

        # For some reason this works
        # (TODO figure out how to scale this consistently)
        # deg.a = deg.a**0.5

        # We want the largest node to be roughly 10%
        # of the width of the image (somewhat arbitrary)
        scale = (0.03*w)/max(deg.a)
        deg.a = deg.a*scale

        # For some reason this doesn't work
        # deg.a = deg.a*scale # For some reason this blows up the output

        # Set K=scale because we want the average edge length
        # to be the size of the largest node
        pos = random_layout(self.graph, shape=(w, h), dim=2)

        # Draw the graph
        graph_draw(self.graph,
            pos=pos,
            vertex_size=deg,
            vertex_fill_color=deg,
            pen_width=0,
            bg_color=[1,1,1,1],
            output=self.f_snapshot,
            output_size=(w,h),
            fit_view=True
        )

    def extend(self, n, save=True):
        """
        Add n blocks to the current TxnGraph instance.

        Description:
        ------------
        Rather than creating a bunch of TxnGraph instances from scratch,
        this method can be used to add n blocks to the existing TxnGraph
        instance. It can be called multiple times to iterate over the block
        chain with resolution of n blocks. The extended TxnGraph will be
        saved by default.

        Parameters:
        -----------
        n <int>: number of blocks to add (from the last_block)
        save <bool>, default True: save the new state automatically
        """
        old_end = self.end_block
        new_end = self.end_block + n

        client, popen = self._getMongoClient()
        self._addBlocks(client, old_end, new_end)
        self.end_block = new_end
        self._setFilePaths()

        if save:
            self.save()
