"""Root launcher for Bond Risk Lab.
Run with: streamlit run app.py
"""
from pathlib import Path
import runpy

APP_FILE = Path(__file__).resolve().parent / "app" / "bond_risk_lab_app.py"
runpy.run_path(str(APP_FILE), run_name="__main__")
