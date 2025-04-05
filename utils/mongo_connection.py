import os
from typing import Dict, List, Optional, Tuple

import pymongo
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MongoDBConnection:
    def __init__(self):
        self.client = None
        self.db = None
        self.collections = {}
        self.collection_schemas = {}
    
    def connect(self, connection_string: str, db_name: str) -> bool:
        """Connect to MongoDB using the provided connection string and database name"""
        try:
            self.client = MongoClient(connection_string)
            self.db = self.client[db_name]
            # Test connection
            self.client.admin.command('ping')
            return True
        except Exception as e:
            st.error(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def get_collections(self) -> List[str]:
        """Get list of collections in the connected database"""
        if self.db is None:
            return []
        
        try:
            return self.db.list_collection_names()
        except Exception as e:
            st.error(f"Failed to get collections: {str(e)}")
            return []
    
    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a specific collection"""
        if self.db is None:
            return None
        
        if collection_name not in self.collections:
            try:
                self.collections[collection_name] = self.db[collection_name]
            except Exception as e:
                st.error(f"Failed to get collection {collection_name}: {str(e)}")
                return None
                
        return self.collections[collection_name]
    
    def get_collection_sample(self, collection_name: str, limit: int = 5) -> List[Dict]:
        """Get a sample of documents from a collection"""
        collection = self.get_collection(collection_name)
        if collection is None:
            return []
        
        try:
            return list(collection.find().limit(limit))
        except Exception as e:
            st.error(f"Failed to get sample from {collection_name}: {str(e)}")
            return []
    
    def execute_query(self, collection_name: str, query: List[Dict]) -> List[Dict]:
        """Execute a MongoDB aggregation pipeline"""
        collection = self.get_collection(collection_name)
        if collection is None:
            return []
        
        try:
            result = list(collection.aggregate(query))
            return result
        except Exception as e:
            st.error(f"Failed to execute query on {collection_name}: {str(e)}")
            return []
    
    def disconnect(self):
        """Close the MongoDB connection"""
        if self.client is not None:
            self.client.close()
            self.client = None
            self.db = None
            self.collections = {}
            self.collection_schemas = {}

# Create singleton instance
mongo_connection = MongoDBConnection() 