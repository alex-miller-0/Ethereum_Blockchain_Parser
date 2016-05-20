#	A client to interact with node and to save data to mongo
import requests, json
from pymongo import MongoClient
import sys, os
sys.path.append( os.path.realpath("%s"%os.path.dirname(__file__)) )
import logging
from util import decodeBlock
import mongo_util
from tqdm import *
import time
from collections import deque

def refresh_logger(filename):
	if os.path.isfile(filename):
		os.remove(filename)
	open(filename, 'a').close()

refresh_logger('logs/crawler.log')
logging.basicConfig(filename='logs/crawler.log',level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Crawler(object):
	def __init__(self, start=True):
		logging.debug("Starting Crawler")
		self.node_host = "http://localhost:2000/"
		self.node_headers = {"content-type": "application/json"}
		self.mongo_client = mongo_util.initMongo(MongoClient())				# Initializes to default host/port = localhost/27017
		self.max_block_mongo = self.highestBlockMongo()						# The max block number that is in mongo
		self.max_block_geth = self.highestBlockEth()						# The max block number in the public blockchain
		self.insertion_errors = list()										# Record errors for inserting block data into mongo
		self.block_queue = mongo_util.makeBlockQueue(self.mongo_client)		# Make a stack of block numbers that are in mongo
		if start:
			self.run()


	#	Get a specific block from the blockchain and filter the data we want from it
	def getBlock(self, n):
		url = self.node_host + "get_block"
		body = {"block_num": n}
		r = requests.post(url, data=json.dumps(body), headers=self.node_headers)
		data = json.loads(r.text)
		if "result" not in data:
			logging.warn("ERROR in response getBlock: %s"%str(data))
		if data["result"] == None:
			logging.warn("Null block number %s"%n)
		assert "result" in data, "Block %s not correctly requested!"%n
		block = decodeBlock(data["result"])
		return block

	# Find the highest numbered block in the current blockchain
	def highestBlockEth(self):
		url = self.node_host + "latest_block"
		logging.debug("Requesting highest block from geth via node server.")
		r = requests.get(url, headers=self.node_headers)
		data = json.loads(r.text)
		logging.debug("Highest block return from node: %s"%str(data))
		assert "result" in data, "Error in highestBlockEth: Could not communicate with node server"
		int_blockNo = int(data["result"], 16)
		logging.info("Highest block found in geth: %s"%int_blockNo)
		return int_blockNo

	# Insert a given (parsed) block into mongo
	def saveBlock(self, block):
		e = mongo_util.insertMongo(self.mongo_client, block)
		if e:
			self.insertion_errors.append(e)

	# Find the highest numbered block in the mongo database
	def highestBlockMongo(self):
		highest_block = mongo_util.highestBlock(self.mongo_client)
		logging.info("Highest block found in mongodb: %s"%highest_block)
		return highest_block


	# Add a block to mongo
	def add_block(self, n):
		b = self.getBlock(n)
		if b:
			self.saveBlock(b)
			time.sleep(0.001)
		else:
			self.saveBlock({"number": n, "transactions": []})

	# Query the blockchain and fill up the mongo db with blocks
	def run(self):
		logging.debug("Processing geth blockchain:")
		logging.info("Highest block found as: %s"%str(self.max_block_geth))
		logging.info("Number of blocks to process: %s"%(len(self.block_queue)))

		# Make sure the database isn't missing any blocks up to this point
		logging.debug("Verifying that mongo isn't missing any blocks...")
		self.max_block_mongo = 1
		test = list()
		if len(self.block_queue) > 0:
			print("Looking for missing blocks...")
			self.max_block_mongo = self.block_queue.pop()
			for n in tqdm(range(1, self.max_block_mongo)):
				if len(self.block_queue) == 0:
					# If we have reached the max index of the queue, break the loop
					break
				else:
					# 	-- If a block with number = current index is not in the queue, add it to mongo.
					#	-- If the lowest block number in the queue (_n) is not the current running index (n),
					#		then _n > n and we must add block n to mongo. After doing so, we will add _n back
					#		to the queue.
					_n = self.block_queue.popleft()
					if n != _n:
						self.add_block(n)
						self.block_queue.appendleft(_n)
						logging.info("Added block %s"%n)

		#	Get all new blocks
		print("Processing remainder of the blockchain...")
		for n in tqdm(range(self.max_block_mongo, self.max_block_geth)):
			self.add_block(n)

		print("Done!\n")
