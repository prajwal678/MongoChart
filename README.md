# MongoDB Chart Generator

A Streamlit application that connects to MongoDB, processes natural language queries using Google's Gemini API, and generates appropriate visualizations.

## Features

- **MongoDB Connection**: Securely connect to MongoDB clusters
- **Schema Detection**: Automatically detect collection schemas
- **Natural Language Processing**: Use Google's Gemini LLM to parse user queries into MongoDB operations
- **Dynamic Visualization**: Generate appropriate charts based on query results
- **Query History**: Keep track of previous queries and visualizations

## Example Scenario

For a movies database:

1. User connects to MongoDB cluster containing film data
2. User types: "Show number of movies released per year"
3. System:
   - Parses query to identify intent (count) and grouping (by year)
   - Converts to MongoDB aggregation: `db.movies.aggregate([{$group: {_id: "$year", count: {$sum: 1}}}, {$sort: {_id: 1}}])`
   - Determines bar chart is appropriate for this data
   - Renders visualization with years on x-axis and counts on y-axis

## MongoDB Setup

### Local MongoDB Setup

1. Install MongoDB on your system if not already installed:
   - **Arch Linux**: `sudo pacman -S mongodb-bin`
   - **Ubuntu/Debian**: `sudo apt install mongodb`
   - **macOS**: `brew install mongodb-community`

2. Start MongoDB service:
   - **Linux (systemd)**: 
     ```bash
     sudo systemctl start mongodb
     sudo systemctl enable mongodb
     ```
   - **macOS**: 
     ```bash
     brew services start mongodb-community
     ```

3. Create a new database and add sample data:
   ```bash
   mongosh
   use mydb
   db.movies.insertMany([
     {title: "Inception", year: 2010, director: "Christopher Nolan", genre: "Sci-Fi"},
     {title: "The Dark Knight", year: 2008, director: "Christopher Nolan", genre: "Action"},
     {title: "Pulp Fiction", year: 1994, director: "Quentin Tarantino", genre: "Crime"}
   ])
   ```

4. (Optional) Create a user with authentication:
   ```bash
   use mydb
   db.createUser({
     user: "myuser",
     pwd: "mypassword",
     roles: [{ role: "readWrite", db: "mydb" }]
   })
   ```

5. Your MongoDB connection string will be:
   - Without authentication: `mongodb://localhost:27017/mydb`
   - With authentication: `mongodb://myuser:mypassword@localhost:27017/mydb`

### MongoDB Atlas (Cloud) Setup

1. Create a free MongoDB Atlas account at [https://www.mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (the free tier is sufficient)
3. Set up a database user with password authentication
4. Add your IP address to the network access list
5. Load sample data (optional) or create your own collections
6. Get your connection string from the Atlas dashboard: 
   - Click "Connect" > "Connect your application"
   - The format will be: `mongodb+srv://username:password@cluster.mongodb.net/mydb`

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/mongodb-chart-generator.git
cd mongodb-chart-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```
MONGO_URI=mongodb://user:password@hostname:port/dbname
MONGO_DB_NAME=your_database_name
GOOGLE_API_KEY=your_google_api_key
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Connect to your MongoDB database:
   - Enter your MongoDB URI and database name in the sidebar
   - If you're using the `.env` file, these fields will be pre-filled

3. Select a collection to analyze:
   - After connecting, available collections will appear in a dropdown
   - Select a collection to automatically detect its schema

4. Enter a natural language query:
   - Type a question about your data (e.g., "Show me number of movies by director")
   - Click "Generate Chart" to process the query

5. View and interact with the generated visualization

## Project Structure

- `app.py`: Main Streamlit application
- `utils/`: MongoDB connection and schema detection utilities
- `models/`: Query parsing and aggregation pipeline generation
- `visualizations/`: Chart generation and selection utilities

## Dependencies

- Streamlit
- PyMongo
- LangChain
- Google Generative AI
- Plotly
- Pandas

## License

MIT License