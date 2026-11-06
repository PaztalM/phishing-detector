import io

import pytest

import db
from app import app

client = app.test_client()

class FakeDB:
    def __init__(self):
        self.rows = []

    def save_scan(self, result):
        self.rows.append(result)

    def get_history(self, limit=50):
        return []

    def sender_history(self, address):
        return sum(1 for r in self.rows
                   if r["sender_address"] == address and r["is_phishing"])


@pytest.fixture(autouse=True)
def fake_db(monkeypatch):
    fake = FakeDB()
    monkeypatch.setattr(db, "save_scan", fake.save_scan)
    monkeypatch.setattr(db, "get_history", fake.get_history)
    monkeypatch.setattr(db, "sender_history", fake.sender_history)
    return fake

PHISHING = """From: PayPal Security <security@paypa1-support.com>
Subject: Your account will be suspended

Dear customer,
Verify your account immediately:
http://192.168.4.20/login
"""

LEGIT = """From: PayPal <service@paypal.com>
Subject: Your receipt

Hi Matan, thanks for shopping. https://www.paypal.com/activity
"""


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "ok"}


def test_scan_pasted_text():
    r = client.post("/scan", data={"email_text": PHISHING})
    assert r.status_code == 200
    assert b"LIKELY PHISHING" in r.data


def test_scan_uploaded_file():
    data = {"email_file": (io.BytesIO(LEGIT.encode("utf-8")), "legit.txt")}
    r = client.post("/scan", data=data, content_type="multipart/form-data")
    assert r.status_code == 200
    assert b"Probably safe" in r.data


def test_empty_input_is_rejected():
    r = client.post("/scan", data={"email_text": "   "})
    assert r.status_code == 400


def test_too_large_upload_is_rejected():
    big = b"x" * (2 * 1024 * 1024)
    data = {"email_file": (io.BytesIO(big), "big.txt")}
    r = client.post("/scan", data=data, content_type="multipart/form-data")
    assert r.status_code == 413


def test_html_in_email_is_escaped():
    evil = "From: x <a@b.com>\nSubject: hi\n\nhttp://evil.xyz/<script>alert(1)</script>"
    r = client.post("/scan", data={"email_text": evil})
    assert b"<script>" not in r.data
    assert b"&lt;script&gt;" in r.data