@echo off
REM BuildSure AI — Windows one-command start. Run from the project folder.
setlocal

echo [1/4] Setting up the backend...
cd backend
if not exist .venv ( python -m venv .venv )
call .venv\Scripts\activate
pip install -q -r requirements.txt
if not exist .env ( copy .env.example .env >nul )
if not exist buildsure.db ( python -m app.seed )

echo [2/4] Starting the API on http://localhost:8000 ...
start "BuildSure API" cmd /k ".venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
cd ..

echo [3/4] Installing frontend packages...
cd frontend
if not exist node_modules ( call npm install )

echo [4/4] Starting the React app on http://localhost:5173 ...
call npm run dev

endlocal
