import sys
import os
import importlib.util

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod

parser = load_module("parser", os.path.join(PROJECT_ROOT, "log-collector", "parser.py"))
collector_mod = load_module("collector", os.path.join(PROJECT_ROOT, "log-collector", "collector.py"))
classifier = load_module("classifier", os.path.join(PROJECT_ROOT, "ai-engine", "classifier.py"))

extract_failure_block = parser.extract_failure_block
clean_log = parser.clean_log
diagnose_failure = classifier.diagnose_failure

sys.path.insert(0, os.path.join(PROJECT_ROOT, "orchestrator"))

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from remediation import execute_fix
from github_client import get_logs_from_github

load_dotenv()

app = FastAPI(title="CI/CD Orchestrator", version="1.0.0")

@app.get("/")
def root():
    return {"status": "CI/CD Orchestrator is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/webhook")
async def handle_pipeline_failure(request: Request):
    payload = await request.json()

    if payload.get("action") != "completed":
        return JSONResponse({"status": "ignored", "reason": "action is not completed"})

    conclusion = payload.get("workflow_run", {}).get("conclusion")
    if conclusion != "failure":
        return JSONResponse({"status": "ignored", "reason": f"conclusion is {conclusion}"})

    repo = payload["repository"]["full_name"]
    run_id = payload["workflow_run"]["id"]
    workflow_name = payload["workflow_run"]["name"]

    print(f"[WEBHOOK] Failure in {repo} - {workflow_name} - run {run_id}")

    print("[STEP 1] Fetching logs...")
    raw_log = get_logs_from_github(repo, run_id)
    cleaned_log = clean_log(raw_log)
    failure_block = extract_failure_block(cleaned_log)
    print(f"[STEP 1] Extracted {len(failure_block.splitlines())} lines")

    print("[STEP 2] Running AI diagnosis...")
    repo_context = {
    "repo": repo,
    "branch": "master",
    "workflow_name": workflow_name,
    "commit_sha": payload["workflow_run"].get("head_sha", "unknown")[:7],
    "commit_message": payload["workflow_run"].get("head_commit", {}).get("message", "unknown") if payload["workflow_run"].get("head_commit") else "unknown"
}
    diagnosis = diagnose_failure(failure_block, repo_context)
    print(f"[STEP 2] Type: {diagnosis.get('failure_type')} | Fix: {diagnosis.get('fix_type')}")

    print("[STEP 3] Executing fix...")
    fix_result = execute_fix(diagnosis, repo, run_id)
    print(f"[STEP 3] Action: {fix_result.get('action')}")

    try:
        store = load_module("store_result", os.path.join(PROJECT_ROOT, "feedback-loop", "store_result.py"))
        store.save_event(str(run_id), repo, diagnosis, fix_result)
        print("[STEP 4] Saved to DB")
    except Exception as e:
        print(f"[STEP 4] DB save skipped: {e}")

    return JSONResponse({
        "status": "processed",
        "repo": repo,
        "run_id": run_id,
        "diagnosis": diagnosis,
        "fix_result": fix_result
    })
