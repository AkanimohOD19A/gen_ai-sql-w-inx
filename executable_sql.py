import streamlit as st
import pandas as pd
import sqlite3
import io
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import tempfile
import os

st.set_page_config(page_title="SQL Query Interface", layout="wide")

st.title("🗃️ SQL Query Interface")
st.markdown("Execute SQL queries against various database types")

## Session state
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

if 'sample_data_created' not in st.session_state:
    st.session_state.sample_data_created = False

if 'current_query' not in st.session_state:
    st.session_state.current_query = ""

# Sidebar for database configuration
st.sidebar.header("Database Configuration")

db_type = st.sidebar.selectbox(
    "Database Type",
    ["SQLite (Sample Data)", "SQLite (File Upload)", "PostgreSQL", "MySQL", "SQL Server"]
)

##-----------------------
# .DB Connection setup
##-----------------------
engine = None
connection_string = ""

if db_type == "SQLite (Sample Data)":
    # Create a temporary file-based SQLite database for better persistence
    if 'sample_db_path' not in st.session_state:
        # Create a temporary database file
        temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        st.session_state.sample_db_path = temp_db.name
        temp_db.close()

        # Create engine and sample data
        engine = create_engine(f"sqlite:///{st.session_state.sample_db_path}")

        with engine.connect() as conn:
            try:
                # Create sample tables
                conn.execute(text("""
                    CREATE TABLE employees (
                        id INTEGER PRIMARY KEY, -- AUTOINCREMENT,
                        name TEXT NOT NULL,
                        department TEXT,
                        salary REAL NOT NULL,
                        hire_date DATE NOT NULL
                    )
                """))

                conn.execute(text("""
                    CREATE TABLE departments (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        budget REAL
                    )
                """))

                # Insert into sample data
                conn.execute(text("""
                    INSERT INTO departments (name, budget) VALUES
                        ('Engineering', 500000),
                        ('Marketing', 200000),
                        ('Sales', 300000),
                        ('HR', 150000)
                """))

                conn.execute(text("""
                    INSERT INTO employees (name, department, salary, hire_date) VALUES 
                        ('Allen Kupoluyi', 'Engineering', 75000, '2023-01-15'),
                        ('Demilade Smith', 'Marketing', 65000, '2023-02-20'),
                        ('Akan Daniel', 'Sales', 55000, '2023-03-10'),
                        ('Chikezie Brown', 'Engineering', 80000, '2023-01-25'),
                        ('Charlie Bilal', 'HR', 50000, '2023-04-05')
                """))

                conn.commit()
                st.session_state.sample_engine = engine

            except Exception as e:
                st.sidebar.error(f"Error creating sample .db: {str(e)}")

    # Use existing sample .db
    engine = create_engine(f"sqlite:///{st.session_state.sample_db_path}")
    connection_string = f"sqlite:///{st.session_state.sample_db_path}"

    # Verify tables exist
    try:
        with engine.connect() as conn:
            tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
            existing_tables = [row[0] for row in tables_result.fetchall()]

        st.sidebar.success("✅ Connected to sample SQLite database")
        if existing_tables:
            st.sidebar.info(f"Available tables: {', '.join(existing_tables)}")
        else:
            st.sidebar.warning("⚠️ No tables found")

    except Exception as e:
        st.sidebar.error(f"❌ Error: {str(e)}")
        # Reset if there's an issue
        if 'sample_db_path' in st.session_state:
            del st.session_state.sample_db_path
        st.rerun()

elif db_type == "SQLite (File Upload)":
    uploaded_file = st.sidebar.file_uploader("Upload SQLite file", type=['db', 'sqlite', 'sqlite3'])

    if uploaded_file:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as tmp_file:
            tmp_file.write(uploaded_file.read())
            temp_pth = tmp_file.name

        try:
            engine = create_engine(f"sqlite:///{temp_pth}")
            connection_string = f"sqlite:///{temp_pth}"

            # Test connection and show available tables
            with engine.connect() as conn:
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                tables = [row[0] for row in tables_result.fetchall()]

            st.sidebar.success("✅ Connected to SQLite file")
            if tables:
                st.sidebar.info(f"Available tables: {', '.join(tables)}")
            else:
                st.sidebar.warning("No tables found in database")

        except Exception as e:
            st.sidebar.error(f"❌ Connection failed: {str(e)}")
    else:
        st.sidebar.info("👆 Upload a SQLite file to get started")

else:
    # Other .db types
    st.sidebar.subheader("Connection Details")
    host = st.sidebar.text_input("Host", "localhost")
    port = st.sidebar.number_input("Port", value=5432 if db_type == "PostgreSQL" else 3306)
    database = st.sidebar.text_input("Database Name")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Connect"):
        try:
            if db_type == "PostgreSQL":
                connection_string = f"postgresql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "MySQL":
                connection_string = f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
            elif db_type == "SQL Server":
                connection_string = f"mssql+pyodbc://{username}:{password}@{host}:{port}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

            engine = create_engine(connection_string)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            st.sidebar.success("✅ Connected successfully")
        except Exception as e:
            st.sidebar.error(f"❌ Connection failed: {str(e)}")

# Main interface
col1, col2 = st.columns([2, 1])

with col1:
    st.header("SQL Query Editor")

    # Query input
    query = st.text_area(
        "Enter your SQL query:",
        value=st.session_state.current_query,
        height=200,
        placeholder="SELECT * FROM employees WHERE salary > 60000;",
        help="Write your SQL query here. Use Ctrl+Enter to execute.",
        key="query_input"
    )

    # Query execution buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

    with col_btn1:
        execute_btn = st.button("▶️ Execute", type="primary")

    with col_btn2:
        clear_btn = st.button("🗑️ Clear")

    if clear_btn:
        st.session_state.current_query = ""
        st.rerun()

