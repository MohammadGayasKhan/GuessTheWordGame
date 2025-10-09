from django.db import models
import pymongo
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

try:
    mongo_uri = os.getenv('MONGO_URI')
    
    if not mongo_uri:
        print("ERROR: MONGO_URI not found in environment variables!")
    
    database_name = 'user_db'
    
    client = pymongo.MongoClient(mongo_uri)
    client.server_info()
    db = client[database_name]
    
    print("Successfully connected to MongoDB Atlas!")
    
except pymongo.errors.ServerSelectionTimeoutError:
    print("Error: Could not connect to MongoDB Atlas. Check your connection string and network.")
except pymongo.errors.ConfigurationError as e:
    print(f"Error: MongoDB configuration error: {e}")
except Exception as e:
    print(f"Error connecting to MongoDB Atlas: {e}")