// Imports
var assert = require('assert'),
	MongoClient = require('mongodb').MongoClient;

// Configure node
var node = {
	port: 2000,
	geth_port: 8545
};

// Configure mongo interface
var mongo = {
	collection: "transactions",
	db: "blockchain",
	host: "localhost",
	port: 27017
};

// Mongo db and collection connections
var mongo_db, mongo_c;

// Connect to mongo and export the collection object (mongo_c) for use in routes
// TODO create db and collection if not exists on boot
var mongo_config = function (app) {
	var url = "mongodb://"+mongo.host+":"+mongo.port+"/"+mongo.db;
	MongoClient.connect(url, function(err, database){
		assert.equal(null, err);
		mongo_db = database;
		mongo_c = mongo_db.collection(mongo.collection);
		
		exports.mongo_c = mongo_c;
		exports.mongo_db = mongo_db;

		app.listen(node.port);
	});
};


// Export variables
exports.node = node;
exports.mongo = mongo;
exports.mongo_db = mongo_db;
exports.mongo_c = mongo_c;
exports.mongo_config = mongo_config;