with col2:
    st.header("Quick Actions")

    if db_type == "SQLite (Sample Data)":
        st.subheader("Sample Queries")

        sample_queries = {
            "Show all employees": "SELECT * FROM employees;",
            "High salary employees": "SELECT * FROM employees WHERE salary > 65000;",
            "Count by department": "SELECT department, COUNT(*) as count FROM employees GROUP BY department;",
            "Join employees & departments": """SELECT e.name, e.salary, d.budget 
            FROM employees e 
            JOIN departments d ON e.department = d.name;""",
            "Show table structure": "PRAGMA table_info(employees);"
        }

        for label, sample_query in sample_queries.items():
            if st.button(label, key = f"sample_{label}"):
                st.session_state.current_query = sample_query
                st.rerun()

    elif db_type == "SQLite (File Upload)" and engine:
        st.subheader("Database Info")
        try:
            with engine.connect() as conn:
                # Get table names
                tables_result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
                tables = [row[0] for row in tables_result.fetchall()]

                if tables:
                    st.write("**Available Tables:**")
                    for table in tables:
                        # Get row count for each table
                        try:
                            count_result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                            count = count_result.fetchone()[0]
                            st.write(f"• `{table}` ({count} rows)")

                            # Add button to show table structure
                            if st.button(f"Show {table} structure", key=f"struct_{table}"):
                                st.session_state.current_query = f"PRAGMA table_info({table});"
                                st.rerun()

                            # Add button to show sample data
                            if st.button(f"Sample from {table}", key=f"sample_{table}"):
                                st.session_state.current_query = f"SELECT * FROM {table} LIMIT 10;"
                                st.rerun()
                        except:
                            st.write(f"• `{table}`")
                else:
                    st.write("No tables found")
        except Exception as e:
            st.error(f"Error reading database info: {str(e)}")

    elif engine and db_type in ["PostgreSQL", "MySQL", "SQL Server"]:
        st.subheader("Common Queries")

        common_queries = {
            "Show all tables": {
                "PostgreSQL": "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';",
                "MySQL": "SHOW TABLES;",
                "SQL Server": "SELECT name FROM sys.tables;"
            },
            "Show databases": {
                "PostgreSQL": "SELECT datname FROM pg_database;",
                "MySQL": "SHOW DATABASES;",
                "SQL Server": "SELECT name FROM sys.databases;"
            }
        }

        for label, queries in common_queries.items():
            if st.button(label, key=f"common_{label}"):
                st.session_state.current_query = queries.get(db_type, "-- Query not available for this database type")
                st.rerun()

    # Query history
    if st.session_state.query_history:
        st.subheader("Query History")
        for i, hist_query in enumerate(reversed(st.session_state.query_history[-5:])):
            if st.button(f"📝 Query {len(st.session_state.query_history)-i}", key=f"hist_{i}"):
                st.session_state.current_query = hist_query
                st.rerun()

# Clear current_query after using it
# if st.session_state.current_query and st.session_state.current_query == query:
#     st.session_state.current_query = ""

# Execute query
if execute_btn and query and engine:
    try:
        with st.spinner("Executing query..."):
            with engine.connect() as conn:
                # Execute query
                result = conn.execute(text(query))

                # Add to history
                if query not in st.session_state.query_history:
                    st.session_state.query_history.append(query)

                # Handle different types of queries
                if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'PRAGMA')):
                    # Query returns data
                    df = pd.DataFrame(result.fetchall(), columns=result.keys())#["name", "salary", "budget"])

                    if not df.empty:
                        st.success(f"✅ Query executed successfully! ({len(df)} rows returned)")

                        # Display results
                        st.subheader("Query Results")
                        st.dataframe(df, use_container_width=True)

                        # Download option
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv"
                        )
                    else:
                        st.info("Query executed successfully but returned no results.")

                else:
                    # i.e Query modifies data (e.g INSERT, UPDATE, DELETE, CREATE, etc..)
                    conn.commit()
                    st.success("✅ Query executed successfully!")

                    # display change
                    if hasattr(result, 'rowcount') and result.rowcount >= 0:
                        st.info(f"Affected rows: {result.rowcount}")

    except SQLAlchemyError as e:
        st.error(f"❌ SQL Error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

elif execute_btn and not engine:
    st.warning("⚠️ Please configure database connection first")

elif execute_btn and not query:
    st.warning("⚠️ Please enter a SQL query")

# Information section
with st.sidebar.expander("ℹ️ How to use this interface"):
    st.markdown("""
    ### Getting Started
    1. **Choose Database Type**: Select from the sidebar
    2. **Configure Connection**: Provide connection details or use sample data
    3. **Write Query**: Enter your SQL query in the editor
    4. **Execute**: Click the Execute button or use sample queries

    ### Features
    - 🔍 **Multiple Database Support**: SQLite, PostgreSQL, MySQL, SQL Server
    - 📊 **Results Display**: View results in a formatted table
    - 📥 **Export**: Download results as CSV
    - 📝 **Query History**: Access previously executed queries
    - 🎯 **Sample Queries**: Quick examples for testing

    ### Tips
    - Use the sample SQLite database to test queries
    - Check query syntax for your specific database type
    - Large result sets are automatically paginated
    - Query history is maintained during your session
    """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit • Execute SQL queries safely and efficiently*")