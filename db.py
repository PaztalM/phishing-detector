import os

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