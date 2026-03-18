# test_ai_engine.py
import sys
sys.path.insert(0, 'ai-engine')
sys.path.insert(0, 'log-collector')

from parser import process_log
from classifier import diagnose_failure
import json

# Same fake log as before
FAKE_LOG = """
Run pip install -r requirements.txt
Collecting flask==2.0.0
Collecting requests
Successfully installed requests-2.28.0
Run python -m pytest tests/
============================= test session starts ==============================
platform linux -- Python 3.11.0
collected 3 items
tests/test_app.py::test_home PASSED
tests/test_app.py::test_login PASSED
tests/test_app.py::test_payment FAILED
================================== FAILURES ===================================
_______________________ test_payment _______________________
    def test_payment():
        response = client.post('/pay', json={'amount': 100})
>       assert response.status_code == 200
E       AssertionError: assert 500 == 200
E       where 500 = <Response [500]>.status_code
tests/test_app.py:45: AssertionError
============================== 1 failed in 3.24s ==============================
Error: Process completed with exit code 1.
"""

# Fake repo context
REPO_CONTEXT = {
    "repo": "abhinav/sample-app",
    "branch": "main",
    "commit_sha": "a1b2c3d",
    "commit_message": "Add payment endpoint",
    "workflow_name": "Run Tests"
}

# Step 1 — Parse the log
print("📋 Step 1 — Parsing log...")
log_result = process_log(FAKE_LOG)
print(f"   Extracted {log_result['failure_lines']} failure lines\n")

# Step 2 — Diagnose with AI
print("🤖 Step 2 — Diagnosing with Mistral...")
diagnosis = diagnose_failure(log_result['failure_block'], REPO_CONTEXT)

# Step 3 — Print result
print("\n" + "=" * 60)
print("🧠 AI DIAGNOSIS RESULT")
print("=" * 60)
print(json.dumps(diagnosis, indent=2))
print("=" * 60)