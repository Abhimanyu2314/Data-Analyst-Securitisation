import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT/'src'))
from bond_risk_engine import portfolio_measures, parallel_price_impact, monte_carlo, key_rate_duration_table

st.set_page_config(page_title='Bond Risk Lab | Convexity AI Agent', layout='wide', page_icon='📈')
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
html, body, [class*="css"] {font-family: Inter, sans-serif;}
.stApp {background: radial-gradient(circle at 0% 0%, #34113f 0%, transparent 26%), radial-gradient(circle at 90% 10%, #064b5a 0%, transparent 30%), #050914; color:#fff;}
.block-container{padding-top:1.2rem; max-width:1500px;}
.hero{position:relative; overflow:hidden; border:1px solid rgba(0,229,255,.25); border-radius:28px; padding:34px 42px; margin-bottom:24px; background:linear-gradient(120deg,rgba(255,47,153,.22),rgba(0,229,255,.16),rgba(91,97,255,.13)); box-shadow:0 20px 70px rgba(0,0,0,.35), inset 0 0 80px rgba(255,255,255,.03); animation:floatIn .7s ease both;}
.hero:before{content:"";position:absolute;inset:-80px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.11),transparent);transform:rotate(20deg);animation:sheen 5s infinite;}
.hero h1{font-size:50px;line-height:1.05;margin:0;font-weight:900;letter-spacing:-1.5px;text-shadow:0 0 30px rgba(0,229,255,.25)}
.hero p{color:#cbd5ff;font-size:17px;margin-top:12px}.status{display:inline-flex;gap:10px;align-items:center;padding:10px 16px;border-radius:99px;background:rgba(28,255,130,.10);border:1px solid rgba(28,255,130,.28);color:#a7ffcb;font-weight:800}.dot{width:10px;height:10px;background:#31f281;border-radius:50%;box-shadow:0 0 16px #31f281;animation:pulse 1.8s infinite}
.card{border:1px solid rgba(127,183,255,.18);border-radius:22px;padding:22px;background:linear-gradient(145deg,rgba(16,24,48,.9),rgba(9,13,28,.76));box-shadow:0 16px 45px rgba(0,0,0,.28);transition:.28s;animation:floatIn .8s ease both}.card:hover{transform:translateY(-6px);border-color:rgba(0,229,255,.45);box-shadow:0 20px 55px rgba(0,229,255,.13)}
.kpi-label{color:#00e5ff;font-weight:800;font-size:13px;text-transform:uppercase;letter-spacing:.8px}.kpi-value{font-size:31px;font-weight:900;margin:8px 0;text-shadow:0 0 18px rgba(255,255,255,.18);animation:numberPop .8s ease both}.kpi-sub{color:#aab7d9;font-size:13px}.insight{border-left:4px solid #00e5ff;background:rgba(0,229,255,.07);padding:16px 18px;border-radius:16px;color:#dce8ff}.stTabs [data-baseweb="tab-list"]{gap:16px;background:rgba(255,255,255,.035);padding:12px;border-radius:18px}.stTabs [data-baseweb="tab"]{height:58px;padding:0 26px;border-radius:16px;color:#dbe4ff;font-size:18px;font-weight:800}.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(255,47,153,.24),rgba(0,229,255,.16));border-bottom:3px solid #ff4fd8}.js-plotly-plot .plotly .modebar{display:none!important}
@keyframes sheen{0%{transform:translateX(-120%) rotate(20deg)}55%,100%{transform:translateX(130%) rotate(20deg)}}@keyframes pulse{0%,100%{opacity:.6;transform:scale(1)}50%{opacity:1;transform:scale(1.35)}}@keyframes floatIn{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:translateY(0)}}@keyframes numberPop{from{opacity:0;transform:scale(.9)}to{opacity:1;transform:scale(1)}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
@st.cache_data
def load_data(): return pd.read_csv(ROOT/'data'/'bond_portfolio.csv')
df = load_data()
st.markdown("""<div class='hero'><div class='status'><span class='dot'></span> AI BOND RISK ENGINE ACTIVE</div><h1>Bond Risk Lab — Convexity Sensitivity AI Agent</h1><p>Duration | Convexity | DV01/PVBP | Key Rate Duration | Yield Curve Scenarios | Monte Carlo VaR | ML Price Prediction</p></div>""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown('### ⚙️ Risk Lab Controls')
    rating = st.multiselect('Credit Rating', sorted(df.CreditRating.unique()), default=list(sorted(df.CreditRating.unique())))
    currency = st.multiselect('Currency', sorted(df.Currency.unique()), default=list(sorted(df.Currency.unique())))
    shift = st.slider('Parallel Yield Shock (bps)', -300, 300, 100, 25)
    sims = st.slider('Monte Carlo Scenarios', 500, 5000, 1000, 500)
    st.caption('Fixed-income duration-convexity platform')
f = df[df.CreditRating.isin(rating) & df.Currency.isin(currency)].copy()
if f.empty: st.error('No bonds match selected filters.'); st.stop()
pm = portfolio_measures(f); pnl, dur_pnl, conv_pnl = parallel_price_impact(f, shift)
cols=st.columns(5)
for c,(a,b,d) in zip(cols,[('Market Value', f"₹{pm['market_value']/1e7:,.1f}Cr", 'portfolio notional'),('Modified Duration', f"{pm['modified_duration']:.2f} yrs", 'linear sensitivity'),('Convexity', f"{pm['convexity']:.2f}", 'curvature benefit'),('DV01 / PVBP', f"₹{pm['dv01']:,.0f}", '1 bp price value'),('Shock P&L', f"₹{pnl/1e7:,.2f}Cr", f'{shift:+} bps scenario')]):
    c.markdown(f"<div class='card'><div class='kpi-label'>{a}</div><div class='kpi-value'>{b}</div><div class='kpi-sub'>{d}</div></div>", unsafe_allow_html=True)
tabs = st.tabs(['Overview','Duration & Convexity','Yield Curve Lab','Monte Carlo VaR','ML Agent','Bond Risk Game','Submission Pack'])
plot_cfg={'displayModeBar':False,'responsive':True}; template='plotly_dark'
with tabs[0]:
    c1,c2=st.columns([1.55,1])
    with c1:
        stage=f.groupby('TenorBucket', as_index=False)['MarketValue_INR'].sum(); order=['3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y']; stage['TenorBucket']=pd.Categorical(stage.TenorBucket,order,ordered=True); stage=stage.sort_values('TenorBucket')
        fig=go.Figure(go.Bar(x=stage.TenorBucket.astype(str), y=stage.MarketValue_INR/1e7, text=[f'{v/1e7:.1f}Cr' for v in stage.MarketValue_INR], textposition='outside', marker=dict(color=stage.MarketValue_INR/1e7, colorscale='Turbo', line=dict(color='rgba(255,255,255,.35)',width=1.5))))
        fig.update_layout(title='Market Value by Tenor Bucket', template=template, height=430, margin=dict(l=30,r=10,t=60,b=30), yaxis_title='₹ Crore', transition=dict(duration=900)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='overview_tenor_mv')
    with c2:
        rating=f.groupby('CreditRating', as_index=False)['MarketValue_INR'].sum(); fig=px.pie(rating, values='MarketValue_INR', names='CreditRating', hole=.58, template=template, color_discrete_sequence=px.colors.sequential.Plasma_r); fig.update_traces(textinfo='percent+label'); fig.update_layout(title='Portfolio Distribution by Rating', height=430, margin=dict(l=10,r=10,t=60,b=20)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='overview_rating_donut')
    st.markdown(f"<div class='insight'><b>AI Insight:</b> A {shift:+} bps parallel move produces estimated P&L of <b>₹{pnl/1e7:,.2f}Cr</b>. Duration contributes ₹{dur_pnl/1e7:,.2f}Cr and convexity contributes ₹{conv_pnl/1e7:,.2f}Cr.</div>", unsafe_allow_html=True)
with tabs[1]:
    c1,c2=st.columns(2)
    with c1:
        g=f.groupby('TenorBucket', as_index=False).agg(ModifiedDuration=('ModifiedDuration','mean'), Convexity=('Convexity','mean')); g['TenorBucket']=pd.Categorical(g.TenorBucket, ['3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y'], ordered=True); g=g.sort_values('TenorBucket')
        fig=go.Figure(); fig.add_trace(go.Scatter(x=g.TenorBucket.astype(str), y=g.ModifiedDuration, mode='lines+markers', name='Modified Duration', line=dict(width=4))); fig.add_trace(go.Scatter(x=g.TenorBucket.astype(str), y=g.Convexity, mode='lines+markers', name='Convexity', yaxis='y2', line=dict(width=4))); fig.update_layout(title='Duration vs Convexity Term Structure', template=template, height=430, yaxis=dict(title='Mod Duration'), yaxis2=dict(title='Convexity', overlaying='y', side='right'), margin=dict(l=30,r=30,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='dur_conv_term')
    with c2:
        krd=key_rate_duration_table(f); fig=go.Figure(go.Bar(x=krd.TenorBucket, y=krd.KRD, marker=dict(color=krd.KRD, colorscale='Viridis'))); fig.update_layout(title='Key Rate Duration by Bucket', template=template, height=430, margin=dict(l=30,r=10,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='krd_bar')
    st.dataframe(f[['BondID','InstrumentType','CreditRating','Currency','YearsToMaturity','CleanPrice','ModifiedDuration','EffectiveDuration','Convexity','DV01_Per100Face','TenorBucket']].head(40), use_container_width=True, hide_index=True)
with tabs[2]:
    curve=pd.DataFrame({'Tenor':[.25,.5,1,2,3,5,7,10,20,30]}); curve['BaseYield']=[6.65,6.72,6.80,6.92,7.02,7.12,7.20,7.28,7.36,7.40]
    steep=st.slider('Steepening / Flattening Shock (bps)', -150, 150, 40, 10, key='steep'); butterfly=st.slider('Butterfly Curvature Shock (bps)', -100, 100, -25, 5, key='butterfly')
    curve['ScenarioYield']=curve.BaseYield + shift/100 + steep/100*((curve.Tenor-curve.Tenor.mean())/curve.Tenor.std()) + butterfly/100*(-abs(curve.Tenor-7)/10)
    fig=go.Figure(); fig.add_trace(go.Scatter(x=curve.Tenor, y=curve.BaseYield, mode='lines+markers', name='Base Curve')); fig.add_trace(go.Scatter(x=curve.Tenor, y=curve.ScenarioYield, mode='lines+markers', name='Scenario Curve')); fig.update_layout(title='Yield Curve Scenario Lab', template=template, height=460, xaxis_title='Tenor (Years)', yaxis_title='Yield (%)', margin=dict(l=30,r=10,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='yield_curve_lab')
with tabs[3]:
    mc,var95,cvar95=monte_carlo(f, n_sims=sims); c1,c2,c3=st.columns(3)
    c1.markdown(f"<div class='card'><div class='kpi-label'>VaR 95%</div><div class='kpi-value'>₹{var95/1e7:,.2f}Cr</div><div class='kpi-sub'>5th percentile loss</div></div>", unsafe_allow_html=True); c2.markdown(f"<div class='card'><div class='kpi-label'>CVaR 95%</div><div class='kpi-value'>₹{cvar95/1e7:,.2f}Cr</div><div class='kpi-sub'>tail expected shortfall</div></div>", unsafe_allow_html=True); c3.markdown(f"<div class='card'><div class='kpi-label'>Scenarios</div><div class='kpi-value'>{sims:,}</div><div class='kpi-sub'>Monte Carlo paths</div></div>", unsafe_allow_html=True)
    fig=px.histogram(mc, x=mc.PnL_INR/1e7, nbins=55, template=template, title='Monte Carlo P&L Distribution'); fig.add_vline(x=var95/1e7, line_dash='dash', annotation_text='VaR 95%'); fig.update_layout(height=460, xaxis_title='P&L ₹ Crore', margin=dict(l=30,r=10,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='mc_hist')
with tabs[4]:
    st.markdown("<div class='insight'><b>ML Agent:</b> Runs Random Forest bond price prediction using coupon, maturity, yield, duration, convexity, rating and tenor bucket.</div>", unsafe_allow_html=True)
    try:
        from sklearn.ensemble import RandomForestRegressor; from sklearn.model_selection import train_test_split; from sklearn.metrics import mean_squared_error, r2_score
        X=pd.get_dummies(f[['CouponRate','YieldToMaturity','YearsToMaturity','ModifiedDuration','Convexity','CreditRating','TenorBucket']], drop_first=True); y=f['CleanPrice']; Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42); model=RandomForestRegressor(n_estimators=160, random_state=42).fit(Xtr,ytr); pred=model.predict(Xte); rmse=float(np.sqrt(mean_squared_error(yte,pred))); r2=float(r2_score(yte,pred)); c1,c2=st.columns(2); c1.metric('Random Forest RMSE', f'{rmse:.4f}'); c2.metric('R² Score', f'{r2:.3f}'); imp=pd.DataFrame({'Feature':X.columns,'Importance':model.feature_importances_}).sort_values('Importance', ascending=False).head(12); fig=px.bar(imp, x='Importance', y='Feature', orientation='h', template=template, title='ML Feature Importance'); fig.update_layout(height=430, yaxis={'categoryorder':'total ascending'}); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='ml_importance')
    except Exception: st.warning('Install scikit-learn to run the live ML model: pip install scikit-learn')
with tabs[5]:
    st.subheader('🎮 Bond Risk Lab Simulation'); st.write('Daily analyst challenge: choose a hedge action after reading the risk position.'); choice=st.radio('RBI surprise: +100 bps parallel hike. Best action?', ['Increase long-duration exposure','Short futures / reduce duration','Ignore convexity','Buy lower-rated long bonds'], horizontal=True)
    if st.button('Submit Risk Decision'):
        st.success('Correct. A rate hike hurts long duration. Reducing DV01 lowers loss exposure.') if choice=='Short futures / reduce duration' else st.error('Not optimal. Review duration impact and DV01 exposure.')
    st.markdown("<div class='card'><b>Score Rules</b><br>+10 correct hedge, +5 convexity benefit, +5 VaR interpretation.</div>", unsafe_allow_html=True)
with tabs[6]:
    st.subheader('Submission Pack'); st.markdown('- Python app: `app/bond_risk_lab_app.py`\n- Quant engine: `src/bond_risk_engine.py`\n- 300-bond data: `data/bond_portfolio.csv`\n- Power BI DAX: `powerbi/BOND_RISK_DAX_MEASURES.txt`\n- R script: `r/bond_risk_models.R`\n- Excel/VBA notes: `excel/BOND_RISK_EXCEL_VBA.txt`\n- Checklist: `BOND_RISK_LAB_REQUIREMENT_CHECKLIST.md`')
    st.dataframe(pd.DataFrame({'Requirement':['Duration','Convexity','DV01','Key Rate Duration','Monte Carlo VaR','Yield Curve Lab','ML Price Prediction','Gamified Lab'], 'Status':['Implemented']*8}), use_container_width=True, hide_index=True)
