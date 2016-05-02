# 	A client to crawl the ethereum blockchain
#
# 	Requires three processes to be running:
#
#	1: geth 	(to access the blockchain data)
#	2: mongodb	(to store processed blockchain data)
#	3: node		(to interact with geth via web3.js and RPC)
#
#	Boot these processes by calling
#		./boot_crawler.sh
#
#
#
from Crawler import Crawler
import subprocess
import time

def main():
	# Spin up necessary processes
	subprocess.call(["scripts/boot_crawler.sh"])

	time.sleep(1)
	
	# Initialize the crawler and sync up the blockchain
	c = Crawler.Crawler()

	# Kill processes
	subprocess.call(["scripts/kill_crawler.sh"])

if __name__ == "__main__":
	main()
