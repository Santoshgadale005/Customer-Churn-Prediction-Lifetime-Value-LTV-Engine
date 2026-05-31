from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "churn_ltv_db")

# URL-encode the password to handle special characters like @
ENCODED_PASSWORD = quote_plus(DB_PASSWORD)

# Connect to the default 'postgres' database to create the new one
DEFAULT_DATABASE_URL = f"postgresql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
engine_default = create_engine(DEFAULT_DATABASE_URL, isolation_level="AUTOCOMMIT")

def create_database():
    with engine_default.connect() as conn:
        try:
            conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"Database '{DB_NAME}' created successfully.")
        except ProgrammingError:
            print(f"Database '{DB_NAME}' already exists.")
        except Exception as e:
            print(f"Error creating database: {e}")

def create_tables():
    # Now connect to the new database to create tables
    APP_DATABASE_URL = f"postgresql://{DB_USER}:{ENCODED_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine_app = create_engine(APP_DATABASE_URL)
    
    create_customers_table = """
    CREATE TABLE IF NOT EXISTS customers (
        customer_id SERIAL PRIMARY KEY,
        gender VARCHAR(20),
        senior_citizen INT,
        partner VARCHAR(10),
        dependents VARCHAR(10),
        tenure INT,
        phone_service VARCHAR(10),
        internet_service VARCHAR(50),
        contract VARCHAR(50),
        monthly_charges FLOAT,
        total_charges FLOAT,
        churn VARCHAR(10)
    );
    """
    
    with engine_app.connect() as conn:
        try:
            conn.execute(text(create_customers_table))
            conn.commit()
            print("Table 'customers' created successfully.")
        except Exception as e:
            print(f"Error creating tables: {e}")

if __name__ == "__main__":
    create_database()
    create_tables()
