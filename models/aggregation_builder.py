from typing import Dict, List, Optional, Any
import streamlit as st
from .query_parser import MongoQueryIntent

class AggregationBuilder:
    """Helper class to build and validate MongoDB aggregation pipelines"""
    
    @staticmethod
    def validate_aggregation(pipeline: List[Dict[str, Any]]) -> bool:
        """Validate a MongoDB aggregation pipeline"""
        if not pipeline:
            return False
            
        # Basic validation - ensure each stage is a dictionary
        if not all(isinstance(stage, dict) for stage in pipeline):
            return False
            
        # Ensure each stage has at least one valid operator
        valid_operators = {
            '$match', '$group', '$sort', '$project', '$limit', 
            '$skip', '$unwind', '$lookup', '$count', '$sum'
        }
        
        for stage in pipeline:
            # At least one key must be a valid MongoDB operator
            if not any(op in valid_operators for op in stage.keys()):
                return False
                
        return True
    
    @staticmethod
    def create_safe_aggregation_from_intent(intent: MongoQueryIntent) -> List[Dict[str, Any]]:
        """Create a safe version of the aggregation pipeline from intent"""
        pipeline = intent.aggregation_pipeline
        
        # Validate the pipeline
        if not AggregationBuilder.validate_aggregation(pipeline):
            # Create a fallback simple pipeline based on the intent
            return AggregationBuilder.create_fallback_pipeline(intent)
            
        return pipeline
    
    @staticmethod
    def create_fallback_pipeline(intent: MongoQueryIntent) -> List[Dict[str, Any]]:
        """Create a fallback pipeline if the generated one is invalid"""
        # Simple $group by x_axis with count
        if intent.x_axis and intent.chart_type in ['bar', 'line', 'pie']:
            return [
                {"$group": {"_id": f"${intent.x_axis}", "count": {"$sum": 1}}},
                {"$sort": {"_id": 1}}
            ]
        
        # Simple $match all and limit
        return [
            {"$match": {}},
            {"$limit": 100}
        ] 