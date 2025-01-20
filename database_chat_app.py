import streamlit as st
import pandas as pd
import sqlalchemy as sql
from sqlalchemy import inspect
import tempfile
import os
from langchain.agents import create_sql_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain.callbacks import StreamlitCallbackHandler
import graphviz
import requests
import io

# Page config
st.set_page_config(page_title="Database Chat Interface", layout="wide")

# Title
st.title("💬 Database Chat Interface")

def load_example_database():
    """Fetch and load the example database from GitHub"""
    try:
        # URL of the raw database file
        url = "https://github.com/SrnrZ/database_chat_app/raw/main/example_database/sqlite-sakila.db"
        
        # Fetch the file
        response = requests.get(url)
        if response.status_code == 200:
            # Create a file-like object from the response content
            db_file = io.BytesIO(response.content)
            return copy_db_to_temp(db_file)
        else:
            st.error("Failed to fetch example database")
            return None
    except Exception as e:
        st.error(f"Error loading example database: {str(e)}")
        return None

def copy_db_to_temp(uploaded_db):
    """Create a temporary copy of the uploaded database file"""
    try:
        # Create a temporary file for the SQLite database
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        db_path = temp_db.name
        temp_db.close()
        
        # Copy the uploaded file to the temporary location
        with open(db_path, 'wb') as f:
            f.write(uploaded_db.getvalue() if isinstance(uploaded_db, st.runtime.uploaded_file_manager.UploadedFile) else uploaded_db.getbuffer())
        
        return db_path
    except Exception as e:
        st.error(f"Error copying database: {str(e)}")
        return None

def get_database_overview(engine):
    """Get overview of all tables in the database"""
    try:
        inspector = inspect(engine)
        
        # Get all table names
        tables = inspector.get_table_names()
        
        # Create a dictionary to store table info
        db_structure = {}
        
        for table in tables:
            columns = inspector.get_columns(table)
            primary_keys = inspector.get_pk_constraint(table)['constrained_columns']
            foreign_keys = inspector.get_foreign_keys(table)
            
            # Get column information
            column_info = []
            for col in columns:
                column_info.append({
                    'name': col['name'],
                    'type': str(col['type']),
                    'nullable': '✓' if col['nullable'] else '✗',
                    'primary_key': '✓' if col['name'] in primary_keys else '✗'
                })
            
            # Get foreign key information
            fk_info = []
            for fk in foreign_keys:
                fk_info.append({
                    'from': fk['constrained_columns'],
                    'to': f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                })
            
            db_structure[table] = {
                'columns': column_info,
                'foreign_keys': fk_info
            }
            
        return db_structure
    except Exception as e:
        st.error(f"Error getting database overview: {str(e)}")
        return None

def generate_erd(db_structure):
    """Generate an ERD graph using graphviz"""
    try:
        dot = graphviz.Digraph(comment='ERD', format='png')
        
        # Add nodes (tables)
        for table_name, table_info in db_structure.items():
            columns = table_info['columns']
            columns_str = "\n".join([f"{col['name']} ({col['type']})" for col in columns])
            dot.node(table_name, f"{table_name}\n{columns_str}")
        
        # Add edges (relationships)
        for table_name, table_info in db_structure.items():
            for fk in table_info['foreign_keys']:
                source_table = table_name
                target_table = fk['to'].split('.')[0]
                dot.edge(source_table, target_table, label=fk['to'])
        
        return dot
    except Exception as e:
        st.error(f"Error generating ERD: {str(e)}")
        return None

# Sidebar for API key and file upload
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    
    # File upload
    uploaded_file = st.file_uploader("Upload Database File", type=['db'])
    
    st.write("---")
    # Example database link and load button
    
    if st.button("Load example database (sakila.db)"):
        db_path = load_example_database()
        if db_path:
            st.success("Example database 'sqlite-sakila.db' loaded successfully!")
            st.session_state['db_path'] = db_path
        else:
            st.error("Failed to load example database")
    
    if uploaded_file is not None:
        db_path = copy_db_to_temp(uploaded_file)
        if db_path:
            st.success("Database loaded successfully!")
            # Store the database path in session state
            st.session_state['db_path'] = db_path
        else:
            st.error("Failed to load database file")

    st.markdown("<a href='https://github.com/SrnrZ/database_chat_app/tree/main/example_database' style='text-decoration: none'>📚Example database source</a>", unsafe_allow_html=True)

