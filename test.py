from pymongo import MongoClient
import urllib

username = "Harit26"
pwd = "Symbrosia"
client = MongoClient(
    "mongodb+srv://" + urllib.parse.quote_plus(username) + ":" + 
    urllib.parse.quote_plus(pwd) + 
    "@cluster0.lymvb.mongodb.net/?retryWrites=true&w=majority"
)

db_name = client["your_actual_db_name"]       # Replace with your real database name
collection = db_name["your_collection_name"]  # Replace with your real collection name

# Sample query: Which strain has the most batch records submitted?
result = collection.aggregate([
    { "$group": { "_id": "$Strain", "total_batches": { "$sum": 1 } } },
    { "$sort": { "total_batches": -1 } },
    { "$limit": 1 },
    { "$project": { "Strain": "$_id", "total_batches": 1, "_id": 0 } }
])

for doc in result:
    print(doc)