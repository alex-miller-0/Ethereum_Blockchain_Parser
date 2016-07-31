"""Build a hash map of all contract addresses on the Ethereum network."""

from collections import defaultdict
import requests
import json
import pickle
import os
import time
import pymongo
DIR = "."

class ContractMap(object):
    """
    A hash map of all contract addresses in the Ethereum network.

    Public functions:

    - find(): searches all blocks after self.last_block and adds them
            to the table. Updates self.last_block
    - save(): saves the object to a pickle file ".contracts.p"
    - load(): loads the object from pickle file ".contracts.p"

    Attributes:

    - addresses: defaultdict with default value of 0 for non-contracts and
        values of 1 for contract addresses.

    Usage:

    # If a mongo_client is passed, the ContractMap will scan geth via RPC
    # for new contract addresses starting at "last_block".
    cmap = ContractMap(mongo_client, last_block=90000, filepath="contracts.p")
    cmap.save()

    # If None is passed for a mongo_client, the ContractMap will automatically
    # load the map of addresses from the pickle file specified in "filepath",
    # ./contracts.p by default.
    cmap = ContractMap()

    """

    def __init__(self,
                mongo_client=None,
                last_block=0,
                load=False,
                filepath="{}/.contracts.p".format(DIR)):
        """Initialize with a mongo client and an optional last block."""
        self.client = mongo_client
        self.last_block = last_block
        self.url = "http://localhost:8545"
        self.headers = {"content-type": "application/json"}
        self.filepath = filepath

        self.addresses = defaultdict(int)

        if load:
            self.load()

        if self.client:
            self.find()
            self.save()

    def _checkGeth(self):
        """Make sure geth is running in RPC on port 8545."""
        try:
            self._rpcRequest("eth_getBlockByNumber", [1, True], "id")
            return
        except Exception as err:
            assert not err, "Geth cannot be reached: {}".format(err)

    def _rpcRequest(self, method, params, key):
        """Make an RPC request to geth on port 8545."""
        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "2.0",
            "id": 0
        }

        res = requests.post(self.url,
            data=json.dumps(payload),
            headers=self.headers).json()

        # Geth will sometimes crash if overloaded with requests
        time.sleep(0.005)

        return res[key]

    def find(self):
        """
        Build a hash table of contract addresses.

        Iterate through all blocks and search for new contract addresses.
        Append them to self.addresses if found.
        """
        blocks = self.client.find(
            {"number": {"$gt": self.last_block}},
            sort=[("number", pymongo.ASCENDING)]
        )
        counter = 0
        for block in blocks:
            if block["transactions"]:
                # Loop through all of the transactions in the current block
                # Add all the nodes to a global set (self.nodes)
                for txn in block["transactions"]:
                    if txn["to"] and not self.addresses[txn["to"]]:
                        # Get the code at the "to" address.
                        code = self._rpcRequest(
                            "eth_getCode",
                            [txn["to"], "latest"],
                            "result")
                        # Add addressees if there is non-empty data
                        if code != "0x":
                            self.addresses[txn["to"]] = 1

            self.last_block = block["number"]
            counter += 1
            # Save the list every 10000 blocks in case geth crashes
            # midway through the procedure
            if not counter % 10000:
                print("Done with block {}...".format(self.last_block))
                self.save()

    def save(self):
        """Pickle the object and save it to a file."""
        state = (self.last_block, self.addresses)
        pickle.dump(state, open(self.filepath, "wb"))

    def load(self):
        """Load the contract map from a  file."""
        no_file = "Error loading ContractMap: No file exists in that path."
        assert os.path.isfile(self.filepath), no_file
        state = pickle.load(open(self.filepath, "rb"))
        self.addresses = state[1]
        self.last_block = state[0]
