import json
import statistics
import time
import urllib.request

BASE_URL = "http://localhost:8000"
ITERATIONS = 5


def request(path, method="GET", payload=None, token=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request_object = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers=headers,
        method=method,
    )
    start = time.perf_counter()
    with urllib.request.urlopen(request_object, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    return result, (time.perf_counter() - start) * 1000


def main():
    suffix = int(time.time())
    username = f"cache_benchmark_{suffix}"
    password = "password123"

    request(
        "/register",
        "POST",
        {
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )
    login, _ = request(
        "/login",
        "POST",
        {"username": username, "password": password},
    )
    token = login["access_token"]

    prediction_payload = {
        "gender_Male": 1,
        "SeniorCitizen": 0,
        "tenure": suffix % 60 + 1,
        "MonthlyCharges": 90,
        "TotalCharges": 400,
    }

    cold_result, cold_ms = request(
        "/api/v1/predict",
        "POST",
        prediction_payload,
        token,
    )

    warm_times = []
    for _ in range(ITERATIONS):
        warm_result, warm_ms = request(
            "/api/v1/predict",
            "POST",
            prediction_payload,
            token,
        )
        warm_times.append(warm_ms)

    warm_average = statistics.mean(warm_times)
    improvement = ((cold_ms - warm_average) / cold_ms) * 100 if cold_ms else 0

    print(f"Cold prediction: {cold_ms:.2f} ms")
    print(f"Warm average:   {warm_average:.2f} ms")
    print(f"Improvement:    {improvement:.2f}%")
    print(f"Cold cache_hit: {cold_result.get('cache_hit')}")
    print(f"Warm cache_hit: {warm_result.get('cache_hit')}")


if __name__ == "__main__":
    main()
