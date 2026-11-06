import os
import json

import psycopg


def get_connection():
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "phishing"),
        user=os.environ.get("DB_USER", "phish"),
        password=os.environ["DB_PASSWORD"],
        connect_timeout=3,
    )

def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id          SERIAL PRIMARY KEY,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
                sender      TEXT NOT NULL,
                subject     TEXT,
                score       INTEGER NOT NULL,
                level       TEXT NOT NULL,
                is_phishing BOOLEAN NOT NULL,
                indicators  JSONB NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS scans_sender_idx ON scans (sender)")

def save_scan(result):
    indicators = {
        "sender": result["sender"],
        "wording": result["wording"],
        "links": result["links"],
        "attachments": result["attachments"],
    }
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO scans (sender, subject, score, level, is_phishing, indicators)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (result["sender_address"], result["subject"], result["score"],
             result["level"], result["is_phishing"], json.dumps(indicators)),
        )

def get_history(limit=50):
    with get_connection() as conn:
        return conn.execute(
            """SELECT created_at, sender, subject, score, level, is_phishing
               FROM scans ORDER BY created_at DESC LIMIT %s""",
            (limit,),
        ).fetchall()         