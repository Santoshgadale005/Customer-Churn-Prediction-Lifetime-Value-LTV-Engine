# Day 2: Database Design & Data Engineering Foundations

## Overview
Today we built the data foundation for the production ML system. We moved from a simple environment setup to a structured PostgreSQL database architecture.

## Accomplishments
- ✅ Created `app/database/db_connection.py`: Centralized database connection management using SQLAlchemy.
- ✅ Created `app/database/setup_db.py`: Automated script to create the `churn_ltv_db` database and the `customers` table.
- ✅ Created `app/services/load_data.py`: ETL-like script to insert sample customer data into the database.
- ✅ Created `app/services/verify_data.py`: Script to query and verify the data in the table.
- ✅ Set up a Virtual Environment (`.venv`) and installed all required dependencies.
- ✅ Created a `.env` file to manage database credentials securely.

## Current Status
The database infrastructure is ready, but a **password authentication error** occurred when trying to connect to the local PostgreSQL server.

### Action Required
Please update the `.env` file in the root directory with your PostgreSQL password:

```env
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=churn_ltv_db
```

## How to Run the Scripts
Once you have updated the `.env` file, run the following commands in your terminal:

### 1. Set Up the Database and Table
```bash
source .venv/bin/activate
python app/database/setup_db.py
```

### 2. Load Sample Data
```bash
python app/services/load_data.py
```

### 3. Verify Data
```bash
python app/services/verify_data.py
```

## Next Steps
In Day 3, we will begin **Exploratory Data Analysis (EDA)** and start building the data preprocessing pipeline for the ML models.
