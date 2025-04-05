import os
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Import our modules
from utils.mongo_connection import mongo_connection
from utils.schema_detection import detect_collection_schema
from models.query_parser import query_parser
from models.aggregation_builder import AggregationBuilder
from visualizations.chart_generator import ChartGenerator

# Load environment variables
load_dotenv()

# Page config
st.set_page_config(
    page_title="MongoDB Visualizer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Session state initialization
if "connected" not in st.session_state:
    st.session_state.connected = False
if "collection" not in st.session_state:
    st.session_state.collection = None
if "schema" not in st.session_state:
    st.session_state.schema = {}
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "last_query" not in st.session_state:
    st.session_state.last_query = None
if "last_pipeline" not in st.session_state:
    st.session_state.last_pipeline = None

# Title and Description
st.title("📊 MongoDB Chart Generator")
st.markdown("""
This application allows you to connect to a MongoDB database and generate charts from your data using natural language queries.
Simply connect to your database, select a collection, and describe the chart you want to see!
""")

# Sidebar - Connection Settings
with st.sidebar:
    st.header("MongoDB Connection")
    
    # Connection form
    with st.form("connection_form"):
        mongo_uri = st.text_input("MongoDB URI", value=os.getenv("MONGO_URI", ""), type="password")
        db_name = st.text_input("Database Name", value=os.getenv("MONGO_DB_NAME", ""))
        connect_button = st.form_submit_button("Connect")
    
    # Connect to MongoDB when button is clicked
    if connect_button:
        if mongo_uri and db_name:
            with st.spinner("Connecting to MongoDB..."):
                if mongo_connection.connect(mongo_uri, db_name):
                    st.session_state.connected = True
                    st.success(f"Connected to {db_name} database!")
                else:
                    st.session_state.connected = False
                    st.error("Failed to connect to MongoDB. Please check your credentials.")
        else:
            st.error("MongoDB URI and Database name are required.")
    
    # Collection selection if connected
    if st.session_state.connected:
        st.subheader("Collections")
        collections = mongo_connection.get_collections()
        
        if collections:
            selected_collection = st.selectbox("Select a collection", collections)
            
            if selected_collection != st.session_state.collection:
                st.session_state.collection = selected_collection
                with st.spinner("Analyzing collection schema..."):
                    st.session_state.schema = detect_collection_schema(selected_collection)
                    if st.session_state.schema:
                        st.success(f"Schema detected for {selected_collection}!")
                    else:
                        st.warning(f"No schema could be detected for {selected_collection}.")
        else:
            st.warning("No collections found in the database.")
    
    # Show collection schema if available
    if st.session_state.connected and st.session_state.schema:
        with st.expander("Collection Schema"):
            st.json(st.session_state.schema)
    
    # Google API Key
    st.subheader("LLM Settings")
    google_key = st.text_input("Google API Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
    if google_key:
        os.environ["GOOGLE_API_KEY"] = google_key
        st.success("Google API Key set!")
    else:
        st.warning("Google API Key is required for natural language queries.")

# Main content
if st.session_state.connected and st.session_state.collection:
    # Query input
    st.subheader("Ask a Question About Your Data")
    query = st.text_area("Enter your query (e.g., 'Show number of documents by category')", height=100, 
                          help="Describe what data you want to see and how you want it visualized.")
    
    # Process query button
    if st.button("Generate Chart"):
        if not query:
            st.error("Please enter a query.")
        elif not st.session_state.schema:
            st.error("Schema information is not available. Please select a valid collection.")
        elif not os.getenv("GOOGLE_API_KEY") and not google_key:
            st.error("Google API Key is required for natural language queries.")
        else:
            with st.spinner("Processing your query..."):
                # Parse the query
                intent = query_parser.parse_query(
                    query, 
                    st.session_state.collection, 
                    st.session_state.schema
                )
                
                if intent:
                    # Create a safe aggregation pipeline
                    pipeline = AggregationBuilder.create_safe_aggregation_from_intent(intent)
                    
                    # Execute the query
                    results = mongo_connection.execute_query(st.session_state.collection, pipeline)
                    
                    # Save to session state
                    st.session_state.last_query = query
                    st.session_state.last_pipeline = pipeline
                    
                    # Add to query history
                    st.session_state.query_history.append({
                        "query": query,
                        "pipeline": pipeline,
                        "intent": intent.dict() if intent else None
                    })
                    
                    # Display results
                    st.subheader("Generated Chart")
                    
                    # Show the MongoDB query
                    with st.expander("MongoDB Aggregation Pipeline"):
                        st.code(json.dumps(pipeline, indent=2), language="json")
                    
                    # Generate visualization
                    fig = ChartGenerator.generate_chart(results, intent)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show data table
                        with st.expander("Raw Data"):
                            df = pd.DataFrame(results)
                            st.dataframe(df)
                    else:
                        st.error("Failed to generate chart from the results.")
                else:
                    st.error("Failed to interpret your query. Please try rewording it.")
    
    # Query history
    if st.session_state.query_history:
        st.subheader("Query History")
        for i, history_item in enumerate(reversed(st.session_state.query_history)):
            with st.expander(f"Query {len(st.session_state.query_history) - i}: {history_item['query'][:50]}..."):
                st.code(json.dumps(history_item['pipeline'], indent=2), language="json")

else:
    # Not connected or no collection selected
    st.info("Connect to a MongoDB database and select a collection to start visualizing your data.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, MongoDB, and Google's Gemini API") 