# Only show the main interface if a database has been uploaded
if 'db_path' in st.session_state:
    # Database Overview Section
    with st.expander("**Database Overview**", expanded=False):
        engine = sql.create_engine(f"sqlite:///{st.session_state['db_path']}")
        db_structure = get_database_overview(engine)

        if db_structure:
            # Create tabs for different views
            tab_tables, tab_relationships, tab_erd = st.tabs(["Tables", "Relationships", "ERD"])
            
            with tab_tables:
                # Create a selectbox for table selection
                table_names = list(db_structure.keys())
                selected_table = st.selectbox("Select a table to view", table_names)
                
                if selected_table:
                    table_info = db_structure[selected_table]
                    columns_df = pd.DataFrame([
                        {
                            'Column': col['name'],
                            'Type': col['type'],
                            'Nullable': col['nullable'],
                            'Primary Key': col['primary_key']
                        }
                        for col in table_info['columns']
                    ])
                    st.dataframe(columns_df, use_container_width=True)
            
            with tab_relationships:
                # Relationships view
                relationships = []
                for table_name, table_info in db_structure.items():
                    for fk in table_info['foreign_keys']:
                        relationships.append({
                            'Source Table': table_name,
                            'Source Column': ', '.join(fk['from']),
                            'References': fk['to']
                        })
                
                if relationships:
                    relationships_df = pd.DataFrame(relationships)
                    st.dataframe(relationships_df, use_container_width=True)
                else:
                    st.write("No relationships found in the database.")
            
            with tab_erd:
                # ERD visualization
                erd_graph = generate_erd(db_structure)
                if erd_graph:
                    st.graphviz_chart(erd_graph)
                else:
                    st.write("Unable to generate ERD.")

    st.write("Ask questions about your database in natural language!")

    # Initialize session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    def initialize_agent(callbacks):
        """Initialize the database agent with OpenAI and SQLite connection"""
        try:
            # Set up database connection
            db = SQLDatabase.from_uri(f"sqlite:///{st.session_state['db_path']}")
            
            # Set up OpenAI
            llm = ChatOpenAI(
                temperature=0,
                model_name="gpt-3.5-turbo",
                api_key=api_key,
                callbacks=callbacks
            )
            
            # Create toolkit
            toolkit = SQLDatabaseToolkit(db=db, llm=llm)
            
            # Create agent
            agent = create_sql_agent(
                llm=llm,
                toolkit=toolkit,
                agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
                verbose=True,
                callbacks=callbacks
            )
            return agent
        except Exception as e:
            st.error(f"Error initializing agent: {str(e)}")
            return None

    # Chat interface
    st.write("### Chat")
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about the database..."):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
        else:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.write(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Initialize callbacks
                    callbacks = [StreamlitCallbackHandler(st.container())]
                    
                    # Initialize agent
                    agent = initialize_agent(callbacks)
                    if agent:
                        try:
                            # Add system prompt as the first message
                            system_prompt = """
                            You are an intelligent assistant designed to help users interact with a SQLite database. Your primary role is to assist with querying, analyzing, and managing data stored in the database. You can perform tasks such as:

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
                            # Prepend the system prompt to the chat history
                            messages = [{"role": "system", "content": system_prompt}]
                            messages.extend(st.session_state.chat_history)
                            
                            # Invoke the agent with the updated messages
                            response = agent.invoke({"input": prompt, "messages": messages})
                            st.write(response["output"])
                            
                            # Add AI response to chat history
                            st.session_state.chat_history.append(
                                {"role": "assistant", "content": response["output"]}
                            )
                        except Exception as e:
                            st.error(f"Error getting response: {str(e)}")

    # Clear chat button
    if st.sidebar.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    # Clean up temporary database file when session ends
    def cleanup():
        if 'db_path' in st.session_state:
            try:
                os.remove(st.session_state['db_path'])
            except:
                pass

    # Register cleanup function
    import atexit
    atexit.register(cleanup)

else:
    st.write("Please upload a SQLite database file (.db) to begin.")

# Example questions
with st.sidebar:
    st.write("---")
    st.write("Example tasks you can ask for:")
    examples = [
        "Count the number of tables in the database.",
        "How many records are in [table_name]?",
        "Show the first 5 rows of [table_name].",
        "What are the relationships between [table_a] and [table_b].",
        "What columns are in the [table_name] table?",
        "What do you think is the most interesting insight from this database?"
    ]
    for example in examples:
        st.info(example)
