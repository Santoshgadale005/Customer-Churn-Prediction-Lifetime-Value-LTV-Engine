import json

from app.utils import cache


class FakeRedis:
    def __init__(self):
        self.values = {}

    def get(self, key):
        return self.values.get(key)

    def set(self, key, value, ex):
        self.values[key] = value
        return True

    def scan_iter(self, match):
        prefix = match.removesuffix("*")
        return [key for key in self.values if key.startswith(prefix)]

    def delete(self, key):
        return int(self.values.pop(key, None) is not None)

    def ping(self):
        return True


def test_prediction_cache_key_is_stable():
    first = cache.build_prediction_cache_key({"tenure": 5, "MonthlyCharges": 90})
    second = cache.build_prediction_cache_key({"MonthlyCharges": 90, "tenure": 5})

    assert first == second
    assert first.startswith("prediction:v1:")


def test_prediction_cache_round_trip(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(cache, "redis_client", fake_redis)

    customer = {"tenure": 5, "MonthlyCharges": 90}
    result = {"churn_prediction": 1, "predicted_ltv": 1200.0}

    assert cache.get_cached_prediction(customer) is None
    assert cache.cache_prediction(customer, result)
    assert cache.get_cached_prediction(customer) == result


def test_clear_prediction_cache_only_removes_prediction_keys(monkeypatch):
    fake_redis = FakeRedis()
    fake_redis.values = {
        "prediction:v1:one": json.dumps({"value": 1}),
        "prediction:v1:two": json.dumps({"value": 2}),
        "session:user": "keep",
    }
    monkeypatch.setattr(cache, "redis_client", fake_redis)

    assert cache.clear_prediction_cache() == 2
    assert fake_redis.values == {"session:user": "keep"}
