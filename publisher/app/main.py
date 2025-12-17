import time
import requests
import uuid
from datetime import datetime
import os

AGGREGATOR_URL = os.getenv("AGGREGATOR_URL", "http://aggregator:8080")

def publish_event():
    event = {
        "topic": "publisher.test",
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "publisher-service",
        "payload": {
            "message": "hello from publisher"
        }
    }

    try:
        r = requests.post(f"{AGGREGATOR_URL}/publish", json=event, timeout=5)
        print(f"[PUBLISHER] Sent event {event['event_id']} | status={r.status_code}")
    except Exception as e:
        print(f"[PUBLISHER] Failed to send event: {e}")

if __name__ == "__main__":
    while True:
        publish_event()
        time.sleep(5)
