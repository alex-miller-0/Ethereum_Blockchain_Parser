#!/bin/sh

# DO NOT run this script from its current directory. This script is meant to be called by crawl.py in the parent directory.
LOGDIR="logs"

# Boot geth, the node server, and mongo
(geth --rpc --rpcport 8545 > ${LOGDIR}/geth.log 2>&1) &
(mongod --dbpath mongo/data --port 27017 > ${LOGDIR}/mongo.log 2>&1) &
(node node/app.js > ${LOGDIR}/node.log 2>&1) &


