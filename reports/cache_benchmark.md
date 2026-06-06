# Redis Cache Performance Benchmark

## Environment

- FastAPI running in Docker
- Redis 7 Alpine running in Docker
- PostgreSQL prediction logging enabled
- Cache TTL: 3,600 seconds
- Benchmark iterations: 1 cold request and 5 warm requests

## Results

| Measurement | Result |
|---|---:|
| Cold prediction latency | 70.82 ms |
| Warm cached latency average | 2.82 ms |
| Latency reduction | 96.01% |
| First response `cache_hit` | `false` |
| Repeated response `cache_hit` | `true` |

## Method

The benchmark registered a temporary user, logged in to receive a JWT, submitted a unique prediction payload, and then repeated the same request five times.

Run again with:

```bash
.venv/bin/python scripts/benchmark_cache.py
```

Results vary by host resources and Docker state, but warm requests should consistently avoid model inference and PostgreSQL writes.
