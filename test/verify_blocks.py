"""Test that the transactions in local blocks are correct."""
import requests
import random
import json
import sys
sys.path.append("../Preprocessing")
from Crawler import Crawler

def test_blocks():
    """
    Check transactions in each of a random sample of blocks.

    Send a request to https://etherchain.org/api/block/:block/tx to get a list
    of all transactions that occurred in that block. Cross-reference with the
    transactions in the local block (in mongo).
    """
    c = Crawler.Crawler(start=False)
    client = c.mongo_client

    sample = random.sample(range(500000, 1500000), 50)
    N = len(sample)

    # Track the number of times the number of transactions is different.
    wrong_nums = 0
    num_error = "Incorrect number of transactions in {}% of {} blocks."

    blocks = client.find({"number": {"$in":sample}})
    for block in blocks:
        n = block["number"]
        uri = "https://etherchain.org/api/block/{}/tx".format(n)
        ethchain = json.loads(requests.get(uri).text)

        # Check the number of transactions in the block
        if len(ethchain["data"]) == len(block["transactions"]):
            wrong_nums += 1

    assert wrong_nums == 0, num_error.format(100.*wrong_nums/N, N)
