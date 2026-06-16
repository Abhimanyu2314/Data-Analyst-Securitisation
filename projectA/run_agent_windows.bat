@echo off
cd /d "%~dp0"
echo Running Bond Risk AI Agent outputs...
echo.
python src\bond_risk_engine.py
pause
