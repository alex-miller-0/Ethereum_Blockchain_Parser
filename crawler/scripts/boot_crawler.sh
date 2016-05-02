#!/bin/sh

# DO NOT run this script from its current directory. This script is meant to be called by crawl.py in the parent directory.
LOG="scripts/logs/boot.log"

# Boot geth, the node server, and mongo
(geth --rpc --rpcport 8545 > ${LOG} 2>&1) &
(mongod --dbpath mongo/data --port 27017 > ${LOG} 2>&1) &
(node node/app.js > ${LOG} 2>&1) &


