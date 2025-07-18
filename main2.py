import requests
import json
from fastapi import FastAPI
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
import uvicorn
import threading
import time

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# FastAPI app setup
app = FastAPI()
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if "_id" in doc:
        doc["_id"] = {"$oid": str(doc["_id"])}
    return doc

@app.get("/get-all")
def get_all():
    docs = list(collection.find())
    serialized_docs = [serialize_doc(doc) for doc in docs]
    return serialized_docs

def start_server():
    """Start FastAPI server in a separate thread"""
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")

def hit_endpoint_and_print():
    """Hit the FastAPI endpoint and print individual values"""
    try:
        # Make request to the endpoint
        response = requests.get("http://127.0.0.1:8000/get-all")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully hit the endpoint!")
            print(f"📊 Found {len(data)} documents")
            print("=" * 50)
            
            # Print each document's values individually
            for i, doc in enumerate(data, 1):
                print(f"📄 Document {i}:")
                print(f"   🆔 Full ID: {doc['_id']}")
                print(f"   🔑 ObjectId: {doc['_id']['$oid']}")
                print(f"   📱 Mobile: {doc['user_mobile_number']}")
                print(f"   🏢 Organization: {doc['organization_name']}")
                print(f"   🆔 Org ID: {doc['organization_id']}")
                print(f"   📋 Type: {doc['organization_type']}")
                print("-" * 30)
                
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to FastAPI server")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def main():
    """Main function to run the FastAPI server and hit the endpoint"""
    print("🚀 Starting FastAPI server...")
    
    # Start FastAPI server in a separate thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)
    
    # Hit the endpoint and print values
    hit_endpoint_and_print()
    
    print("\n🛑 Press Ctrl+C to stop the server")
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()