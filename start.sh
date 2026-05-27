#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/backend"

if [ ! -d ".venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
else
  source .venv/bin/activate
fi

if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "Created backend/.env — add OPENAI_API_KEY for full AI answers."
fi

echo ""
echo "Teaching Assistant → http://127.0.0.1:8000"
echo "Press Ctrl+C to stop."
echo ""
exec uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
