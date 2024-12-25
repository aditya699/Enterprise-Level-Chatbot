import pyodbc
from typing import List
import os
from dotenv import load_dotenv
from contextlib import contextmanager
import time
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
    global CONNECTION_POOL
    CONNECTION_POOL = []  # Reset the pool
    
    retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(retries):
        try:
            for _ in range(POOL_SIZE):
                conn = create_connection()
                CONNECTION_POOL.append(conn)
            print(f"Pool initialized with {len(CONNECTION_POOL)} connections")
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
    
    print("Failed to initialize connection pool after all attempts")
    return False

@contextmanager
def get_db_connection():
    """
    Gets a connection from the pool and returns it when done
    """
    connection = None
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Try to get a connection from the pool
            if CONNECTION_POOL:
                connection = CONNECTION_POOL.pop()
                
                # Test if connection is still alive
                cursor = connection.cursor()
                cursor.execute("SELECT 1")
                cursor.fetchone()
                
                break  # Connection is good
            else:
                # If pool is empty, try to create new connection
                connection = create_connection()
                break
                
        except Exception as e:
            print(f"Connection attempt {retry_count + 1} failed: {e}")
            retry_count += 1
            
            if connection:
                try:
                    connection.close()
                except:
                    pass
                    
            if retry_count < max_retries:
                time.sleep(1)  # Wait before retrying
            
    if not connection:
        raise Exception("Could not establish database connection after multiple attempts")
    
    try:
        yield connection
    finally:
        try:
            # Test connection before returning to pool
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            CONNECTION_POOL.append(connection)
        except:
            # If connection is bad, create new one for pool
            try:
                connection.close()
            except:
                pass
            try:
                new_conn = create_connection()
                CONNECTION_POOL.append(new_conn)
            except Exception as e:
                print(f"Error creating replacement connection: {e}")


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