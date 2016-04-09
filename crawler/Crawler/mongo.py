# Interact with mongo

def initMongo(client):
	db = client["blockchain"]					# Connect to the "blockchain" database (or create if not exists)
	try:
		db.create_collection("transactions")	# Create the collection if not exists
	except:
		pass

	try:
		db["transactions"].createIndex( { number: 1 }, { unique: true } )
	except:
		pass


	return
