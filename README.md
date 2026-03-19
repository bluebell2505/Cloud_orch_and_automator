# AI-Powered CI/CD Pipeline Orchestration

An intelligent CI/CD orchestration system that automatically detects, diagnoses, and fixes pipeline failures using LLMs — reducing Mean Time to Recovery (MTTR) without human intervention.

> Built as a research project for IEEE paper submission.

---

## 🧠 How It Works

```
Developer pushes code
        ↓
GitHub Actions runs pipeline
        ↓ (on failure)
Webhook hits Orchestrator
        ↓
Log Collector pulls & cleans logs
        ↓
AI Engine (Mistral) diagnoses failure
        ↓
Remediation Engine executes fix
   ├── retry pipeline
   ├── open PR with fix
   └── notify human on Slack
        ↓
Feedback Loop stores result to DB
        ↓
Grafana dashboard shows metrics
```

---

## 👥 Team

| Member | Role | Module |
|--------|------|--------|
| Person 1 | AI Engineer | `ai-engine/` |
| Person 2 | Backend Engineer | `orchestrator/` |
| Person 3 | DevOps Engineer | `log-collector/`, `pipeline-samples/` |
| Person 4 | Data + Docs Engineer | `feedback-loop/`, `dashboard/`, `paper/` |

---

## 🗂 Project Structure

```
ai-cicd-orchestrator/
├── ai-engine/               # LLM diagnosis engine
│   ├── classifier.py        # Main diagnosis orchestrator
│   ├── prompts.py           # Prompt engineering
│   ├── llm_client.py        # Ollama/Mistral client
│   └── requirements.txt
├── log-collector/           # CI log fetching & parsing
│   ├── collector.py         # GitHub API log fetcher
│   ├── parser.py            # Failure block extractor
│   └── requirements.txt
├── orchestrator/            # FastAPI backend — system brain
│   ├── main.py              # Webhook receiver & coordinator
│   ├── remediation.py       # Fix execution engine
│   ├── github_client.py     # GitHub API interactions
│   └── requirements.txt
├── feedback-loop/           # Data persistence
│   ├── store_result.py      # PostgreSQL event storage
│   └── requirements.txt
├── pipeline-samples/        # Sample apps with intentional bugs
│   ├── python-app/          # Bug: wrong dependency version
│   ├── node-app/            # Bug: undefined function call
│   └── java-app/            # Bug: missing semicolon
├── dashboard/               # Grafana configuration
├── paper/                   # IEEE paper draft
├── docker-compose.yml       # All services in one command
├── .env.example             # Environment variable template
└── README.md
```

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| CI/CD Engine | GitHub Actions |
| Orchestrator | Python, FastAPI |
| AI Engine | Mistral (via Ollama — local, free) |
| Log Ingestion | Elasticsearch + Logstash |
| Database | PostgreSQL |
| Auto-fix PRs | PyGithub |
| Dashboard | Grafana |
| Tunnel (dev) | ngrok |
| Containerization | Docker + Docker Compose |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker Desktop
- Git
- Ollama (for local Mistral)

### 1. Clone the repo
```bash
git clone https://github.com/bluebell2505/Cloud_orch_and_automator.git
cd Cloud_orch_and_automator
```

### 2. Set up environment variables
```bash
cp .env.example .env
# Fill in your values
```

### 3. Start all services
```bash
docker-compose up -d
```

### 4. Pull the AI model
```bash
ollama pull mistral
# If low on RAM, use:
ollama pull tinyllama
```

### 5. Install Python dependencies
```bash
pip install fastapi uvicorn PyGithub requests python-dotenv psycopg2-binary ollama
```

### 6. Start the orchestrator
```bash
uvicorn orchestrator.main:app --reload --port 8000
```

### 7. Start ngrok tunnel
```bash
./ngrok http 8000
```

### 8. Add webhook to GitHub
Go to repo → Settings → Webhooks → Add webhook
- Payload URL: `https://your-ngrok-url/webhook`
- Content type: `application/json`
- Events: Workflow runs

---

## 🐳 Docker Services

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5432 | Failure events database |
| Elasticsearch | 9200 | Log indexing and search |
| Logstash | 5044 | Log parsing pipeline |
| Grafana | 3000 | Metrics dashboard |

---

## 🧪 Failure Scenarios

These bugs are intentionally planted in `pipeline-samples/` to test the AI:

| # | App | Bug | Expected AI Response |
|---|-----|-----|---------------------|
| 1 | Python | `flask==99.0.0` (invalid version) | `dependency_error` → open PR |
| 2 | Node | Undefined function call | `build_error` → notify human |
| 3 | Java | Missing semicolon | `build_error` → notify human |
| 4 | Python | Missing env variable | `config_error` → retry |
| 5 | Python | Random pass/fail test | `flaky_test` → retry |

---

## 📊 Module Interface Contracts

### Log Collector → Orchestrator
```python
# log-collector/parser.py
def extract_failure_block(raw_log: str) -> str
# Returns: 30-50 lines around the error
```

### AI Engine → Orchestrator
```python
# ai-engine/classifier.py
def diagnose_failure(failure_block: str, repo_context: dict) -> dict
# Returns:
{
    "failure_type": "dependency_error | test_failure | config_error | flaky_test | build_error | unknown",
    "root_cause": "one sentence",
    "suggested_fix": "actionable fix",
    "fix_type": "retry | patch_dependency | fix_config | open_pr | notify_human",
    "confidence": 0.0,
    "affected_file": "filename or null"
}
```

### Orchestrator → Feedback Loop
```python
# feedback-loop/store_result.py
def save_event(run_id: str, repo: str, diagnosis: dict, fix_result: dict) -> None
```

---

## 📈 IEEE Metrics

| Metric | Description |
|--------|-------------|
| MTTR | Mean Time to Recovery — AI-assisted vs manual baseline |
| Auto-fix rate | % of failures resolved without human |
| Classifier accuracy | Precision/Recall on failure types |
| False positive rate | Wrong fixes that broke things further |

---

## 🌿 Git Workflow

```bash
# Before starting work every day
git checkout master
git pull origin master
git checkout your-branch
git merge master

# After finishing
git add .
git commit -m "feat(module): description"
git push origin your-branch
# Open PR on GitHub → merge to master
```

### Branch naming
- `member-1/feature-name`
- `member-2/feature-name`
- `bluebell/devops-setup` (Person 3)

---

## 💰 Cost

| Tool | Cost |
|------|------|
| GitHub | Free |
| Mistral via Ollama | Free (runs locally) |
| PostgreSQL | Free (Docker) |
| Elasticsearch | Free (Docker) |
| Grafana | Free (Docker) |
| ngrok | Free tier |
| **Total** | **$0** |

---

## 📄 License

This project is built for academic research purposes.
