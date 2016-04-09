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

def main():
	c = Crawler.Crawler()
	c.getBlock(10000)

if __name__ == "__main__":
	main()


