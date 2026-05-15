# PipOtter: An AI-Powered CI/CD Pipeline Orchestration

PipOtter automatically detects, diagnoses, and fixes CI/CD pipeline failures using a local LLM — no human intervention needed.

---


## What It Does

When a GitHub Actions pipeline fails, this system:

1. Receives the failure event via GitHub webhook
2. Fetches and cleans the raw CI logs
3. Sends the failure context to a local Mistral LLM for diagnosis
4. Automatically executes the right fix:
   - Opens a Pull Request with the corrected code
   - Retries the pipeline (for flaky tests)
   - Sends an email alert (for complex failures)
5. Records everything to PostgreSQL
6. Shows live metrics on a Grafana dashboard

---

## Demo

```
Developer pushes bad code
        ↓
GitHub Actions fails
        ↓
Webhook hits Orchestrator automatically
        ↓
Log Collector fetches real CI logs
        ↓
Mistral AI diagnoses the failure
        ↓
Remediation Engine acts:
   ├── dependency_error  →  opens PR with fix
   ├── flaky_test        →  retries pipeline
   ├── config_error      →  retries with fix
   └── unknown / low confidence  →  emails the owner
        ↓
Event saved to PostgreSQL
        ↓
Grafana dashboard updates in real time
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| CI/CD Engine | GitHub Actions |
| Orchestrator | Python + FastAPI |
| AI Engine | Mistral via Ollama (local, free) |
| Log Ingestion | Elasticsearch + Logstash |
| Database | PostgreSQL |
| Auto-fix PRs | PyGithub |
| Email Alerts | Gmail SMTP |
| Dashboard | Grafana |
| Dev Tunnel | ngrok |
| Containers | Docker + Docker Compose |

---

## Project Structure

```
Cloud_orch_and_automator/
├── ai-engine/                  # LLM diagnosis engine
│   ├── classifier.py           # Two-stage diagnosis with confidence check
│   ├── prompts.py              # Prompt engineering templates
│   ├── llm_client.py           # Ollama/Mistral client
│   └── requirements.txt
├── log-collector/              # CI log fetching and parsing
│   ├── collector.py            # GitHub API log fetcher
│   ├── parser.py               # Failure block extractor
│   └── requirements.txt
├── orchestrator/               # FastAPI backend — system brain
│   ├── main.py                 # Webhook receiver and coordinator
│   ├── remediation.py          # Fix execution engine
│   ├── github_client.py        # GitHub API — logs, PRs, retrigger
│   ├── email_notifier.py       # Gmail alert system
│   └── requirements.txt
├── feedback-loop/              # Data persistence
│   ├── store_result.py         # PostgreSQL event storage
│   ├── db_models.py            # SQLAlchemy models
│   └── requirements.txt
├── pipeline-samples/           # Sample apps with intentional bugs
│   ├── python-app/             # Bug: wrong dependency version
│   ├── node-app/               # Bug: undefined function call
│   └── java-app/               # Bug: missing semicolon
├── dashboard/
│   └── grafana-config/
│       └── dashboard.json      # Import this into Grafana
├── .github/workflows/          # CI workflow definitions
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Docker Desktop
- Git
- Ollama

### 1. Clone the repo
```bash
git clone https://github.com/bluebell2505/Cloud_orch_and_automator.git
cd Cloud_orch_and_automator
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in your values — see .env.example for all required variables
```

### 3. Pull the AI model
```bash
ollama pull mistral
# Low on RAM? Use the lighter model:
ollama pull tinyllama
```

### 4. Start all Docker services
```bash
docker-compose up -d
docker ps   # verify 4 containers are running
```

### 5. Install Python dependencies
```bash
pip install fastapi uvicorn PyGithub requests python-dotenv psycopg ollama
```

### 6. Start the orchestrator
```bash
uvicorn orchestrator.main:app --reload --port 8000
```

### 7. Start ngrok tunnel
```bash
./ngrok http 8000
```

