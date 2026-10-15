@echo off
REM Lance tous les tests et ecrit le resultat dans test-results.txt
cd /d "%~dp0"
echo ===== BACKEND pytest ===== > test-results.txt
cd backend
if not exist .venv python -m venv .venv
call .venv\Scripts\activate
pip install -q -r requirements.txt >> ..\test-results.txt 2>&1
pytest -q >> ..\test-results.txt 2>&1
cd ..\frontend
echo. >> ..\test-results.txt
echo ===== FRONTEND vitest ===== >> ..\test-results.txt
if not exist node_modules call npm install >> ..\test-results.txt 2>&1
call npm run test -- --run >> ..\test-results.txt 2>&1
echo. >> ..\test-results.txt
echo ===== FRONTEND build ===== >> ..\test-results.txt
call npm run lint >> ..\test-results.txt 2>&1
call npm run build >> ..\test-results.txt 2>&1
echo ===== FIN ===== >> ..\test-results.txt
cd ..
echo Termine. Resultats dans test-results.txt
pause
