# Premium Styling and Animation Upgrade

Applied to: `app/securitisation_risk_app.py`

## What was upgraded

- Premium glassmorphism command-center dashboard theme
- Animated cyber grid background and floating glow particles
- Expanded sidebar with branded Risk Command panel
- Hero shimmer animation with executive title section
- Live status pills with pulse indicator
- KPI card reveal animation, hover lift, neon border glow, and shine sweep
- Animated portfolio health bar with neon pulse
- Premium risk badge glow for LOW / MEDIUM / HIGH states
- Recommendation cards with slide-in animation and hover movement
- Styled Streamlit tabs, download buttons, tables, charts, and responsive layout
- Mobile responsive typography and spacing
- Reduced-motion accessibility support

## How to run

```cmd
setup_windows.bat
run_agent_windows.bat
run_app_windows.bat
```

Or manually:

```cmd
pip install -r requirements.txt
python src/securitisation_ai_agent.py --data-dir data --output-dir outputs
streamlit run app/securitisation_risk_app.py
```

## Notes

The business logic was not broken or replaced. Only the UI layer was upgraded, with safe CSS/HTML animations inside Streamlit.
