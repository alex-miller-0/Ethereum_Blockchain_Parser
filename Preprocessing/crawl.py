# 	A client to crawl the ethereum blockchain
#
# 	Requires two processes to be running:
#
#	1: geth 	(with RPC enabled, to access the blockchain data)
#	2: mongodb	(to store processed blockchain data)
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
	#subprocess.call(["scripts/boot_crawler.sh"])
	time.sleep(1)
	print("Booting processes.")

	# Initialize the crawler and sync up the blockchain
	c = Crawler.Crawler()

	# Kill processes
	subprocess.call(["scripts/kill_crawler.sh"])

if __name__ == "__main__":
	main()
