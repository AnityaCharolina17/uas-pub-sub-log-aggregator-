import pytest
import requests
import time
from datetime import datetime
import random

BASE_URL = "http://localhost:8080"

def wait_for_service():
    """Wait for aggregator to be ready"""
    for _ in range(30):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(1)
    return False

@pytest.fixture(scope="module", autouse=True)
def setup():
    """Setup: wait for service"""
    assert wait_for_service(), "Service not ready"
    yield

def create_test_event(event_id=None):
    """Helper: create test event"""
    if event_id is None:
        event_id = f"test-{int(time.time() * 1000)}-{random.randint(1000, 9999)}"

    return {
        "topic": "test",
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "pytest",
        "payload": {"test": "data"}
    }

# TEST 1: Basic Deduplication
def test_deduplication():
    event = create_test_event()

    r1 = requests.post(f"{BASE_URL}/publish", json=event)
    assert r1.status_code == 200
    data1 = r1.json()
    assert data1["is_duplicate"] is False
    assert data1["status"] == "processed"

    r2 = requests.post(f"{BASE_URL}/publish", json=event)
    assert r2.status_code == 200
    data2 = r2.json()
    assert data2["is_duplicate"] is True
    assert data2["status"] == "duplicate"

# TEST 2: Stats Consistency
def test_stats_consistency():
    stats_before = requests.get(f"{BASE_URL}/stats").json()

    for _ in range(5):
        event = create_test_event()
        requests.post(f"{BASE_URL}/publish", json=event)

    stats_after = requests.get(f"{BASE_URL}/stats").json()

    assert stats_after["unique_processed"] == stats_before["unique_processed"] + 5
    assert stats_after["received"] >= stats_before["received"] + 5

# TEST 3: Get Events by Topic
def test_get_events_by_topic():
    topic = f"test-topic-{int(time.time())}"

    for _ in range(3):
        event = create_test_event()
        event["topic"] = topic
        requests.post(f"{BASE_URL}/publish", json=event)

    response = requests.get(f"{BASE_URL}/events", params={"topic": topic})
    assert response.status_code == 200

    data = response.json()
    assert data["count"] >= 3
    assert data["topic"] == topic

# TEST 4: Concurrent Requests
def test_concurrent_deduplication():
    import concurrent.futures

    event = create_test_event()

    def send_event():
        return requests.post(f"{BASE_URL}/publish", json=event)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(send_event) for _ in range(10)]
        results = [f.result().json() for f in futures]

    non_duplicates = sum(1 for r in results if not r["is_duplicate"])
    assert non_duplicates == 1

# TEST 5: Invalid Event Schema
def test_invalid_event_schema():
    invalid_event = {
        "topic": "",
        "event_id": "test",
        "timestamp": "invalid-timestamp",
        "source": "test",
        "payload": {}
    }

    response = requests.post(f"{BASE_URL}/publish", json=invalid_event)
    assert response.status_code == 422

# TEST 6: Health Check
def test_health_check():
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data

# TEST 7: Batch Events
def test_batch_events():
    stats_before = requests.get(f"{BASE_URL}/stats").json()

    for _ in range(20):
        event = create_test_event()
        response = requests.post(f"{BASE_URL}/publish", json=event)
        assert response.status_code == 200

    stats_after = requests.get(f"{BASE_URL}/stats").json()
    assert stats_after["unique_processed"] >= stats_before["unique_processed"] + 20

# TEST 8: Event Persistence
def test_event_persistence():
    event = create_test_event()
    event["topic"] = "persistence-test"

    post_response = requests.post(f"{BASE_URL}/publish", json=event)
    assert post_response.status_code == 200

    time.sleep(0.5)
    get_response = requests.get(f"{BASE_URL}/events", params={"topic": "persistence-test"})
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["count"] > 0

    event_ids = [e["event_id"] for e in data["events"]]
    assert event["event_id"] in event_ids

# TEST 9: Multiple Topics
def test_multiple_topics():
    topics = ["topic-A", "topic-B", "topic-C"]

    for topic in topics:
        event = create_test_event()
        event["topic"] = topic
        response = requests.post(f"{BASE_URL}/publish", json=event)
        assert response.status_code == 200

    stats = requests.get(f"{BASE_URL}/stats").json()
    assert stats["topics"] >= 3

# TEST 10: Stats After Duplicates
def test_stats_after_duplicates():
    stats_before = requests.get(f"{BASE_URL}/stats").json()

    event = create_test_event()
    requests.post(f"{BASE_URL}/publish", json=event)

    for _ in range(3):
        requests.post(f"{BASE_URL}/publish", json=event)

    stats_after = requests.get(f"{BASE_URL}/stats").json()

    assert stats_after["unique_processed"] == stats_before["unique_processed"] + 1
    assert stats_after["duplicate_dropped"] >= stats_before["duplicate_dropped"] + 3

# TEST 11: Event ID Collision Resistance
def test_event_id_uniqueness():
    event_id = f"shared-id-{int(time.time())}"

    event_a = create_test_event(event_id)
    event_a["topic"] = "topic-A"
    r1 = requests.post(f"{BASE_URL}/publish", json=event_a)
    assert r1.json()["is_duplicate"] is False

    event_b = create_test_event(event_id)
    event_b["topic"] = "topic-B"
    r2 = requests.post(f"{BASE_URL}/publish", json=event_b)
    assert r2.json()["is_duplicate"] is False

# TEST 12: Stress Test (Small)
def test_stress_small():
    stats_before = requests.get(f"{BASE_URL}/stats").json()

    events = []
    duplicate_count = 0

    for i in range(100):
        event = create_test_event(f"stress-{i}")
        events.append(event)

    for event in events:
        requests.post(f"{BASE_URL}/publish", json=event)

    for _ in range(30):
        event = random.choice(events)
        requests.post(f"{BASE_URL}/publish", json=event)
        duplicate_count += 1

    time.sleep(1)

    stats_after = requests.get(f"{BASE_URL}/stats").json()

    assert stats_after["unique_processed"] >= stats_before["unique_processed"] + 100
    assert stats_after["duplicate_dropped"] >= stats_before["duplicate_dropped"] + duplicate_count

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
