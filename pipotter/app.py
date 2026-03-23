# pipotter/app.py
# Run: python app.py
# Visit: http://localhost:5001

from flask import Flask, redirect, send_from_directory
import os

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
GRAFANA_URL = os.getenv("GRAFANA_URL", "http://localhost:3000/d/adks94q/ci-cd-pipeline-metrics?orgId=1&from=2026-03-01T13:24:03.880Z&to=2026-03-31T13:24:03.880Z&timezone=browser")

with open(os.path.join(BASE, "landing.html"), "r") as f:
    LANDING_HTML = f.read()

@app.route("/")
def index():
    return LANDING_HTML

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(os.path.join(BASE, "static"), filename)

@app.route("/dashboard")
def dashboard():
    return redirect(GRAFANA_URL)

@app.route("/health")
def health():
    return {"status": "ok", "service": "PipOtter"}

if __name__ == "__main__":
    print("PipOtter running at http://localhost:5001")
    print(f"Dashboard -> {GRAFANA_URL}")
    app.run(host="0.0.0.0", port=5001, debug=True)