from app.database import test_connection, example_query

def main():
    print("Testing database connection...")
    if test_connection():
        print("Database connection successful!")
        try:
            result = example_query()
            print(f"Test query result: {result}")
        except Exception as e:
            print(f"Query test failed: {e}")
    else:
        print("Database connection failed!")

if __name__ == "__main__":
    main()