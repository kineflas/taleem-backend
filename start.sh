#!/bin/sh

echo "=== Taleem Backend Starting ==="
echo "DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo 'yes' || echo 'NO!')"
echo "Python version: $(python --version 2>&1)"

echo "Waiting for database..."
for i in $(seq 1 30); do
  if python -c "
from sqlalchemy import create_engine, text
import os
url = os.environ.get('DATABASE_URL', '')
print(f'Connecting to: {url[:30]}...')
e = create_engine(url)
with e.connect() as c:
    c.execute(text('SELECT 1'))
print('Database ready!')
" 2>&1; then
    break
  fi
  echo "  attempt $i/30 — retrying in 2s..."
  sleep 2
done

echo "Running migrations..."
alembic upgrade head 2>&1
if [ $? -ne 0 ]; then
  echo "ERROR: Alembic migrations failed!"
  echo "Sleeping to keep container alive for debugging..."
  sleep 3600
  exit 1
fi

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
