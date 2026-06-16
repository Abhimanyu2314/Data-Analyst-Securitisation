# Bond Risk Lab — Convexity Sensitivity AI Agent

Premium Streamlit fixed-income risk analytics platform converted from the previous securitisation dashboard to satisfy the Zetheta **Data Analyst - Convexity Sensitivity AI Agent** brief.

## Fast Run
```bash
pip install -r requirements.txt
streamlit run app/bond_risk_lab_app.py
```

On Windows, double-click `run_bond_risk_lab_windows.bat` after installing requirements.

## Included Modules
- Bond pricing engine with Macaulay Duration, Modified Duration, Effective Duration, Convexity and DV01/PVBP
- 300-bond portfolio dataset across INR/USD/EUR/GBP/JPY/AUD instruments
- Parallel, steepening/flattening and butterfly yield-curve scenario lab
- Monte Carlo VaR and CVaR / Expected Shortfall engine
- ML price prediction agent using Random Forest, with optional extension notes for XGBoost and Neural Networks
- Gamified Bond Risk Lab simulation challenge
- Premium Streamlit control-tower UI with animated KPI cards, hidden Plotly toolbar and stress matrix
- Power BI DAX measures, R implementation sample, and Excel/VBA implementation notes
