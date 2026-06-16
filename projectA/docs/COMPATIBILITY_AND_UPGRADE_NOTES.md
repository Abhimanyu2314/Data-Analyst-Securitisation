# Device Compatibility & Upgrade Notes

## What was added
- Python securitisation AI risk agent
- Streamlit risk terminal
- Windows setup and run scripts
- Power BI DAX measures
- Output report generation

## Compatibility
Use Python 3.10 to 3.12.

## Run order
1. `setup_windows.bat`
2. `run_agent_windows.bat`
3. `run_app_windows.bat`

## Why this upgrade was needed
The uploaded CSVs are auto-loan securitisation datasets, not bond portfolio outputs. This upgrade builds a compatible AI Agent around these exact files.
