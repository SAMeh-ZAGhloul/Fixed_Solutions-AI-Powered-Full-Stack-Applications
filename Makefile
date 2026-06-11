.PHONY: setup install install-dev run run-llm migrate lint format test test-unit test-integration backup ingest

setup:           ## Full first-time setup
	bash scripts/setup.sh

install:         ## Install Python dependencies
	pip install -r requirements.txt

install-dev:     ## Install dev dependencies
	pip install -r requirements-dev.txt

run:             ## Start the application
	uvicorn app.main:app --reload --port 8000

run-llm:         ## Start llama.cpp server
	llama-server \
	  --hf-repo unsloth/gemma-4-E2B-it-GGUF \
	  --model gemma-4-E2B-it-Q4_K_M.gguf \
	  --cache-ram 2048 \
	  -ctxcp 2 \
	  -c 2048

migrate:         ## Apply DB migrations
	alembic upgrade head

lint:            ## Run linters and type checks
	ruff check app/ tests/
	mypy app/

format:          ## Auto-format code
	ruff format app/ tests/

test:            ## Run all tests
	pytest tests/ -v --cov=app --cov-report=term-missing

test-unit:       ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests
	pytest tests/integration/ -v

backup:          ## Backup SQLite + ChromaDB
	bash scripts/backup.sh

ingest:          ## Ingest documents from ./data/uploads/
	python scripts/ingest.py --dir data/uploads/
