@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Creating a local Python environment...
  py -m venv .venv
  if errorlevel 1 goto error
)
echo Installing or checking required libraries...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error
echo Starting ScatterLab. Open http://127.0.0.1:5000 in your browser.
".venv\Scripts\python.exe" app.py
goto end
:error
echo Setup failed. Check Python installation and internet connection, then review README.md.
 pause
:end
