# helper/gen_sql_chunk.py
import pandas as pd
import sqlite3
import json
import tempfile
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import io

def csv_to_sqlite_sample_data(csv_file_path, table_name="data", sample_size=1000):
    """
    Convert CSV file to SQLite sample data code for Streamlit app

    Args:
        csv_file_path (str): Path to CSV file
        table_name (str): Name for the table in SQLite
        sample_size (int): Number of rows to include in sample (for large files)

    Returns:
        str: Python code to create the sample data
    """

    # Read CSV file
    print(f"Reading CSV file: {csv_file_path}")
    df = pd.read_csv(csv_file_path)
    print(f"Original data shape: {df.shape}")

    # Take a sample if data is large
    if len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size} rows from {len(df)} total rows")
    else:
        df_sample = df
        print(f"Using all {len(df)} rows")

    # Clean column names (remove spaces, special characters)
    df_sample.columns = [col.replace(' ', '_').replace('-', '_').replace('.', '_')
                         for col in df_sample.columns]

    # Generate CREATE TABLE statement
    create_table_sql = generate_create_table_sql(df_sample, table_name)

    # Generate INSERT statements
    insert_sql = generate_insert_sql(df_sample, table_name)

    # Generate the complete Python code for Streamlit
    python_code = f'''
    # Sample data creation code for your Streamlit app
    # Replace the existing sample data section with this code
    
    # Create sample table
    conn.execute(text("""
    {create_table_sql}
    """))
    
    # Insert sample data
    {insert_sql}
    
    conn.commit()
    '''

    return python_code


def json_to_sqlite_sample_data(json_file_path, table_name="data", sample_size=1000):
    """
    Convert JSON file to SQLite sample data code for Streamlit app
    """

    # Read JSON file
    print(f"Reading JSON file: {json_file_path}")
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    # Convert to DataFrame
    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, dict):
        # If it's a dict, try to find the main data array
        if len(data) == 1:
            key = list(data.keys())[0]
            df = pd.DataFrame(data[key])
        else:
            df = pd.DataFrame([data])
    else:
        raise ValueError("Unsupported JSON structure")

    print(f"Original data shape: {df.shape}")

    # Take a sample if data is large
    if len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size} rows from {len(df)} total rows")
    else:
        df_sample = df
        print(f"Using all {len(df)} rows")

    # Clean column names
    df_sample.columns = [col.replace(' ', '_').replace('-', '_').replace('.', '_')
                         for col in df_sample.columns]

    # Generate CREATE TABLE statement
    create_table_sql = generate_create_table_sql(df_sample, table_name)

    # Generate INSERT statements
    insert_sql = generate_insert_sql(df_sample, table_name)

    # Generate the complete Python code for Streamlit
    python_code = f'''
    # Sample data creation code for your Streamlit app
    # Replace the existing sample data section with this code
    
    # Create sample table
    conn.execute(text("""
    {create_table_sql}
    """))
    
    # Insert sample data
    {insert_sql}
    
    conn.commit()
    '''

    return python_code


def generate_create_table_sql(df, table_name):
    """Generate CREATE TABLE SQL statement from DataFrame"""

    columns = []
    for col in df.columns:
        # Determine SQLite data type based on pandas dtype
        dtype = df[col].dtype

        if pd.api.types.is_integer_dtype(dtype):
            sql_type = "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            sql_type = "REAL"
        elif pd.api.types.is_bool_dtype(dtype):
            sql_type = "INTEGER"  # SQLite stores booleans as integers
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            sql_type = "DATE"
        else:
            sql_type = "TEXT"

        columns.append(f"    {col} {sql_type}")

    create_sql = f"CREATE TABLE {table_name} (\n" + ",\n".join(columns) + "\n)"
    return create_sql


def generate_insert_sql(df, table_name):
    """Generate INSERT SQL statements from DataFrame"""

    # Convert DataFrame to list of tuples for SQL insertion
    records = []
    for _, row in df.iterrows():
        record_values = []
        for value in row:
            if pd.isna(value):
                record_values.append("NULL")
            elif isinstance(value, str):
                # Escape single quotes in strings
                escaped_value = value.replace("'", "''")
                record_values.append(f"'{escaped_value}'")
            elif isinstance(value, (int, float)):
                record_values.append(str(value))
            elif isinstance(value, bool):
                record_values.append("1" if value else "0")
            else:
                # Convert other types to string
                escaped_value = str(value).replace("'", "''")
                record_values.append(f"'{escaped_value}'")

        records.append(f"({', '.join(record_values)})")

    # Split into chunks to avoid very long SQL statements
    chunk_size = 100
    insert_statements = []

    columns = ', '.join(df.columns)

    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        values_str = ',\n    '.join(chunk)

        insert_sql = f'''conn.execute(text("""
            INSERT INTO {table_name} ({columns}) VALUES 
            {values_str}
        """))'''

        insert_statements.append(insert_sql)

    return '\n\n'.join(insert_statements)


