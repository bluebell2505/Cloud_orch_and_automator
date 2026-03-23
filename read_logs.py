import requests, os, zipfile, io
from dotenv import load_dotenv
from sympy import python
load_dotenv()

token = os.getenv('GITHUB_TOKEN')
headers = {'Authorization': f'Bearer {token}', 'Accept': 'application/vnd.github+json'}

# Read the most recent Python CI failure
run_id = 23301694834
url = f'https://api.github.com/repos/bluebell2505/Cloud_orch_and_automator/actions/runs/{run_id}/logs'
r = requests.get(url, headers=headers, allow_redirects=True)

z = zipfile.ZipFile(io.BytesIO(r.content))
for filename in z.namelist():
    if filename.endswith('.txt'):
        content = z.read(filename).decode('utf-8', errors='replace')
        print(f'\n=== {filename} ===')
        print(content[:2000])