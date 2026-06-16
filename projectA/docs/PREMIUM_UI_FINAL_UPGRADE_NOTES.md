# Premium UI Final Upgrade Notes

Applied upgrades:

- Premium loading overlay with blur background, animated progress bar, and boot steps.
- Bloomberg-style dark fintech theme with animated mesh/grid background and floating particles.
- Glassmorphism KPI cards with hover lift, shimmer sweep, glow border, and animated reveal.
- Extra executive metrics row: Stress Loss, DPD60+ Trigger, DPD90+ Watch, Recovery Rate, RAROC Signal.
- Portfolio Health radial gauge with animated neon progress treatment.
- AI Risk Interpretation upgraded into driver cards for delinquency migration, ECL sensitivity, and vintage watchlist.
- Plotly-powered animated charts replacing basic Streamlit charts.
- Premium chart containers with transparent dark panels and hover tooltips.
- Responsive mobile/tablet layout improvements.
- Added Plotly dependency in requirements.txt.

Run instructions:

1. Open the project folder in terminal.
2. Run: pip install -r requirements.txt
3. Run agent first if outputs are missing: python src/securitisation_ai_agent.py --data-dir data --output-dir outputs
4. Launch app: streamlit run app/securitisation_risk_app.py
