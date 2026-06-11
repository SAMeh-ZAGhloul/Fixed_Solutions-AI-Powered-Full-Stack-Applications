#!/usr/bin/env bash
set -euo pipefail

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/$DATE"
mkdir -p "$BACKUP_DIR"

if [ -f data/app.db ]; then
  sqlite3 data/app.db ".backup '$BACKUP_DIR/app.db'"
fi

if [ -d data/chroma_db ]; then
  tar -czf "$BACKUP_DIR/chroma_db.tar.gz" data/chroma_db
fi

echo "Backup written to $BACKUP_DIR"