### 8. Configure GitHub webhook
- Go to repo → Settings → Webhooks → Add webhook
- Payload URL: `https://your-ngrok-url/webhook`
- Content type: `application/json`
- Events: Workflow runs only

### 9. Import Grafana dashboard
- Open `http://localhost:3000` (admin/admin)
- Connections → Data sources → Add PostgreSQL
  - Host: `host.docker.internal:5433`
  - Database: `cicd_db`, User: `cicd_user`, Password: `cicd_pass`
  - SSL: disable
- Dashboards → Import → Upload `dashboard/grafana-config/dashboard.json`

---

## Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5433 | Failure events database |
| Elasticsearch | 9200 | Log indexing and search |
| Logstash | 5044 | Log parsing pipeline |
| Grafana | 3000 | Live metrics dashboard |

> Note: PostgreSQL runs on port **5433** to avoid conflicts with any native PostgreSQL installation on port 5432.

---

## How the AI Works

The system uses a **two-stage diagnosis**:

**Stage 1 — Primary diagnosis:**
The failure log is sent to Mistral with a structured prompt that forces JSON output:
```json
{
  "failure_type": "dependency_error",
  "root_cause": "flask==0.0.1 does not exist on PyPI",
  "suggested_fix": "Update flask to a supported version like 3.1.3",
  "fix_type": "patch_dependency",
  "confidence": 0.95,
  "affected_file": "requirements.txt"
}
```

**Stage 2 — Flaky test check (if confidence < 0.6):**
A secondary prompt checks specifically for flaky test patterns and overrides the diagnosis if confirmed.

**Confidence threshold (default 0.65):**
Below this threshold, the system always notifies the human via email instead of attempting an auto-fix.

---

## Failure Scenarios

| # | App | Bug | AI Response |
|---|-----|-----|-------------|
| 1 | Python | `flask==0.0.1` invalid version | `dependency_error` → opens PR |
| 2 | Node | Undefined function call | `build_error` → emails owner |
| 3 | Java | Missing semicolon | `build_error` → emails owner |
| 4 | Python | Missing env variable | `config_error` → retry |
| 5 | Python | Random pass/fail test | `flaky_test` → retry |

---

## Grafana Dashboard Metrics

| Panel | What It Shows |
|-------|--------------|
| Total Failures Processed | Count of all pipeline failures detected |
| Auto-Fixed Successfully | Count of failures resolved automatically |
| Avg Time to Fix (MTTR) | Mean time from failure to fix in seconds |
| Avg AI Confidence Score | Average confidence across all diagnoses |
| Auto-Fix Success Rate | % of failures fixed without human intervention |
| Failure Type Distribution | Bar chart of failure categories |
| Pipeline Failures Over Time | Time series of events |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token (repo + workflow + contents) |
| `GITHUB_REPO` | Format: owner/repo-name |
| `DATABASE_URL` | `postgresql://cicd_user:cicd_pass@127.0.0.1:5433/cicd_db` |
| `OLLAMA_MODEL` | `mistral` or `tinyllama` |
| `CONFIDENCE_THRESHOLD` | Default 0.65 — below this, notify human |
| `EMAIL_SENDER` | Gmail address for sending alerts |
| `EMAIL_PASSWORD` | Gmail app password (16 chars, no spaces) |
| `EMAIL_RECEIVER` | Email address to receive alerts |

---

## Git Workflow

```bash
# Before starting work
git checkout master
git pull origin master
git checkout -b your-branch

# After finishing
git add .
git commit -m "feat(module): description"
git push origin your-branch
# Open PR on GitHub → merge to master
```

---

## Cost

| Tool | Cost |
|------|------|
| GitHub + Actions | Free |
| Mistral via Ollama | Free (runs locally) |
| PostgreSQL | Free (Docker) |
| Elasticsearch | Free (Docker) |
| Grafana | Free (Docker) |
| ngrok | Free tier |
| **Total** | **$0** |


---

