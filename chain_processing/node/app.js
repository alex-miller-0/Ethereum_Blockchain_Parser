/**
 * app.js
 *
 * API for ethereum blockchain crawler
 */

/**************************
	Imports
**************************/
// General packages
var bodyParser = require('body-parser'),
	http = require('http'),
	express = require('express');

// Internal imports
var config = require('./config.js'),
	routes = require('./routes.js');






// Run node on each CPU in the cluster
/*(function init_cluster() {
	var cluster = require('cluster');
	if (cluster.isMaster) {
		var cpuCount = require('os').cpus().length;
		
		// Fork a worker to each CPU in the cluster
		for (var i=0; i< cpuCount; i += 1)
			cluster.fork();

		//Fork a new worker when one dies
		cluster.on('exit', function(worker) {
			cluster.fork();
		})
	}
	else setup_servers();
})();*/
setup_servers();

/**************************
	Functions
**************************/

/**
 * setup_servers
 *
 * @desc - main function that sets up the node.js server
 */
function setup_servers() {
	var api = express();

	// Config allowed headers
	var auth_config = function(req, res, next) {
		res.header('Access-Control-Allow-Origin', '*');
		res.header("Access-Control-Allow-Headers", "X-Requested-With");
		res.header('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE');
		res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, x-access-token');
		next();
	};

	// Config with any third party dependancies
	var basic_config = function() { 
		api.use(bodyParser.json());
		api.use(bodyParser.urlencoded({
  			extended: true
		}));
	};

	

	basic_config();
	api.use(auth_config);
	routes_config(api);
	api.listen(config.node.port);
	
};

/**
 * routes_config
 *
 * @desc - define all of the node.js routes in the webserver
 * @param app - express app
 */
function routes_config(app) {
	app.post('/get_block', routes.get_block);
	app.get('/latest_block', routes.latest_block);
};


