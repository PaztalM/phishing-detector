import logging
from flask import Flask, render_template, request

from detector import scan_email
import db

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("phishing")

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB

try:
    db.init_db()
except Exception as e:
    log.error("database init failed: %s", e)

@app.get("/")
def index():
    return render_template("index.html")

def safe_sender_history(address):
    try:
        return db.sender_history(address)
    except Exception as e:
        log.warning("history lookup failed: %s", e)
        return 0

@app.post("/scan")
def scan():
    uploaded = request.files.get("email_file")
    if uploaded and uploaded.filename:
        text = uploaded.read().decode("utf-8", errors="ignore")
    else:
        text = request.form.get("email_text", "")

    if not text.strip():
        return render_template("index.html", error="Please upload a file or paste an email."), 400        

    result = scan_email(text, history_lookup=safe_sender_history)

    saved = True
    try:
        db.save_scan(result)
    except Exception as e:
        saved = False
        log.error("saving scan failed: %s", e)

    log.info("scan sender=%s score=%s level=%s saved=%s",
             result["sender_address"], result["score"], result["level"], saved)
    return render_template("result.html", result=result, saved=saved)

@app.get("/history")
def history():
    try:
        rows = db.get_history()
    except Exception as e:
        log.error("reading history failed: %s", e)
        return render_template("history.html", rows=[], error="History is unavailable right now."), 503
    return render_template("history.html", rows=rows)

@app.get("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)