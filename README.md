# Database Chat Agent

This Streamlit web application allows users to interact with a SQLite database (upload limit 200 mb) using natural language queries. 

https://databasechatapp-aypn4gqbzxuoh8bw8pcbxr.streamlit.app/

### Sidebar Input

1. Provide your OpenAI API Key.
2. Drag and drop or browse your SQLite database (db) file.
3. Disconnect upload or clear chat if desired.

### Main Chat Interface
After upload, you are provided with the following function:
1. Database Overiew Tab, including:
   - Tables: Displays column information for a selected table.
   - Relationships: Displays foreign key relationships between tables.
   - ERD: Displays the Entity-Relationship Diagram 
Besides, the main chat interface is displayed only if a database file has been uploaded

Additionally providing the API Key lets you interact with the database main chat interface:

2. Chat Interface:
   - When a user submits a question, the agent processes the query and generates a response.
   - The response is displayed and added to the chat history.
   - Besides the final answer, the response displayed also includes the thought and search process of the agent, to make the user aware of the agent's logic. This provides the possibility, to check the answer's validity as well as adjust the syntax of the questions asks for better targeting.

**Notes on Questions**
- The more open the questions to the agent, the higher the variation of the response.
- Questions about specific data are best expressed by being as precise as possible, e.g. "Provide the sum of Column_A in Table_C" or "Count the number of tables in the database."
- In rare cases no answer or an error is being given. In that case, you can just ask the question again to receive an answer. 

### Deployment

The application can be run locally via terminal command "streamlit run database_chat_app.py" from the project folder. Besides it has been deployed on streamlit hub under following link: https://databasechatapp-aypn4gqbzxuoh8bw8pcbxr.streamlit.app/.

Necessary libraries:
- Streamlit (st): For building the web interface.
- Pandas (pd): For handling data in tabular format.
- SQLAlchemy (sql): For interacting with the database.
- LangChain: For creating an AI-powered SQL agent that can process natural language queries.
- Graphviz: For generating Entity-Relationship Diagrams (ERDs).
- Tempfile and OS: For handling temporary files and cleanup.

### Agent System Prompt

Following system prompt has been injected:

"""
You are an intelligent assistant designed to help users interact with a SQLite database. Your primary role is to assist with querying, analyzing, and managing data stored in the database. 
You can perform tasks such as:
- Writing and executing SQL queries (e.g., SELECT, INSERT, UPDATE, DELETE).
- Retrieving and summarizing data from tables.
- Providing insights or analysis based on the data.
- Assisting with database schema design or modifications.
- Troubleshooting SQL errors or optimizing queries.

Always ensure the following:
- Confirm the structure of the database (e.g., table names, columns, and relationships) before executing queries.
- Handle sensitive data with care and avoid exposing it unless explicitly requested.
- Explain your steps and provide clear, concise responses.
- If a query is complex, break it down and explain each part.
- If unsure about a request, ask clarifying questions.
"""

### Ending Notes
- You can find some example dataset files to play around with in the github folder example_database.
- Neither the API Key nor the dataset file is being copied or stored!
- The python code has been assembled with heavy usage of claude 3.5 Sonnet as well as Cursor EDI.
