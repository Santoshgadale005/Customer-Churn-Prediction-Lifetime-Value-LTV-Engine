import hashlib
import json
import os
from typing import Any, Dict, Optional

import redis
from redis.exceptions import RedisError

from app.utils.metrics import (
    cache_errors_total,
    cache_hit_rate,
    cache_hits_total,
    cache_misses_total,
)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
CACHE_VERSION = os.getenv("CACHE_VERSION", "v1")

redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1,
)

_hits = 0
_misses = 0


def build_prediction_cache_key(data: Dict[str, Any]) -> str:
    serialized = json.dumps(data, sort_keys=True, separators=(",", ":"), default=str)
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    return f"prediction:{CACHE_VERSION}:{digest}"


def _update_hit_rate() -> None:
    total = _hits + _misses
    cache_hit_rate.set(_hits / total if total else 0)


def get_cached_prediction(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    global _hits, _misses

    try:
        cached_value = redis_client.get(build_prediction_cache_key(data))
    except RedisError:
        cache_errors_total.inc()
        return None

    if cached_value is None:
        _misses += 1
        cache_misses_total.inc()
        _update_hit_rate()
        return None

    _hits += 1
    cache_hits_total.inc()
    _update_hit_rate()
    try:
        return json.loads(cached_value)
    except json.JSONDecodeError:
        cache_errors_total.inc()
        redis_client.delete(build_prediction_cache_key(data))
        return None


def cache_prediction(data: Dict[str, Any], result: Dict[str, Any]) -> bool:
    try:
        redis_client.set(
            build_prediction_cache_key(data),
            json.dumps(result),
            ex=CACHE_TTL_SECONDS,
        )
        return True
    except RedisError:
        cache_errors_total.inc()
        return False


def clear_prediction_cache() -> int:
    deleted = 0
    try:
        for key in redis_client.scan_iter(match="prediction:*"):
            deleted += redis_client.delete(key)
    except RedisError:
        cache_errors_total.inc()
        return 0
    return deleted


def get_cache_status() -> Dict[str, Any]:
    try:
        redis_client.ping()
        return {
            "status": "healthy",
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "ttl_seconds": CACHE_TTL_SECONDS,
            "cache_version": CACHE_VERSION,
        }
    except RedisError:
        return {
            "status": "unavailable",
            "host": REDIS_HOST,
            "port": REDIS_PORT,
            "ttl_seconds": CACHE_TTL_SECONDS,
            "cache_version": CACHE_VERSION,
        }
