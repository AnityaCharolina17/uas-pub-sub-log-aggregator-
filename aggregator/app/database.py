import psycopg2
from psycopg2.extras import RealDictCursor, Json
import time

def get_db_connection():
    """Get database connection"""
    max_retries = 5
    retry_count = 0

    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host="storage",
                database="eventdb",
                user="admin",
                password="password123"
            )
            return conn
        except psycopg2.OperationalError as e:
            retry_count += 1
            print(f"Database connection failed (attempt {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                time.sleep(2)
            else:
                raise

def init_db():
    """Initialize database schema"""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Tabel events
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_events (
                id SERIAL PRIMARY KEY,
                topic VARCHAR(255) NOT NULL,
                event_id VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                source VARCHAR(255) NOT NULL,
                payload JSONB NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_event UNIQUE(topic, event_id)
            )
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_topic
            ON processed_events(topic)
        """)

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_processed_at
            ON processed_events(processed_at DESC)
        """)

        # Tabel stats (single row)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY DEFAULT 1,
                received BIGINT DEFAULT 0,
                unique_processed BIGINT DEFAULT 0,
                duplicate_dropped BIGINT DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT single_row CHECK (id = 1)
            )
        """)

        cur.execute("""
            INSERT INTO stats (id, received, unique_processed, duplicate_dropped)
            VALUES (1, 0, 0, 0)
            ON CONFLICT (id) DO NOTHING
        """)

        # Audit log
        cur.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id SERIAL PRIMARY KEY,
                event_id VARCHAR(255),
                topic VARCHAR(255),
                action VARCHAR(50),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        print("✅ Database initialized successfully")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def insert_event(event: dict) -> bool:
    """
    Insert event with deduplication.
    Return True jika duplicate, False jika unique.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # received selalu naik
        cur.execute("UPDATE stats SET received = received + 1")

        cur.execute("""
            INSERT INTO processed_events (
                topic, event_id, timestamp, source, payload
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (topic, event_id) DO NOTHING
            RETURNING id
        """, (
            event["topic"],
            event["event_id"],
            event["timestamp"],
            event["source"],
            Json(event["payload"])   # 🔥 INI KUNCINYA
        ))

        inserted = cur.fetchone()

        if inserted:
            cur.execute("UPDATE stats SET unique_processed = unique_processed + 1")
            is_duplicate = False
        else:
            cur.execute("UPDATE stats SET duplicate_dropped = duplicate_dropped + 1")
            is_duplicate = True

        conn.commit()
        return is_duplicate

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
