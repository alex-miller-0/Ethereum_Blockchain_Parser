"""Pull data from geth and parse it into mongo."""

import subprocess
import sys
sys.path.append("./../Preprocessing")
import os
os.environ['ETH_BLOCKCHAIN_ANALYSIS_DIR'] = './../Preprocessing/'
from Crawler import Crawler
import subprocess
import time
LOGDIR = "./../Preprocessing/logs"


subprocess.call([
    "(geth --rpc --rpcport 8545 > {}/geth.log 2>&1) &".format(LOGDIR),
    "(mongod --dbpath mongo/data --port 27017 > {}/mongo.log 2>&1) &".format(LOGDIR)
], shell=True)

print("Booting processes.")
c = Crawler.Crawler()
subprocess.call([
    "(geth --rpc --rpcport 8545 > {}/geth.log 2>&1) &".format(LOGDIR),
    "(mongod --dbpath mongo/data --port 27017 > {}/mongo.log 2>&1) &".format(LOGDIR)
], shell=True)
