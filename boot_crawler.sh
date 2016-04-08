#!/bin/sh


# Boot geth, the node server, and mongo
echo "Booting geth..."
(geth --rpc --rpcport 27016 > ./logs/boot.txt 2>&1) &
echo "Booting mongo..."
(mongod --dbpath mongo/data --port 27017 > ./logs/boot.txt 2>&1) &
echo "Booting node..."
(node node/app.js > ./logs/boot.txt 2>&1) &
echo "Boot success!\n"


