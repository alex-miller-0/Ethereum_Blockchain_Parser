#	Interact with mongo
import pymongo
from collections import deque

#	Global vars
DB_NAME = "blockchain"
COLLECTION = "transactions"


#	Initialize a mongo client and create db/collection if they do not exist
#	Returns a collection object
def initMongo(client):
	db = client[DB_NAME]						# Connect to the "blockchain" database (or create if not exists)
	try:										# Create the collection if not exists
		db.create_collection(COLLECTION)	
	except Exception as e:
		pass
		#print("Error creating collection: %s"%str(e))
	try:										# Create an index on the block number so duplicate records cannot be made
		db[COLLECTION].create_index([("number", pymongo.DESCENDING)], unique=True)
	except Exception as e:
		pass
		#print("Error creating 'number' index: %s"%str(e))
	
	return db[COLLECTION]


#	Insert a document into mongo
def insertMongo(client, d):
	try:
		result = client.insert_one(d)
		return 0
	except:
		return 1



#	Get the highest numbered block 
#	Returns an integer
def highestBlock(client):
	n = client.find_one(sort=[("number", pymongo.DESCENDING)])
	if not n:									# If the database is empty, the highest block # is 0
		return 0
	assert "number" in n, "Highest block is incorrectly formatted"
	return n["number"]


# Form a queue of blocks in the blockchain that are recorded in mongo
# returns deque object
def makeBlockQueue(client):
	queue = deque()
	all_n = client.find({}, {"number":1, "_id":0}, sort=[("number", pymongo.ASCENDING)])
	for i in all_n:
		queue.append(i["number"])
	return queue
	