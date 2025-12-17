from fastapi import FastAPI
from app.database import init_db

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/publish")
def publish_event(event: dict):
    return {
        "status": "processed",
        "event_id": event.get("event_id"),
        "is_duplicate": False,
        "message": "Event successfully processed"
    }
