import pyodbc
from typing import List
import os
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()

# Pool configuration
POOL_SIZE = 5  # Number of connections to maintain
CONNECTION_POOL: List[pyodbc.Connection] = []  # Store our connections

def create_connection():
    """Creates a single database connection"""
    return pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=DESKTOP-KLL45AE\\SQLEXPRESS;'
        'DATABASE=master;'
        'Trusted_Connection=yes;'
    )

def initialize_pool():
    """Creates the initial pool of connections"""
    for _ in range(POOL_SIZE):
        try:
            conn = create_connection()
            CONNECTION_POOL.append(conn)
        except Exception as e:
            print(f"Error creating connection: {e}")
    print(f"Pool initialized with {len(CONNECTION_POOL)} connections")

@contextmanager
def get_db_connection():
    """
    Gets a connection from the pool and returns it when done
    Usage: 
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Users")
    """
    connection = None
    
    # Try to get a connection from the pool
    if CONNECTION_POOL:
        connection = CONNECTION_POOL.pop()
    else:
        # If pool is empty, create new connection
        connection = create_connection()
    
    try:
        # Give the connection to the user
        yield connection
    finally:
        try:
            # Return connection to pool if it's good
            if connection and not connection.closed:
                CONNECTION_POOL.append(connection)
            else:
                # If connection is bad, create new one for pool
                new_conn = create_connection()
                CONNECTION_POOL.append(new_conn)
        except Exception as e:
            print(f"Error returning connection to pool: {e}")

# Function to test if connection is working
def test_connection():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

# Initialize the pool when module is imported
initialize_pool()

# Example usage function
def example_query():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT TOP 1 * FROM Users")
        result = cursor.fetchone()
        return result