def create_sqlite_file_directly(file_path, output_db_path, table_name="data", sample_size=1000):
    """
    Create a SQLite database file directly from CSV/JSON
    This creates a file you can upload to the "SQLite (File Upload)" option
    """

    # Read the file
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    elif file_path.endswith('.json'):
        with open(file_path, 'r') as f:
            data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame([data])
    else:
        raise ValueError("Unsupported file format. Use .csv or .json")

    print(f"Original data shape: {df.shape}")

    # Sample data if too large
    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size} rows")

    # Clean column names
    df.columns = [col.replace(' ', '_').replace('-', '_').replace('.', '_')
                  for col in df.columns]

    # Create SQLite database
    engine = create_engine(f'sqlite:///{output_db_path}')
    df.to_sql(table_name, engine, if_exists='replace', index=False)

    print(f"SQLite database created: {output_db_path}")
    print(f"Table name: {table_name}")
    print(f"Records: {len(df)}")

    return output_db_path


def create_sqlite_from_uploaded_file(uploaded_file, table_name="data", sample_size=None):
    """
    Convert Streamlit uploaded CSV/JSON file to SQLite database

    Args:
        uploaded_file: Streamlit UploadedFile object
        table_name (str): Name for the table in SQLite
        sample_size (int): Number of rows to sample (None for all rows)

    Returns:
        str: Path to the created SQLite database file
    """

    # Create temporary SQLite database file
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db_pth = temp_db.name
    temp_db.close()

    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)

        # Read the uploaded file based on its type
        if uploaded_file.name.endswith('.csv'):
            # Read CSV from uploaded file using StringIO
            content = uploaded_file.read()

            # Handle both bytes and string content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Create StringIO object for pandas
            csv_buffer = io.StringIO(content)
            df = pd.read_csv(csv_buffer)

        elif uploaded_file.name.endswith('.json'):
            # Read JSON from uploaded file
            content = uploaded_file.read()

            # Handle both bytes and string content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Parse JSON
            json_data = json.loads(content)

            # Convert JSON to DataFrame
            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                # If it's a dict, try to find the main data array
                if len(json_data) == 1:
                    key = list(json_data.keys())[0]
                    if isinstance(json_data[key], list):
                        df = pd.DataFrame(json_data[key])
                    else:
                        df = pd.DataFrame([json_data[key]])
                else:
                    df = pd.DataFrame([json_data])
            else:
                raise ValueError("Unsupported JSON structure")

        else:
            raise ValueError(f"Unsupported file type: {uploaded_file.name}")

        print(f"Original data shape: {df.shape}")

        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("The uploaded file contains no data")

        # Sample data if requested
        if sample_size and len(df) > sample_size:
            df = df.sample(n=sample_size, random_state=42)
            print(f"Sampled {sample_size} rows from {len(df)} total rows")

        # Clean column names (remove spaces, special characters)
        df.columns = [
            str(col).replace(' ', '_')
            .replace('-', '_')
            .replace('.', '_')
            .replace('(', '_')
            .replace(')', '_')
            .replace('/', '_')
            .replace('\\', '_')
            .replace('[', '_')
            .replace(']', '_')
            .replace('{', '_')
            .replace('}', '_')
            .replace(':', '_')
            .replace(';', '_')
            .replace(',', '_')
            .replace('?', '_')
            .replace('!', '_')
            .replace('@', '_')
            .replace('#', '_')
            .replace('$', '_')
            .replace('%', '_')
            .replace('^', '_')
            .replace('&', '_')
            .replace('*', '_')
            .replace('+', '_')
            .replace('=', '_')
            .replace('|', '_')
            for col in df.columns
        ]

        # Clean up column names (remove consecutive underscores and trailing underscores)
        df.columns = [
            '_'.join([part for part in col.split('_') if part])  # Remove empty parts
            for col in df.columns
        ]

        # Handle empty column names
        df.columns = [f"column_{i}" if col == "" else col for i, col in enumerate(df.columns)]

        # Remove any duplicate column names
        seen_columns = set()
        new_columns = []
        for col in df.columns:
            if col in seen_columns:
                counter = 1
                new_col = f"{col}_{counter}"
                while new_col in seen_columns:
                    counter += 1
                    new_col = f"{col}_{counter}"
                new_columns.append(new_col)
                seen_columns.add(new_col)
            else:
                new_columns.append(col)
                seen_columns.add(col)

        df.columns = new_columns

        # Create SQLite database and insert data
        engine = create_engine(f'sqlite:///{temp_db_pth}')
        df.to_sql(table_name, engine, if_exists='replace', index=False)

        print(f"SQLite database created: {temp_db_pth}")
        print(f"Table name: {table_name}")
        print(f"Records: {len(df)}")

        return temp_db_pth

    except Exception as e:
        # Clean up temp file if there's an error
        import os
        if os.path.exists(temp_db_pth):
            os.unlink(temp_db_pth)
        raise e


