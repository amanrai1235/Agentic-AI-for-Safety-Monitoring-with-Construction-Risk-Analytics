#!/usr/bin/env bash
# One-command local run: seeds the database, starts the API, starts the React dev server.
set -e
cd "$(dirname "$0")"

echo "→ backend"
cd backend
python3 -m venv .venv 2>/dev/null || true
source .venv/bin/activate
pip install -q -r requirements.txt
[ -f .env ] || cp .env.example .env
python -m app.seed
uvicorn app.main:app --reload --port 8000 &
API_PID=$!
cd ..

echo "→ frontend"
cd frontend
[ -d node_modules ] || npm install
npm run dev

kill $API_PID
