# Deployment Guide

## Run Locally

pip install -r requirements.txt

uvicorn app.main:app --reload

---

## Run Using Docker

docker build -t ltv-project .

docker run -p 8000:8000 ltv-project