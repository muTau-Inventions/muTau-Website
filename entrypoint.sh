#!/bin/sh
set -e

echo "Running database init..."
python -c "
import sys
sys.path.insert(0, '/app/src')
from mutau_website import init_db
init_db()
print('DB init complete.')
"

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 "mutau_website:create_app()"