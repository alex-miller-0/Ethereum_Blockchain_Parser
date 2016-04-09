#	A client to interact with node and to save data to mongo
import requests, json
from pymongo import MongoClient

import sys, os
sys.path.append( os.path.realpath("%s"%os.path.dirname(__file__)) )
from util import decodeBlock
from mongo import initMongo

class Crawler(object):
	def __init__(self):
		self.node_host = "http://localhost:2000/"
		self.node_headers = {"content-type": "application/json"}
		self.mongo_client = MongoClient()	# Initializes to default host/port = localhost/27017
		initMongo(self.mongo_client)
		

	#	Get a specific block from the blockchain and filter the data we want from it
	def getBlock(self, n):
		url = self.node_host + "get_block"
		body = {"block_num": n}
		r = requests.post(url, data=json.dumps(body), headers=self.node_headers)
		data = json.loads(r.text)
		assert "result" in data, "Block %s not correctly requested!"%n
		block = decodeBlock(data["result"])
		return block

	# Find the highest numbered block in the current blockchain
	def highestBlockEth(self):
		url = self.node_host + "latest_block"
		r = requests.get(url, headers=self.node_headers)
		data = json.loads(r.text)
		assert "result" in data, "Error in highestBlock: Could not communicate with node server"
		return data["result"]

	# Find the highest numbered block in the mongo database