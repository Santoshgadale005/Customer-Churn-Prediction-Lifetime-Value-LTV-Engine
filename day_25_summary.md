# Day 25: Redis Caching & Performance Optimization

## Overview
Today, the Customer Churn Prediction & LTV Engine evolved into a faster and more scalable platform. Redis now caches repeated prediction results, PostgreSQL indexes improve dashboard queries, and Prometheus/Grafana track whether caching is effective.

## Accomplishments
- ✅ **Redis Installed:** Added Redis 7 Alpine to Docker Compose on port `6379`.
- ✅ **Redis Client Integrated:** Added the Python `redis` package and a reusable connection module at `app/utils/cache.py`.
- ✅ **Prediction Caching Added:** Predictions now check Redis before running the ML models.
- ✅ **Deterministic Cache Keys Added:** Customer inputs are sorted, serialized, hashed with SHA-256, and namespaced by model cache version.
- ✅ **Cache Expiration Configured:** Added a default TTL of 3,600 seconds.
- ✅ **Graceful Fallback Added:** Redis failures do not prevent predictions; the API falls back to normal model inference.
- ✅ **Cache Invalidation Added:** Added admin endpoints for cache status and prediction-cache invalidation.
- ✅ **Database Indexes Added:** Added indexes for churn probability, customer segment, creation time, and user ID.
- ✅ **Existing Database Migration Added:** Startup logic creates missing indexes with `CREATE INDEX IF NOT EXISTS`.
- ✅ **Dashboard Queries Optimized:** Replaced `SELECT *` with explicit columns and result limits.
- ✅ **Docker Resources Limited:** Added practical memory limits for API, PostgreSQL, Redis, Airflow, Grafana, Prometheus, Metabase, and cAdvisor.
- ✅ **Redis Monitoring Added:** Added Redis Exporter, Prometheus scraping, Grafana cache panels, and Redis/cache alerts.
- ✅ **Cache Tests Added:** Added deterministic key, cache round-trip, and selective invalidation tests.
- ✅ **Performance Benchmark Added:** Added `scripts/benchmark_cache.py` and documented measured results.

## Performance Results

| Measurement | Result |
|---|---:|
| Cold model prediction | 70.82 ms |
| Warm Redis-cached prediction | 2.82 ms |
| Latency reduction | 96.01% |

## Final Validation
- Redis container: healthy
- Redis command check: `PONG`
- Redis Exporter: HTTP `200`
- Prometheus Redis target: `up=1`
- PostgreSQL dashboard indexes: 4 verified
- Test suite: 13 tests passed

## Outcome
Repeated predictions now avoid unnecessary model inference and database writes. The platform can share cached results across multiple FastAPI instances, measure cache hit rate, and automatically expire or invalidate stale results when models change.
