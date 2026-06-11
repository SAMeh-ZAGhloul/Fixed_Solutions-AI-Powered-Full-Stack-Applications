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
	./models/llama-server -m models/gemma-4-2b-instruct.gguf \
	  --port 8080 --ctx-size 4096 -ngl 0

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
