# DevOps Design
## AI Customer Support Assistant

**Version:** 1.0 | **Date:** June 2026

---

## 1. Overview

No Docker. No cloud. All processes run natively on the host machine. The DevOps strategy focuses on:
- Reproducible local setup (`Makefile` + `requirements.txt`)
- Lightweight CI (GitHub Actions for linting + testing on push)
- Process management with `systemd` or `supervisord`
- Backup scripts for persistent data

---

## 2. Repository Structure

```
ai-support-assistant/
├── .env.example               # Template — copy to .env
├── .gitignore
├── Makefile                   # All developer commands
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini
├── migrations/
│   └── versions/
├── app/
│   ├── main.py                # FastAPI app factory
│   ├── config.py              # Settings via pydantic-settings
│   ├── routers/
│   │   ├── auth.py
│   │   ├── chat.py
│   │   ├── documents.py
│   │   └── health.py
│   ├── services/
│   │   ├── rag_service.py
│   │   ├── llm_service.py
│   │   ├── cache_service.py
│   │   ├── ingest_service.py
│   │   └── sanitizer.py
│   ├── models/
│   │   └── db_models.py
│   └── schemas/
│       └── api_schemas.py
├── frontend/
│   └── index.html             # Single-file chat UI
├── scripts/
│   ├── setup.sh               # One-command setup
│   ├── ingest.py              # CLI document ingest
│   └── backup.sh              # SQLite + ChromaDB backup
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── models/                    # .gitignored — GGUF files here
└── data/
    ├── chroma_db/             # .gitignored
    └── uploads/               # .gitignored
```

---

## 3. Makefile — Developer Commands

```makefile
.PHONY: setup install run test lint format migrate backup

setup:           ## Full first-time setup
	bash scripts/setup.sh

install:         ## Install Python dependencies
	pip install -r requirements.txt

install-dev:     ## Install dev dependencies
	pip install -r requirements-dev.txt

run:             ## Start the application
	uvicorn app.main:app --reload --port 8000

run-llm:         ## Start llama.cpp server
	./models/llama-server -m models/gemma-4-2b-instruct.gguf \
	  --port 8080 --ctx-size 4096 -ngl 0

migrate:         ## Apply DB migrations
	alembic upgrade head

lint:            ## Run linters
	ruff check app/ tests/
	mypy app/

format:          ## Auto-format code
	ruff format app/ tests/

test:            ## Run all tests
	pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:       ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests (requires Redis + ChromaDB)
	pytest tests/integration/ -v

backup:          ## Backup SQLite + ChromaDB
	bash scripts/backup.sh

ingest:          ## Ingest documents from ./data/uploads/
	python scripts/ingest.py --dir data/uploads/
```

---

## 4. Setup Script

```bash
#!/usr/bin/env bash
# scripts/setup.sh

set -e

echo "=== AI Support Assistant Setup ==="

# 1. Check Python version
python3 --version | grep -E "3\.(11|12)" || { echo "Python 3.11+ required"; exit 1; }

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Copy .env
[ -f .env ] || cp .env.example .env
echo "⚠  Edit .env before starting (set SECRET_KEY at minimum)"

# 5. Run migrations
alembic upgrade head

# 6. Create directories
mkdir -p data/chroma_db data/uploads models

echo "✅ Setup complete. Run 'make run' to start."
```

---

## 5. CI/CD Architecture (GitHub Actions)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Lint
        run: |
          ruff check app/ tests/
          mypy app/ --ignore-missing-imports

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.xml
```

---

## 6. Environments

| Environment | Description | Setup |
|-------------|-------------|-------|
| `local-dev` | Developer machine; live reload | `make run` |
| `local-prod` | Stable instance; no reload | `uvicorn app.main:app --port 8000` |
| `ci` | GitHub Actions; no LLM | Unit + lint tests only |

---

## 7. Process Management (Production)

Use `supervisord` or `systemd` to keep services running.

**supervisord.conf excerpt:**
```ini
[program:rag-backend]
command=/path/to/.venv/bin/uvicorn app.main:app --port 8000
directory=/path/to/ai-support-assistant
autostart=true
autorestart=true
stderr_logfile=/var/log/rag-backend.err.log
stdout_logfile=/var/log/rag-backend.out.log

[program:llama-server]
command=/path/to/models/llama-server -m models/gemma-4-2b-instruct.gguf --port 8080
directory=/path/to/ai-support-assistant
autostart=true
autorestart=true
```

---

## 8. Monitoring & Logging

**Log format:** Structured JSON via `structlog`

```python
import structlog
log = structlog.get_logger()

log.info("rag.query", user_id=uid, cache_hit=False, provider="local", latency_ms=1100)
log.warning("llm.fallback", reason="timeout", switching_to="openrouter")
log.error("chromadb.error", error=str(e))
```

**Log destinations:**
- `logs/app.log` — rotating file (10MB, keep 5)
- stdout — captured by supervisord

**Health check:** `GET /api/v1/health` — poll every 30s from a simple cron or monitoring script.

---

## 9. Backup Strategy

```bash
#!/usr/bin/env bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"
mkdir -p "$BACKUP_DIR"

# SQLite online backup
sqlite3 data/app.db ".backup $BACKUP_DIR/app.db"

# ChromaDB — copy directory
cp -r data/chroma_db "$BACKUP_DIR/chroma_db"

# Compress
tar -czf "backups/backup_$DATE.tar.gz" "$BACKUP_DIR"
rm -rf "$BACKUP_DIR"

echo "Backup created: backups/backup_$DATE.tar.gz"
```

**Schedule:** Add to crontab:
```
0 2 * * * /path/to/ai-support-assistant/scripts/backup.sh >> /var/log/rag-backup.log 2>&1
```

---

## 10. Rollback Strategy

Since there is no deployment pipeline, rollback = git revert + migration rollback:

```bash
git revert HEAD            # revert last commit
alembic downgrade -1       # rollback last migration
make run                   # restart
```
