from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

app = FastAPI()
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to simple string
    return doc

@app.get("/get-all")
def get_all():
    docs = list(collection.find())
    serialized_docs = [serialize_doc(doc) for doc in docs]
    return serialized_docs