import requests, os
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}

r = requests.get('https://api.github.com/repos/bluebell2505/Cloud_orch_and_automator/actions/runs', headers=headers)
print(f'Status: {r.status_code}')

runs = r.json().get('workflow_runs', [])
for run in runs[:5]:
    print(f"Run {run['id']} — {run['name']} — {run['conclusion']} — {run['created_at']}")
    log_url = f"https://api.github.com/repos/bluebell2505/Cloud_orch_and_automator/actions/runs/{run['id']}/logs"
    log_r = requests.get(log_url, headers=headers, allow_redirects=True)
    print(f"  Logs: {log_r.status_code} — Size: {len(log_r.content)} bytes")
