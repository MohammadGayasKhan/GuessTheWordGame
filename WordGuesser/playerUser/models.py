from django.db import models
import pymongo


# Create your models here.
try: 
    client = pymongo.MongoClient("mongodb://localhost:27017/") 
    client.server_info()   
    db = client["user_db"]
    
except pymongo.errors.ServerSelectionTimeoutError:
    print("Error: Could not connect to MongoDB. Make sure MongoDB server is running.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")