from fastapi import FastAPI, Query
from app.database import init_db, insert_event, get_db_connection
from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from psycopg2.extras import RealDictCursor

app = FastAPI()
started_at = datetime.utcnow()


# =======================
# Models
# =======================
class Event(BaseModel):
    topic: str
    event_id: str
    timestamp: datetime
    source: str
    payload: dict


# =======================
# Startup
# =======================
@app.on_event("startup")
def startup_event():
    init_db()


# =======================
# Health
# =======================
@app.get("/health")
def health():
    uptime = (datetime.utcnow() - started_at).total_seconds()
    return {
        "status": "healthy",
        "uptime_seconds": uptime
    }


# =======================
# Publish Event
# =======================
@app.post("/publish")
def publish(event: Event):
    is_duplicate = insert_event(event.dict())
    return {
        "status": "duplicate" if is_duplicate else "processed",
        "event_id": event.event_id,
        "is_duplicate": is_duplicate,
        "message": "Event successfully processed"
    }


# =======================
# Stats
# =======================
@app.get("/stats")
def stats():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("SELECT * FROM stats LIMIT 1")
    stats_row = cur.fetchone()

    cur.execute("SELECT COUNT(DISTINCT topic) AS topics FROM processed_events")
    topic_row = cur.fetchone()

    conn.close()

    return {
        "received": stats_row["received"],
        "unique_processed": stats_row["unique_processed"],
        "duplicate_dropped": stats_row["duplicate_dropped"],
        "topics": topic_row["topics"],
        "started_at": stats_row["started_at"],
        "uptime_seconds": (datetime.utcnow() - started_at).total_seconds()
    }


# =======================
# Events
# =======================
@app.get("/events")
def get_events(
    topic: Optional[str] = Query(None),
    limit: int = Query(100, le=1000)
):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    if topic:
        cur.execute(
            """
            SELECT topic, event_id, timestamp, source, payload, processed_at
            FROM processed_events
            WHERE topic = %s
            ORDER BY processed_at DESC
            LIMIT %s
            """,
            (topic, limit),
        )
    else:
        cur.execute(
            """
            SELECT topic, event_id, timestamp, source, payload, processed_at
            FROM processed_events
            ORDER BY processed_at DESC
            LIMIT %s
            """,
            (limit,),
        )

    events = cur.fetchall()
    conn.close()

    return {
        "count": len(events),
        "topic": topic,
        "events": events
    }
