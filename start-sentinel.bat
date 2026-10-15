@echo off
REM Lance Sentinel PME : backend (port 8000) + frontend (port 5173) dans deux fenetres.
cd /d "%~dp0"

REM Alembic met la base existante a niveau sans supprimer les donnees.
start "Sentinel backend" cmd /k "cd /d ""%~dp0backend"" && if not exist .venv python -m venv .venv && call .venv\Scripts\activate && python -m pip install -q -r requirements.txt && python -m alembic upgrade head && python -m uvicorn app.main:app --reload"
start "Sentinel frontend" cmd /k "cd /d ""%~dp0frontend"" && if not exist node_modules npm install && npm run dev"

echo Backend  : http://localhost:8000/docs
echo Frontend : http://localhost:5173
