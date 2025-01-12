# database_chat_app

This Streamlit web application allows users to interact with a SQLite database (upload limit 200 mb) using natural language queries. 

https://databasechatapp-aypn4gqbzxuoh8bw8pcbxr.streamlit.app/

### Sidebar Input

1. Provide your OpenAI API Key
2. Drag and drop or browse your SQLite database (db) file
3. Disconnect upload or clear chat if desired

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
   - **Besides the final answer, the response displayed also includes the thought and search process of the agent, to make the user aware of the agent's logic. This provides the possibility, to check the answer's validity as well as adjust the syntax of the questions asks for better targeting.**




Below is a step-by-step explanation of what the code does:
