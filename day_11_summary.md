# Day 11: Dockerizing the Entire ML Platform

## Overview
Today, we elevated the project from a local machine dependency to a **Containerized Production System** using Docker and Docker Compose. This ensures reproducibility, scalability, and aligns the infrastructure with industry-standard DevOps practices.

## Accomplishments
- ✅ **Dockerfile Created:** Created a robust `Dockerfile` to containerize the FastAPI application.
- ✅ **.dockerignore Added:** Configured `.dockerignore` to prevent unnecessary files (like `.venv`, `__pycache__`) from inflating the container image.
- ✅ **Docker Image Built:** Successfully built the `churn-api` Docker image, encapsulating our code and dependencies.
- ✅ **Docker Compose Implemented:** Orchestrated the entire platform (FastAPI, PostgreSQL, and Metabase) via `docker-compose.yml`.
- ✅ **Container Networking Configured:** Updated the internal `DATABASE_URL` in `app/database/database.py` to route to `postgres:5432`—utilizing Docker's internal DNS instead of `localhost`.
- ✅ **Data Persistence (Volumes):** Configured a Docker volume (`postgres_data`) in `docker-compose.yml` so that database records and predictions survive container restarts.

## Architecture
The platform now operates as a unified, multi-container system:

```text
Docker Compose Network
    ├── api (FastAPI on port 8000)
    ├── postgres (PostgreSQL DB with persistent volume)
    └── metabase (BI Dashboard on port 3000)
```

## Running the Platform
To spin down or start the platform in the future, simply run:
```bash
# Stop the containers
docker compose down

# Start the containers
docker compose up -d
```

## Action Items
1. Because we attached a new, persistent volume to the PostgreSQL database, we need to initialize the tables and re-seed the predictions. You can do this by running the scripts **inside** the running API container:
```bash
docker exec -it churn_api python create_tables.py
docker exec -it churn_api python seed_predictions.py
```
2. Check your API documentation at [http://localhost:8000/docs](http://localhost:8000/docs).
3. Check your Dashboard at [http://localhost:3000](http://localhost:3000). *(Note: Because we destroyed the manual Day 10 container and replaced it with this orchestrated one, you will need to re-do the initial Metabase setup just once!)*

## Next Steps
Now that the API, ML model, database, and dashboards are running in an orchestrated, cloud-ready environment, the foundation for a professional production ML platform is officially complete!
