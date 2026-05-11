from sqlalchemy import text
from app.database.db_connection import get_engine

def verify_data():
    engine = get_engine()
    
    query = "SELECT * FROM customers;"
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text(query))
            rows = result.fetchall()
            
            print(f"Total records in 'customers' table: {len(rows)}")
            for row in rows:
                print(row)
    except Exception as e:
        print(f"Error querying data: {e}")

if __name__ == "__main__":
    verify_data()
