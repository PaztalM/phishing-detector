from flask import Flask, render_template, request

from detector import scan_email
import db

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB
db.init_db()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/scan")
def scan():
    uploaded = request.files.get("email_file")
    if uploaded and uploaded.filename:
        text = uploaded.read().decode("utf-8", errors="ignore")
    else:
        text = request.form.get("email_text", "")

    if not text.strip():
        return render_template("index.html", error="Please upload a file or paste an email."), 400        

    result = scan_email(text, history_lookup=db.sender_history)
    db.save_scan(result)
    return render_template("result.html", result=result)

@app.get("/history")
def history():
    rows = db.get_history()
    return render_template("history.html", rows=rows)

@app.get("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)