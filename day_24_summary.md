# Day 24: Prometheus, Grafana & Production Monitoring

## Overview
Today, the project evolved from a deployed ML platform into an observable production system. The goal was to make the FastAPI service, prediction traffic, latency, errors, and Docker containers measurable through Prometheus and visible through Grafana dashboards.

## Accomplishments
- ✅ **Prometheus Client Added:** Added `prometheus-client` to `requirements.txt`.
- ✅ **Metrics Module Completed:** Created `app/utils/metrics.py` with API request, API error, prediction, churn, non-churn, churn-rate, and latency metrics.
- ✅ **Prediction Counter Wired:** Updated prediction flows to increment prediction metrics whenever churn predictions are generated.
- ✅ **Latency Middleware Added:** Added FastAPI middleware to observe request duration for every endpoint.
- ✅ **Prometheus Endpoint Created:** Updated `/metrics` to expose Prometheus text metrics and moved the simple JSON view to `/metrics/summary`.
- ✅ **Prometheus Config Added:** Created `prometheus.yml` to scrape FastAPI and cAdvisor.
- ✅ **Alert Rules Added:** Created `monitoring/alerts.yml` with high-latency, high-error-rate, and API-down alerts.
- ✅ **Grafana Added:** Added Grafana to Docker Compose on `http://localhost:3001`.
- ✅ **Grafana Provisioning Added:** Added an automatic Prometheus datasource and a starter `Customer Intelligence Monitoring` dashboard.
- ✅ **Container Monitoring Added:** Added cAdvisor on `http://localhost:8081` for Docker container metrics.
- ✅ **README Updated:** Documented monitoring URLs, metrics, Prometheus queries, Grafana login, and alert foundations.

## Final Validation
- FastAPI metrics endpoint: `http://localhost:8000/metrics`
- JSON monitoring summary: `http://localhost:8000/metrics/summary`
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3001`
- cAdvisor: `http://localhost:8081`

## Outcome
The project now has production observability foundations. Engineers can monitor API traffic, prediction volume, latency, errors, churn prediction trends, and Docker container health before users report problems.
