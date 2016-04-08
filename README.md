# eth-blockchain-data
An exploration of the Ethereum blockchain!

I want to crawl the Ethereum blockchain and pull out the transactions so that I can explore how the network has evolved over time. 

A geth instance downloads the blockchain and processes it, saving the blocks as LevelDB files in the specified data directory (`~/.ethereum` by default). The geth instance can be queried via RPC with `eth_getBlockByNumber([block, true])` to get the `X-th` block (with `true` indicating we want the transactional data included), which is of the form:
  
    {
      difficulty: 12549332509227,
      extraData: "0xd783010303844765746887676f312e352e31856c696e7578",
      gasLimit: 3141592,
      gasUsed: 50244,
      hash: "0x8e38b4dbf6b11fcc3b9dee84fb7986e29ca0a02cecd8977c161ff7333329681e",
      logsBloom: "0x0",
      miner: "0x2a65aca4d5fc5b5c859090a6c34d164135398226",
      nonce: "0xcd4c55b941cf9015",
      number: 1000000,
      parentHash: "0xb4fbadf8ea452b139718e2700dc1135cfc81145031c84b7ab27cd710394f7b38",
      receiptRoot: "0x20e3534540caf16378e6e86a2bf1236d9f876d3218fbc03958e6db1c634b2333",
      sha3Uncles: "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
      size: 768,
      stateRoot: "0x0e066f3c2297a5cb300593052617d1bca5946f0caa0635fdb1b85ac7e5236f34",
      timestamp: 1455404053,
      totalDifficulty: 7135202464334937706,
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
      ],
      transactionsRoot: "0x65ba887fcb0826f616d01f736c1d2d677bcabde2f7fc25aa91cfbc0b3bad5cb3",
      uncles: []
    } 

Using the `from` and `to` addresses in the `transactions` array, I can map the traffic of ether through the network as time processes (since there is a unix `timestamp` in the block itself). 

