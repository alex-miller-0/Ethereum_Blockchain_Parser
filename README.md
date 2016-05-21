# eth-blockchain-data
#### An exploration of the Ethereum blockchain!

## Background

This is a little project to explore the network of ethereum transactions. The goal is to process a copy of the Ethereum blockchain. 

## Prerequisites:

### Geth
[Geth](https://github.com/ethereum/go-ethereum/wiki/Geth) is the go implementation of a full Ethereum node. We will need to run it with the `--rpc` flag in order to make requests about data on the block chain (**WARNING** if you run this on a geth client that has ether in it, make sure you put a firewall 8545 or whatever port you run geth RPC on). A geth instance downloads the blockchain and processes it, saving the blocks as LevelDB files in the specified data directory (`~/.ethereum/chaindata` by default). The geth instance can be queried via RPC with `eth_getBlockByNumber([block, true])` to get the `X-th` block (with `true` indicating we want the transactional data included), which is of the form:
  
    {
      number: 1000000,
      ...
      transactions: [
        {
          blockHash: "0x2052ce710a08094b81b5047ea9df5119773ce4b263a23d86659fa7293251055e",
          blockNumber: 1284937,
          from: "0x1f57f826caf594f7a837d9fc092456870a289365",
          gas: 22050,
          gasPrice: 20000000000,
          hash: "0x654ac26084ee6e40767e8735f38274ef5f594454a4d34cfdd70c93aa95be0c64",
          input: "0x",
          nonce: 6610,
          to: "0xfbb1b73c4f0bda4f67dca266ce6ef42f520fbb98",
          transactionIndex: 27,
          value: 201544820000000000
        }
      ]
    } 

Since I am only interested in `number` and `transactions` for this application, I have thrown out the rest of the data, but there is lots of additional information in the block (explore [here](https://etherchain.org/blocks)).

Using the `from` and `to` addresses in the `transactions` array, I can map the traffic of ether through the network as time processes (since there is a unix `timestamp` in the block itself). Note that the value, gas, and gasPrice are in Wei, where 1 Ether = 10<sup>18</sup> Wei. The numbers are converted into Ether in this tool.

### MongoDB

We will use mongo to essentially copy each block served by Geth, preserving its structure. A lot of the irrelevant data will be thrown out. This project also requires pymongo.

### graph-tool

[graph-tool](https://graph-tool.skewed.de/) is a python library written in C to construct graphs quickly and has a flexible feature set for mapping properties to its edges and vertices. Depending on your system, this may be tricky to install, so be sure and follow their instructions carefully. I recommend you find some way to install it with a package manager because building from source is a pain.

### python3

This was written for python 3.4. Some things will probably break if you try to do this analysis in python 2.




## Preprocessing

Preprocessing is done with the `Crawler` class, which can be found in the `Preprocessing/Crawler` directory. Before instantiating a `Crawler` object, you need to have geth and mongo processes running. This can be done easily by running `boot_scripts.sh` found in the `Crawler/scripts` directory. After these processes are running, either run `Crawler/crawl.py` or start a `Crawler()` instance. This will go through the processes of downloading (if applicable) and processing the blockchain from geth and copying it over to a mongo collection named `transactions`. Note that at the time of writing, the Ethereum blockchain has about 1.5 million blocks so this will take a few hours. Once copied over, you can close the `Crawler()` instance.

## Analysis and Visualization

### TxnGraph

A snapshot of the network (i.e. all of the transactions occurring between two timestamps, or numbered blocks in the block chain) can be taken with a `TxnGraph()` instance. This class can be found in the `Analysis` directory. Create an instance with:

    TxnGraph(a, b)

where a is the starting block (int) and b is ending block (int). This will load a directed graph of all ethereum addresses that made transactions between the two specified blocks. It will also weight vertices by the total amount of Ether at the time that the ending block was mined.

#### Drawing an image:

Once `TxnGraph` is created, it will create a graph out of all of the data in the blocks between a and b. An image can be drawn by calling `TxnGraph.draw()` and specific dimensions can be passed using `TxnGraph.draw(w=A, h=B)` where A and B are ints corresponding to numbers of pixels. By default, this is saved to the `Analysis/data/snapshots` directory.

#### Saving/Loading State (using pickle)

The `TxnGraph` instance state can be pickled with `TxnGraph.save()` where the filename is parameterized by the start/end blocks and is saved, by default, to the `Analysis/data/pickles` directory. Because `graph_tool` `Graph` instances cannot be pickled, they are first dumped to a file with the same parameterization in `Analysis/data/graphs`. If another instance was pickled with a different set of start/end blocks, it can be reloaded with `TxnGraph.load(a,b)`.

#### ContractMap

An important consideration when doing an analysis of the Ethereum network is of smart contract addresses. Much ether flows to and from contracts, which you may want to distinguish from simple peer-to-peer transactions. This can be done by loading a `ContractMap` instance:

    # If a mongo_client is passed, the ContractMap will scan geth via RPC
    # for new contract addresses starting at "last_block".
    cmap = ContractMap(mongo_client, last_block=90000, filepath="./contracts.p")
    cmap.save()

    # If None is passed for a mongo_client, the ContractMap will automatically
    # load the map of addresses from the pickle file specified in "filepath",
    # ./contracts.p by default.
    cmap = ContractMap()

This will create a hash table of all contract addresses using a `defaultdict` and will save it to a pickle file.


