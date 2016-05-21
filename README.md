# eth-blockchain-data
#### An exploration of the Ethereum blockchain!

## Background

This is a little project to explore the network of ethereum transactions. The goal is to process a local blockchain by calling geth via RPC. (**WARNING** if you run this on a geth client that has ether in it, make sure you close port 8545 or whatever port you run geth RPC on).

A geth instance downloads the blockchain and processes it, saving the blocks as LevelDB files in the specified data directory (`~/.ethereum/chaindata` by default). The geth instance can be queried via RPC with `eth_getBlockByNumber([block, true])` to get the `X-th` block (with `true` indicating we want the transactional data included), which is of the form:
  
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

## Components

### Crawler

Before instantiating a `Crawler` object, you need to have geth, and mongo processes running. This can be done easily by running `boot_scripts.sh` found in the `Crawler/scripts` directory. After these processes are running, either run `Crawler/crawl.py` or start a `Crawler()` instance. This will go through the processes of downloading (if applicable) and processing the blockchain from geth and copying it over to a mongo collection named `transactions`. Note that at the time of writing, the Ethereum blockchain has about 1.4 million blocks so this will take a few hours. Once copied over, you can close the `Crawler()` instance.

### Graph Visualization

#### TxnGraph

The network can be visualized with a `TxnGraph()` object found found in the `graph_visualization` directory. This uses the python package [graph-tool](https://graph-tool.skewed.de/), which unfortunately cannot be installed via pip. I would advise that you use your OS' package manager to install because there are a lot of dependencies.

Once graph-tool is installed, you can create an instance with

    TxnGraph(a, b)

where a is the starting block (int) and b is ending block (int). This will load a directed graph of all ethereum addresses that made transactions between the two specified blocks.

Once `TxnGraph` is created, it will by default take a snapshot of the block range specified (this can be avoided with `TxnGraph(a, b, snap=False)`, which will also save an image. To take another image with different dimensions, call `TxnGraph.snap(w=A, h=B)` where A and B are ints corresponding to numbers of pixels.

#### Saving State (pickling)

The `TxnGraph` instance state can be pickled with `TxnGraph.save()` where the filename is parameterized by the start/end blocks. If another instance was pickled with a different set of start/end blocks, it can be reloaded with `TxnGraph.load(a,b)`.


