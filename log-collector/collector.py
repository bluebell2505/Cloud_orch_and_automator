# log-collector/collector.py
# Responsible for: fetching logs from GitHub Actions API

import requests
import os
import zipfile
import io
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}


def get_run_logs(repo: str, run_id: int) -> str:
    """
    Downloads and returns the full log text for a GitHub Actions run.
    
    Args:
        repo: Format "owner/repo-name" e.g. "abhinav/my-project"
        run_id: The GitHub Actions workflow run ID (from webhook payload)
    
    Returns:
        Full raw log as a single string
    """
    
    # Step 1: Request log download URL from GitHub
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}/logs"
    response = requests.get(url, headers=HEADERS, allow_redirects=True)
    
    if response.status_code == 404:
        return "ERROR: Run not found or logs expired."
    
    if response.status_code != 200:
        return f"ERROR: Could not fetch logs. Status: {response.status_code}"
    
    # Step 2: Logs come as a ZIP — extract all .txt files inside
    zip_bytes = io.BytesIO(response.content)
    all_logs = []
    
    with zipfile.ZipFile(zip_bytes) as z:
        for filename in z.namelist():
            if filename.endswith('.txt'):
                with z.open(filename) as f:
                    content = f.read().decode('utf-8', errors='replace')
                    all_logs.append(f"=== {filename} ===\n{content}")
    
    return '\n\n'.join(all_logs)


def get_run_info(repo: str, run_id: int) -> dict:
    """
    Fetches metadata about the workflow run — branch, commit, status etc.
    Useful context for the AI engine.
    """
    url = f"https://api.github.com/repos/{repo}/actions/runs/{run_id}"
    response = requests.get(url, headers=HEADERS)
    
    if response.status_code != 200:
        return {}
    
    data = response.json()
    
    return {
        "repo": repo,
        "run_id": run_id,
        "branch": data.get("head_branch", "unknown"),
        "commit_sha": data.get("head_sha", "unknown")[:7],
        "commit_message": data.get("head_commit", {}).get("message", "unknown"),
        "workflow_name": data.get("name", "unknown"),
        "status": data.get("conclusion", "unknown")
    }