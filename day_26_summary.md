# Day 26: Kubernetes Fundamentals & Container Orchestration

## Overview
Today, the Customer Churn Prediction & LTV Engine evolved from a Dockerized ML application running via Docker Compose into a cloud-native, scalable, and self-healing platform deployed to a local Kubernetes cluster.

## Accomplishments
- ✅ **Kubernetes Local Setup Verified:** Utilized the built-in Kubernetes cluster in Docker Desktop (context `docker-desktop`).
- ✅ **ConfigMaps and Secrets Defined:** Created `k8s/configmap.yaml` and `k8s/secrets.yaml` to securely separate environment settings and PostgreSQL credentials from container code.
- ✅ **Persistent Volumes Configured:** Added Persistent Volume Claims (PVC) for both PostgreSQL (`postgres-pvc`) and Redis (`redis-pvc`) to ensure database and cache persistence across pod lifecycle transitions.
- ✅ **Self-Contained Database & Cache Deployments:** Added Deployments and ClusterIP Services for PostgreSQL (`postgres-service`) and Redis (`redis-service`).
- ✅ **Multi-Replica FastAPI Deployment:** Configured the FastAPI API with a 2-replica setup using `churn-api:latest`.
- ✅ **NodePort Service Integration:** Created `k8s/fastapi-service.yaml` exposing the API externally on port `30080`.
- ✅ **Database Initialization Completed:** Rollout restart triggered tables creation successfully on startup when connected to Postgres.
- ✅ **End-to-End predictions with Cache hits verified:**
  - First prediction: connected to database and model (cache hit: `false`).
  - Repeat prediction: returned instantly from Redis cache (cache hit: `true`).
- ✅ **Self-Healing Tested:** Deleted an API pod and observed Kubernetes scheduling and launching a replacement in under 5 seconds.
- ✅ **Horizontal Scaling Validated:** Scaled the API deployment up to 4 replicas and back down to 2 replicas smoothly.
- ✅ **Rolling Updates Validated:** Tagged local image to `churn-api:v2` and performed a zero-downtime rolling update.
- ✅ **Documentation and Visual Mockups Added:** Created CLI terminal screenshots for deployment and scaling, copied them to the repo, and updated `README.md` with instructions and resume points.

## Outcomes
The prediction engine is now containerized and orchestrated via Kubernetes. It features high availability, self-healing capabilities, painless horizontal scaling to handle sudden traffic spikes, and safe rolling updates to roll out new models with zero downtime in enterprise environments.
