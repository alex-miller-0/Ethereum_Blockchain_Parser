#	A client to interact with node and to save data to mongo
import requests, json
from pymongo import MongoClient

import sys, os
sys.path.append( os.path.realpath("%s"%os.path.dirname(__file__)) )
from util import decodeBlock
import mongo_util
from tqdm import *
import time
from collections import deque

class Crawler(object):
	def __init__(self):
		self.node_host = "http://localhost:2000/"
		self.node_headers = {"content-type": "application/json"}
		self.mongo_client = mongo_util.initMongo(MongoClient())				# Initializes to default host/port = localhost/27017
		self.max_block_mongo = self.highestBlockMongo()						# The max block number that is in mongo
		self.max_block_geth = self.highestBlockEth()						# The max block number in the public blockchain
		self.insertion_errors = 0 											# Record errors for inserting block data into mongo
		self.block_queue = mongo_util.makeBlockQueue(self.mongo_client)		# Make a stack of block numbers that are in mongo
		self.run()
		

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
		return int(data["result"], 16)

	# Insert a given (parsed) block into mongo
	def saveBlock(self, block):
		e = mongo_util.insertMongo(self.mongo_client, block)
		self.insertion_errors += e 

	# Find the highest numbered block in the mongo database
	def highestBlockMongo(self):
		highest_block = mongo_util.highestBlock(self.mongo_client)
		return highest_block


	# Query the blockchain and fill up the mongo db with blocks
	def run(self):
		assert self.max_block_geth > self.max_block_mongo, "Mongo Blockchain up to date!"
		print("Processing geth blockchain:")
		print("Number of items in mongo: %s"%(len(self.block_queue)))
		
		def add_block(n):
			b = self.getBlock(n)
			if b:
				self.saveBlock(b)
			time.sleep(0.001)


		# Make sure the database isn't missing any blocks up to this point
		print("Verifying that mongo isn't missing any blocks...")
		self.max_block_mongo = 1
		test = list()
		if len(self.block_queue) > 0:
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
						add_block(n)
						self.block_queue.appendleft(_n)
		
		#	Get all new blocks
		print("Processing remainder of the blockchain...")
		for n in tqdm(range(self.max_block_mongo, self.max_block_geth)):
			add_block(n)

		print("Done!\n")