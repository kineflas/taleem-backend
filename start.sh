#!/bin/sh
set -e

echo "Waiting for database..."
for i in $(seq 1 30); do
  if python -c "
from sqlalchemy import create_engine, text
import os
e = create_engine(os.environ['DATABASE_URL'])
with e.connect() as c:
    c.execute(text('SELECT 1'))
print('Database ready!')
" 2>/dev/null; then
    break
  fi
  echo "  attempt $i/30 — retrying in 2s..."
  sleep 2
done

echo "Running migrations..."
alembic upgrade head

echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
