# MongoDB Chart Generator

A Streamlit application that connects to MongoDB, processes natural language queries using Google's Gemini API, and generates appropriate visualizations.

## Features

- **MongoDB Connection**: Securely connect to MongoDB clusters
- **Schema Detection**: Automatically detect collection schemas
- **Natural Language Processing**: Use Google's Gemini LLM to parse user queries into MongoDB operations
- **Dynamic Visualization**: Generate appropriate charts based on query results
- **Query History**: Keep track of previous queries and visualizations

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

IF NO DATABASE, IF THERE THEN JUST ADD CREDS IN THE STREAMLIT APPLICATION

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


## Installation

1. Clone this repository:
```bash
git clone https://github.com/prajwal678/MongoChart
cd MongoChart
```

2. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate # for linux, please follow accordingly for windows n mac
pip install -r requirements.txt
```

3. Create a `.env` file with the following variables:
```bash
cp .env.example .env
```
and then modify accordingly

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