def get_file_info(uploaded_file):
    """
    Get basic information about an uploaded file
    """
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)

        if uploaded_file.name.endswith('.csv'):
            # Read CSV content
            content = uploaded_file.read()

            # Handle both bytes and string content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Reset file pointer for other operations
            uploaded_file.seek(0)

            # Create StringIO object for pandas
            csv_buffer = io.StringIO(content)
            df = pd.read_csv(csv_buffer)

            return {
                'type': 'CSV',
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'size_mb': uploaded_file.size / (1024 * 1024)
            }

        elif uploaded_file.name.endswith('.json'):
            # Read JSON content
            content = uploaded_file.read()

            # Handle both bytes and string content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Reset file pointer for other operations
            uploaded_file.seek(0)

            # Parse JSON
            json_data = json.loads(content)

            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                if len(json_data) == 1:
                    key = list(json_data.keys())[0]
                    if isinstance(json_data[key], list):
                        df = pd.DataFrame(json_data[key])
                    else:
                        df = pd.DataFrame([json_data[key]])
                else:
                    df = pd.DataFrame([json_data])

            return {
                'type': 'JSON',
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'size_mb': uploaded_file.size / (1024 * 1024)
            }

    except Exception as e:
        return {
            'type': 'Unknown',
            'error': str(e),
            'size_mb': uploaded_file.size / (1024 * 1024) if hasattr(uploaded_file, 'size') else 0
        }


def preview_uploaded_file(uploaded_file, num_rows=5):
    """
    Preview the first few rows of an uploaded file
    """
    try:
        # Reset file pointer to beginning
        uploaded_file.seek(0)

        if uploaded_file.name.endswith('.csv'):
            # Read CSV content
            content = uploaded_file.read()

            # Handle both bytes and string content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Reset file pointer for other operations
            uploaded_file.seek(0)

            # Create StringIO object for pandas
            csv_buffer = io.StringIO(content)
            df = pd.read_csv(csv_buffer)

            return df.head(num_rows)

        elif uploaded_file.name.endswith('.json'):
            # Read JSON content
            content = uploaded_file.read()

            # Handle both bytes and string content
            if isinstance(content, bytes):
                content = content.decode('utf-8')

            # Reset file pointer for other operations
            uploaded_file.seek(0)

            # Parse JSON
            json_data = json.loads(content)

            if isinstance(json_data, list):
                df = pd.DataFrame(json_data)
            elif isinstance(json_data, dict):
                if len(json_data) == 1:
                    key = list(json_data.keys())[0]
                    if isinstance(json_data[key], list):
                        df = pd.DataFrame(json_data[key])
                    else:
                        df = pd.DataFrame([json_data[key]])
                else:
                    df = pd.DataFrame([json_data])

            return df.head(num_rows)

    except Exception as e:
        return f"Error previewing file: {str(e)}"

# Example usage:
# if __name__ == "__main__":
#     # Method 1: Generate code to replace in your Streamlit app
#     print("=== Method 1: Generate Streamlit Code ===")
#
#     # For CSV file:
#     csv_code = csv_to_sqlite_sample_data(
#         csv_file_path="../data/faker.csv",  # Replace with your CSV file path
#         table_name="my_data",
#         sample_size=1000  # Adjust sample size as needed
#     )
#
#     print("Generated Python code for CSV:")
#     print(csv_code)
#
#     # Save the code to a file
#     with open("sqlite_sample_code.py", "w") as f:
#         f.write(csv_code)
#
#     print("\n" + "=" * 50 + "\n")
#
#     # Method 2: Create SQLite file directly
#     print("=== Method 2: Create SQLite File ===")
#
#     # Create SQLite file that you can upload
#     sqlite_file = create_sqlite_file_directly(
#         file_path="../data/faker.csv",  # Replace with your file path
#         output_db_path="my_data.db",
#         table_name="my_data",
#         sample_size=10000  # Can be larger since it's a file upload
#     )
#
#     print(f"SQLite file created: {sqlite_file}")
#     print("You can now upload this .db file using the 'SQLite (File Upload)' option")

# csv_code = csv_to_sqlite_sample_data(
#     csv_file_path="../data/faker.csv",
#     table_name="your_data",
#     sample_size=5000  # Reasonable sample size
# )