from flask import Flask, render_template, request

from detector import scan_email

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024  # 1 MB

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

    result = scan_email(text)
    return render_template("result.html", result=result)

@app.get("/health")
def health():
    return {"status": "ok"}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)