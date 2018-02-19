"""Pull data from geth and parse it into mongo."""

import subprocess
import sys
sys.path.append("./../Preprocessing")
sys.path.append("./../Analysis")
import os
os.environ['ETH_BLOCKCHAIN_ANALYSIS_DIR'] = './../Preprocessing/'
from Crawler import Crawler
from ContractMap import ContractMap
import subprocess
import time
LOGDIR = "./../Preprocessing/logs"


subprocess.call([
    "(geth --rpc --rpcport 8545 > {}/geth.log 2>&1) &".format(LOGDIR),
    "(mongod --dbpath mongo/data --port 27017 > {}/mongo.log 2>&1) &".format(LOGDIR)
], shell=True)

print("Booting processes.")
# Catch up with the crawler
c = Crawler()

print("Updating contract hash map.")
# Update the contract addresses that have been interacted with
ContractMap(c.mongo_client, last_block=c.max_block_mongo)

print("Update complete.")
subprocess.call([
    "(geth --rpc --rpcport 8545 > {}/geth.log 2>&1) &".format(LOGDIR),
    "(mongod --dbpath mongo/data --port 27017 > {}/mongo.log 2>&1) &".format(LOGDIR)
], shell=True)
