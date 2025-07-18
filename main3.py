from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, Optional
import os
from bson import ObjectId
import json
from dotenv import load_dotenv
# Load environment variables
load_dotenv()

app = FastAPI(title="Phone Number API", description="API to manage phone numbers and organizations")

# MongoDB connection
MONGODB_URL = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Custom JSON encoder for MongoDB ObjectId
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

def serialize_doc(doc):
    """Convert MongoDB document to JSON serializable format"""
    if doc is None:
        return None
    return json.loads(json.dumps(doc, cls=JSONEncoder))

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    try:
        # Test the connection
        await client.admin.command('ping')
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    client.close()
    print("Disconnected from MongoDB")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Phone Number API is running"}

@app.get("/phones")
async def get_all_phones():
    """
    Get all phone numbers and their associated organization data
    """
    try:
        cursor = collection.find({})
        documents = []
        
        async for doc in cursor:
            # Remove MongoDB's _id field from response
            doc.pop('_id', None)
            documents.append(serialize_doc(doc))
        
        return {
            "status": "success",
            "count": len(documents),
            "data": documents
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/phones/{phone_number}")
async def get_phone_data(phone_number: str):
    """
    Get organization data for a specific phone number
    
    Args:
        phone_number: The phone number to search for (e.g., +18777804236)
    """
    try:
        # Add + prefix if not present
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        # Find document where the phone number is a key
        query = {phone_number: {"$exists": True}}
        document = await collection.find_one(query)
        
        if document is None:
            raise HTTPException(status_code=404, detail=f"Phone number {phone_number} not found")
        
        # Remove MongoDB's _id field from response
        document.pop('_id', None)
        
        # Extract the data for the specific phone number
        phone_data = document.get(phone_number, {})
        
        return {
            "status": "success",
            "phone_number": phone_number,
            "data": phone_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/phones/{phone_number}/full")
async def get_phone_full_document(phone_number: str):
    """
    Get the full document containing the phone number
    
    Args:
        phone_number: The phone number to search for (e.g., +18777804236)
    """
    try:
        # Add + prefix if not present
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number
        
        # Find document where the phone number is a key
        query = {phone_number: {"$exists": True}}
        document = await collection.find_one(query)
        
        if document is None:
            raise HTTPException(status_code=404, detail=f"Phone number {phone_number} not found")
        
        # Remove MongoDB's _id field from response
        document.pop('_id', None)
        
        return {
            "status": "success",
            "phone_number": phone_number,
            "document": serialize_doc(document)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        await client.admin.command('ping')
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)