"""Utility functions to interact with mongo."""
import pymongo
from collections import deque

DB_NAME = "blockchain"
COLLECTION = "transactions"

def initMongo(client):
    """
    Given a mongo client instance, create db/collection if either doesn't exist

    Parameters:
    -----------
    client <mongodb Client>

    Returns:
    --------
    <mongodb Client>
    """
    db = client[DB_NAME]
    try:
        db.create_collection(COLLECTION)
    except:
        pass
    try:
        # Index the block number so duplicate records cannot be made
        db[COLLECTION].create_index(
			[("number", pymongo.DESCENDING)],
			unique=True
		)
    except:
        pass

    return db[COLLECTION]


def insertMongo(client, d):
    """
    Insert a document into mongo client with collection selected.

    Params:
    -------
    client <mongodb Client>
    d <dict>

    Returns:
    --------
    error <None or str>
    """
    try:
        client.insert_one(d)
        return None
    except Exception as err:
        return err


def highestBlock(client):
    """
    Get the highest numbered block in the collection.

    Params:
    -------
    client <mongodb Client>

    Returns:
    --------
    <int>
    """
    n = client.find_one(sort=[("number", pymongo.DESCENDING)])
    if not n:									# If the database is empty, the highest block # is 0
        return 0
    assert "number" in n, "Highest block is incorrectly formatted"
    return n["number"]


def makeBlockQueue(client):
    """
    Form a queue of blocks that are recorded in mongo.

    Params:
    -------
    client <mongodb Client>

    Returns:
    --------
    <deque>
    """
    queue = deque()
    all_n = client.find({}, {"number":1, "_id":0},
    		sort=[("number", pymongo.ASCENDING)])
    for i in all_n:
        queue.append(i["number"])
    return queue
