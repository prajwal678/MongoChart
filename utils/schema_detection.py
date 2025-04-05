from typing import Dict, List, Set, Any
import streamlit as st
from .mongo_connection import mongo_connection

def detect_field_type(values: List[Any]) -> str:
    """Detect the type of field based on its values"""
    # Remove None values
    values = [v for v in values if v is not None]
    if not values:
        return "unknown"
    
    if all(isinstance(v, int) for v in values):
        return "integer"
    elif all(isinstance(v, float) for v in values):
        return "float"
    elif all(isinstance(v, (int, float)) for v in values):
        return "number"
    elif all(isinstance(v, str) for v in values):
        return "string"
    elif all(isinstance(v, bool) for v in values):
        return "boolean"
    elif all(isinstance(v, list) for v in values):
        return "array"
    elif all(isinstance(v, dict) for v in values):
        return "object"
    else:
        return "mixed"

def detect_collection_schema(collection_name: str, sample_size: int = 100) -> Dict[str, str]:
    """Detect schema for a collection based on sampling documents"""
    # Get a sample of documents
    collection = mongo_connection.get_collection(collection_name)
    if collection is None:
        return {}
    
    try:
        sample_docs = list(collection.find().limit(sample_size))
        if not sample_docs:
            return {}
        
        # Collect all fields
        all_fields = set()
        for doc in sample_docs:
            all_fields.update(doc.keys())
        
        # Remove _id field
        if '_id' in all_fields:
            all_fields.remove('_id')
        
        # Determine types for each field
        schema = {}
        for field in all_fields:
            values = [doc.get(field) for doc in sample_docs if field in doc]
            field_type = detect_field_type(values)
            schema[field] = field_type
            
        return schema
    
    except Exception as e:
        st.error(f"Failed to detect schema for {collection_name}: {str(e)}")
        return {}

def get_schema_for_all_collections() -> Dict[str, Dict[str, str]]:
    """Get schema for all collections in the database"""
    collections = mongo_connection.get_collections()
    all_schemas = {}
    
    for collection_name in collections:
        schema = detect_collection_schema(collection_name)
        if schema:
            all_schemas[collection_name] = schema
    
    return all_schemas 