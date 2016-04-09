var assrt = require('assert'),
    config = require('./config.js'),
	rpc = require('node-json-rpc');
/**
 * Routes to interact with geth
 */

exports.get_block = get_block;
exports.latest_block = latest_block;
exports.rpc_call = rpc_call;

/**
 * Make RPC call to geth
 * @param  {string}   method - geth method to call
 * @param  {array}   params - parameters to send geth
 * @param  {Function} cb - callback function
 */
function rpc_call(method, params, cb){
    console.log("config: ", config)
	var options = {
    	port: config.node.geth_port,
    	host: 'localhost',
	};

	var client = new rpc.Client(options);

	client.call(
		{
			"jsonrpc": "2.0",
			"method": method,
			"params": params,
			"id": 0
		},
		function (err, data) {
			if (err) { cb(err); }
			else { cb(null, data); };
		}
	);
};





/**
 * Get a block from the blockchain.
 * This includes all of the transactions (and their data) in the block
 * @param  {object} req - { block_num: <int> }
 * @param  {object} res - Block data. Of the form:
 * {
  	"data": {
    	"id": 0,
    	"jsonrpc": "2.0",
    	"result": {
    	  "number": "0xf4241",
    	  "hash": "0xcb5cab7266694daa0d28cbf40496c08dd30bf732c41e0455e7ad389c10d79f4f",
    	  "parentHash": "0x8e38b4dbf6b11fcc3b9dee84fb7986e29ca0a02cecd8977c161ff7333329681e",
    	  "nonce": "0x9112b8c2b377fbe8",
    	  "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
    	  "logsBloom": "0x0",
    	  "transactionsRoot": "0xc61c50a0a2800ddc5e9984af4e6668de96aee1584179b3141f458ffa7d4ecec6",
    	  "stateRoot": "0x7dd4aabb93795feba9866821c0c7d6a992eda7fbdd412ea0f715059f9654ef23",
    	  "receiptRoot": "0xb873ddefdb56d448343d13b188241a4919b2de10cccea2ea573acf8dbc839bef",
    	  "miner": "0x2a65aca4d5fc5b5c859090a6c34d164135398226",
    	  "difficulty": "0xb6b4bbd735f",
    	  "totalDifficulty": "0x63056041aaea71c9",
    	  "size": "0x292",
    	  "extraData": "0xd783010303844765746887676f312e352e31856c696e7578",
    	  "gasLimit": "0x2fefd8",
    	  "gasUsed": "0x5208",
    	  "timestamp": "0x56bfb41a",
    	  "transactions": [
    	    {
    	      "hash": "0xefb6c796269c0d1f15fdedb5496fa196eb7fb55b601c0fa527609405519fd581",
    	      "nonce": "0x2a121",
    	      "blockHash": "0xcb5cab7266694daa0d28cbf40496c08dd30bf732c41e0455e7ad389c10d79f4f",
    	      "blockNumber": "0xf4241",
    	      "transactionIndex": "0x0",
    	      "from": "0x2a65aca4d5fc5b5c859090a6c34d164135398226",
    	      "to": "0x819f4b08e6d3baa33ba63f660baed65d2a6eb64c",
    	      "value": "0xe8e43bc79c88000",
    	      "gas": "0x15f90",
    	      "gasPrice": "0xba43b7400",
    	      "input": "0x"
    	    }
    	  ],
    	  "uncles": []
    	}
  	}
 */
function get_block (req, res){
	var method = "eth_getBlockByNumber";
	var params = [req.body.block_num, true];

	rpc_call(method, params, function (err, data){
		if (err) { res.send(500, {error: err}); }
		else { res.send(200, {result: data}) };
	});
};



/**
 * Get the latest block in the network. Response is of the form:
 *  returns a string of hex with the highest block number
 */
function latest_block (req, res){
    var method = "eth_syncing";
    var params = [];

    rpc_call(method, params, function (err, data){
        if (err) { res.send(500, {error: err}); }
        else { res.send(200, {result: data.result.highestBlock}) };
    });
};