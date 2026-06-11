#!/usr/bin/env bash
set -euo pipefail

echo "=== AI Support Assistant Setup ==="

python3 --version | grep -E "3\.(11|12)" >/dev/null || {
  echo "Python 3.11+ required"
  exit 1
}

python3 -m venv .venv
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

[ -f .env ] || cp .env.example .env
mkdir -p data/chroma_db data/uploads models logs

alembic upgrade head

echo "Setup complete. Edit .env, then run 'make run'."
