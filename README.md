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

