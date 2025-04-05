import os
from typing import Dict, List, Optional, Any
import json
import streamlit as st
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

class MongoQueryIntent(BaseModel):
    """Schema for parsed MongoDB query intents"""
    collection: str = Field(description="The collection to query")
    operation_type: str = Field(description="The type of operation (aggregate, find, etc.)")
    aggregation_pipeline: List[Dict[str, Any]] = Field(description="MongoDB aggregation pipeline")
    chart_type: str = Field(description="The type of chart to use (bar, line, pie, scatter, etc.)")
    x_axis: str = Field(description="Field to use for x-axis")
    y_axis: str = Field(description="Field or operation to use for y-axis")
    title: str = Field(description="Chart title")

class QueryParser:
    def __init__(self):
        """Initialize the query parser with LLM"""
        self.api_key = os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            st.error("Google API key not found. Please set it in the .env file.")
            return
            
        try:
            self.llm = ChatGoogleGenerativeAI(
                api_key=self.api_key,
                model="gemini-2.0-flash",
                temperature=0
            )
            self.output_parser = PydanticOutputParser(pydantic_object=MongoQueryIntent)
        except Exception as e:
            st.error(f"Failed to initialize LLM: {str(e)}")
    
    def create_prompt(self, query: str, collection_name: str, schema: Dict[str, str]) -> str:
        """Create a prompt for the LLM"""
        format_instructions = self.output_parser.get_format_instructions()
        
        template = """
        You are an expert in MongoDB and data visualization. You need to translate a natural language query about a MongoDB collection into a proper MongoDB aggregation pipeline and determine the appropriate visualization.

        Collection name: {collection_name}
        Collection schema: {schema}
        
        User query: {query}
        
        First, analyze the intent of the query to determine what data to retrieve and how to visualize it.
        Then, construct the appropriate MongoDB aggregation pipeline to fulfill this intent.
        Finally, determine the best chart type to visualize the result.
        
        {format_instructions}
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["query", "collection_name", "schema"],
            partial_variables={"format_instructions": format_instructions}
        )
        
        return prompt.format(
            query=query,
            collection_name=collection_name,
            schema=json.dumps(schema)
        )
    
    def parse_query(self, query: str, collection_name: str, schema: Dict[str, str]) -> Optional[MongoQueryIntent]:
        """Parse a natural language query into a MongoDB query"""
        if not self.api_key:
            st.error("Google API key not found. Please set it in the .env file.")
            return None
            
        try:
            prompt = self.create_prompt(query, collection_name, schema)
            
            # Call the LLM
            response = self.llm.invoke(prompt)
            
            # Parse the response
            parsed_result = self.output_parser.parse(response.content)
            return parsed_result
            
        except Exception as e:
            st.error(f"Failed to parse query: {str(e)}")
            return None

# Create singleton instance
query_parser = QueryParser() 