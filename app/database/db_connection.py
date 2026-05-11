from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")  # Default to postgres, user should update .env
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "churn_ltv_db")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Engine for the specific database
engine = create_engine(DATABASE_URL)

def get_engine():
    return engine

if __name__ == "__main__":
    try:
        connection = engine.connect()
        print("Database connection initialized successfully")
        connection.close()
    except Exception as e:
        print(f"Error connecting to the database: {e}")
