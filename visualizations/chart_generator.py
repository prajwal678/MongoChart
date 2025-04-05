from typing import Dict, List, Optional, Any
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from models.query_parser import MongoQueryIntent

class ChartGenerator:
    """Generate visualizations based on MongoDB query results and intent"""
    
    @staticmethod
    def convert_to_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert MongoDB results to a pandas DataFrame"""
        if not data:
            return pd.DataFrame()
            
        # Handle _id field from aggregation results
        for item in data:
            if '_id' in item and isinstance(item['_id'], (dict, list)):
                # Flatten the _id field if it's a complex object
                for key, value in item['_id'].items() if isinstance(item['_id'], dict) else enumerate(item['_id']):
                    item[f"_id_{key}"] = value
                del item['_id']
            
        return pd.DataFrame(data)
    
    @staticmethod
    def generate_chart(data: List[Dict[str, Any]], intent: MongoQueryIntent) -> Optional[go.Figure]:
        """Generate a chart based on the data and intent"""
        if not data:
            st.warning("No data available to visualize.")
            return None
            
        # Convert to DataFrame
        df = ChartGenerator.convert_to_dataframe(data)
        
        # Determine x and y axis fields
        x_field = intent.x_axis
        y_field = intent.y_axis
        
        # Handle _id renaming from aggregation
        if x_field == '_id' and '_id' not in df.columns:
            # Look for _id_0, _id_field, etc.
            id_columns = [col for col in df.columns if col.startswith('_id_')]
            if id_columns:
                x_field = id_columns[0]
        
        # If no y_field is specified but there's a 'count', use that
        if (not y_field or y_field not in df.columns) and 'count' in df.columns:
            y_field = 'count'
        
        # Ensure we have the necessary fields
        if x_field not in df.columns:
            st.error(f"X-axis field '{x_field}' not found in the results.")
            return None
            
        if y_field and y_field not in df.columns:
            st.error(f"Y-axis field '{y_field}' not found in the results.")
            return None
        
        # Generate the appropriate chart
        fig = None
        title = intent.title or f"{y_field or 'Value'} by {x_field}"
        
        try:
            if intent.chart_type == 'bar':
                fig = px.bar(df, x=x_field, y=y_field, title=title)
            elif intent.chart_type == 'line':
                fig = px.line(df, x=x_field, y=y_field, title=title)
            elif intent.chart_type == 'scatter':
                fig = px.scatter(df, x=x_field, y=y_field, title=title)
            elif intent.chart_type == 'pie':
                fig = px.pie(df, names=x_field, values=y_field, title=title)
            elif intent.chart_type == 'histogram':
                fig = px.histogram(df, x=x_field, title=title)
            else:
                # Default to bar chart
                fig = px.bar(df, x=x_field, y=y_field, title=title)
                
            # Customize layout
            fig.update_layout(
                xaxis_title=x_field,
                yaxis_title=y_field or "Count",
                template="plotly_white"
            )
                
        except Exception as e:
            st.error(f"Failed to generate chart: {str(e)}")
            return None
            
        return fig 