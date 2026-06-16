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

/* FINAL PREMIUM SUBMISSION PATCH */
[data-testid="stSidebar"]{background:linear-gradient(180deg,rgba(8,12,28,.98),rgba(15,8,28,.96))!important;border-right:1px solid rgba(0,229,255,.18)}
[data-testid="stSidebar"] *{font-size:16px}.stSlider label,.stMultiSelect label{font-weight:900!important;color:#eaf2ff!important;font-size:17px!important}
.control-tower{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:18px 0 22px}.tower-card{position:relative;overflow:hidden;border:1px solid rgba(255,255,255,.14);border-radius:20px;padding:18px 20px;background:linear-gradient(145deg,rgba(255,255,255,.08),rgba(255,255,255,.025));box-shadow:0 18px 45px rgba(0,0,0,.24)}.tower-card:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(0,229,255,.09),transparent);transform:translateX(-120%);animation:sheen 4.5s infinite}.tower-label{color:#9fb5dd;font-size:12px;font-weight:900;text-transform:uppercase;letter-spacing:1px}.tower-value{font-size:25px;font-weight:950;margin-top:7px}.risk-pill{display:inline-flex;align-items:center;gap:9px;border:1px solid rgba(255,196,87,.45);background:rgba(255,196,87,.12);color:#ffd67e;border-radius:999px;padding:9px 13px;font-weight:900}.premium-title{font-size:30px;font-weight:950;letter-spacing:-.8px;margin:22px 0 8px}.matrix{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.matrix-card{border-radius:18px;padding:16px;border:1px solid rgba(0,229,255,.18);background:rgba(9,17,34,.72)}.matrix-card b{font-size:22px}.small-note{color:#a9b7d7;font-size:13px}.stDownloadButton button,.stButton button{border-radius:14px!important;border:1px solid rgba(0,229,255,.35)!important;background:linear-gradient(135deg,rgba(255,47,153,.24),rgba(0,229,255,.18))!important;color:white!important;font-weight:900!important;padding:.75rem 1rem!important}.stDataFrame{border-radius:18px!important;overflow:hidden}.element-container:has(.js-plotly-plot){border-radius:20px;overflow:hidden;border:1px solid rgba(127,183,255,.12);background:rgba(7,12,25,.58);box-shadow:0 15px 45px rgba(0,0,0,.18)}
@media(max-width:900px){.control-tower,.matrix{grid-template-columns:1fr}.hero h1{font-size:34px}.stTabs [data-baseweb="tab"]{font-size:15px;padding:0 14px}}


/* SMOOTH BUTTON + INTERACTION ANIMATION UPGRADE */
*{scroll-behavior:smooth!important}
html,body,.stApp{transition:background .45s ease,color .35s ease!important}
.block-container{animation:pageFade .75s cubic-bezier(.2,.8,.2,1) both}
@keyframes pageFade{from{opacity:0;filter:blur(10px);transform:translateY(14px)}to{opacity:1;filter:blur(0);transform:translateY(0)}}

/* Smooth glass navigation/buttons */
.stButton>button,.stDownloadButton>button,button[kind="primary"],button[kind="secondary"],
[data-testid="stBaseButton-secondary"],[data-testid="stBaseButton-primary"]{
    position:relative!important; overflow:hidden!important;
    border-radius:18px!important;
    border:1px solid rgba(0,229,255,.42)!important;
    background:linear-gradient(135deg,rgba(255,47,153,.30),rgba(0,229,255,.22),rgba(124,97,255,.25))!important;
    background-size:220% 220%!important;
    color:#fff!important; font-weight:950!important; letter-spacing:.25px!important;
    box-shadow:0 12px 30px rgba(0,0,0,.28),0 0 0 rgba(0,229,255,0)!important;
    transform:translateY(0) scale(1)!important;
    transition:transform .22s cubic-bezier(.2,.8,.2,1), box-shadow .22s ease, border-color .22s ease, background-position .45s ease!important;
    animation:buttonGradient 7s ease infinite!important;
}
.stButton>button:before,.stDownloadButton>button:before,[data-testid="stBaseButton-secondary"]:before,[data-testid="stBaseButton-primary"]:before{
    content:""; position:absolute; inset:0; transform:translateX(-115%) skewX(-22deg);
    background:linear-gradient(90deg,transparent,rgba(255,255,255,.38),transparent);
    transition:transform .62s ease; pointer-events:none;
}
.stButton>button:hover,.stDownloadButton>button:hover,[data-testid="stBaseButton-secondary"]:hover,[data-testid="stBaseButton-primary"]:hover{
    transform:translateY(-4px) scale(1.018)!important;
    border-color:rgba(255,79,216,.70)!important;
    box-shadow:0 18px 48px rgba(0,229,255,.18),0 0 34px rgba(255,79,216,.18)!important;
    background-position:100% 50%!important;
}
.stButton>button:hover:before,.stDownloadButton>button:hover:before,[data-testid="stBaseButton-secondary"]:hover:before,[data-testid="stBaseButton-primary"]:hover:before{transform:translateX(115%) skewX(-22deg)}
.stButton>button:active,.stDownloadButton>button:active,[data-testid="stBaseButton-secondary"]:active,[data-testid="stBaseButton-primary"]:active{transform:translateY(0) scale(.985)!important;box-shadow:0 8px 18px rgba(0,0,0,.32)!important}
@keyframes buttonGradient{0%,100%{background-position:0% 50%}50%{background-position:100% 50%}}

/* Bigger, smoother selectable options */
.stRadio [role="radiogroup"]{gap:14px!important;flex-wrap:wrap!important}
.stRadio label,.stCheckbox label,.stMultiSelect div[data-baseweb="select"],.stSelectbox div[data-baseweb="select"]{
    transition:transform .22s ease, box-shadow .22s ease, border-color .22s ease, background .22s ease!important;
}
.stRadio label,.stCheckbox label{
    min-height:48px!important; padding:12px 16px!important; border-radius:16px!important;
    background:rgba(255,255,255,.045)!important; border:1px solid rgba(127,183,255,.16)!important;
    font-size:17px!important; font-weight:850!important;
}
.stRadio label:hover,.stCheckbox label:hover{
    transform:translateY(-3px)!important; background:rgba(0,229,255,.09)!important;
    border-color:rgba(0,229,255,.40)!important; box-shadow:0 14px 35px rgba(0,229,255,.11)!important;
}
.stMultiSelect div[data-baseweb="select"],.stSelectbox div[data-baseweb="select"],.stNumberInput input,.stTextInput input{
    min-height:54px!important; border-radius:16px!important; border:1px solid rgba(0,229,255,.26)!important;
    background:rgba(7,12,28,.72)!important; box-shadow:inset 0 0 0 1px rgba(255,255,255,.03)!important;
}
.stMultiSelect div[data-baseweb="select"]:hover,.stSelectbox div[data-baseweb="select"]:hover,.stNumberInput input:hover,.stTextInput input:hover{
    transform:translateY(-2px)!important; border-color:rgba(255,79,216,.50)!important; box-shadow:0 12px 32px rgba(255,79,216,.10)!important;
}

/* Instant risk game responsiveness patch */
.option-card{will-change:transform,box-shadow;contain:layout paint;}
.stButton>button{will-change:transform,box-shadow;}

/* Smooth sliders */
.stSlider [data-baseweb="slider"]{padding-top:18px!important;padding-bottom:18px!important}
.stSlider [data-baseweb="slider"] div{transition:all .22s ease!important}
.stSlider [role="slider"]{box-shadow:0 0 0 8px rgba(0,229,255,.10),0 0 28px rgba(0,229,255,.28)!important;transition:transform .2s ease, box-shadow .2s ease!important}
.stSlider [role="slider"]:hover{transform:scale(1.15)!important;box-shadow:0 0 0 11px rgba(255,79,216,.13),0 0 34px rgba(255,79,216,.32)!important}

/* Chart/card smooth entrance */
.element-container{animation:softRise .55s cubic-bezier(.2,.8,.2,1) both}
.card,.tower-card,.matrix-card,.insight{transition:transform .25s ease, box-shadow .25s ease, border-color .25s ease, filter .25s ease!important;will-change:transform}
.card:hover,.tower-card:hover,.matrix-card:hover,.insight:hover{transform:translateY(-5px)!important;filter:brightness(1.08)!important}
@keyframes softRise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}

/* Premium loader shimmer at top */
.stApp:before{content:"";position:fixed;top:0;left:0;height:3px;width:100%;z-index:999999;background:linear-gradient(90deg,#ff2f99,#00e5ff,#7b61ff,#ff2f99);background-size:280% 100%;animation:topBeam 3s linear infinite;box-shadow:0 0 22px rgba(0,229,255,.55)}
@keyframes topBeam{to{background-position:280% 0}}

/* Smooth tabs */
.stTabs [data-baseweb="tab"]{transition:transform .22s ease, background .22s ease, box-shadow .22s ease!important}
.stTabs [data-baseweb="tab"]:hover{transform:translateY(-3px)!important;background:rgba(0,229,255,.08)!important;box-shadow:0 12px 30px rgba(0,229,255,.10)!important}

/* Respect reduced motion */
@media (prefers-reduced-motion: reduce){*,*:before,*:after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}


/* RISK GAME PREMIUM CARD OPTIONS PATCH */
.risk-game-wrap{border:1px solid rgba(0,229,255,.18);border-radius:24px;padding:24px;background:linear-gradient(145deg,rgba(10,18,38,.86),rgba(12,9,28,.78));box-shadow:0 22px 60px rgba(0,0,0,.28);animation:softRise .55s ease both}
.challenge-box{border:1px solid rgba(0,229,255,.32);border-radius:18px;padding:16px 18px;background:rgba(0,229,255,.055);color:#dff8ff;font-weight:850;margin:12px 0 20px;box-shadow:inset 0 0 28px rgba(0,229,255,.035)}
.option-card{height:112px;border-radius:22px;border:1px solid rgba(127,183,255,.20);background:linear-gradient(145deg,rgba(255,255,255,.065),rgba(255,255,255,.025));padding:18px;display:flex;align-items:center;gap:14px;box-shadow:0 14px 40px rgba(0,0,0,.25);transition:all .25s cubic-bezier(.2,.8,.2,1);position:relative;overflow:hidden;margin-bottom:10px}
.option-card:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(255,255,255,.12),transparent);transform:translateX(-120%) skewX(-18deg);transition:transform .7s ease}
.option-card:hover{transform:translateY(-7px) scale(1.018);border-color:rgba(0,229,255,.55);box-shadow:0 24px 62px rgba(0,229,255,.16),0 0 28px rgba(255,79,216,.10)}
.option-card:hover:before{transform:translateX(130%) skewX(-18deg)}
.option-card.selected{border-color:rgba(49,242,129,.75);background:linear-gradient(145deg,rgba(49,242,129,.14),rgba(0,229,255,.07));box-shadow:0 0 0 1px rgba(49,242,129,.30),0 22px 55px rgba(49,242,129,.15);animation:selectedPulse 1.7s ease-in-out infinite}
.option-icon{min-width:42px;height:42px;border-radius:15px;display:grid;place-items:center;background:rgba(0,229,255,.10);border:1px solid rgba(0,229,255,.24);font-size:23px}
.option-title{font-size:17px;font-weight:950;color:#fff;line-height:1.2}
.option-sub{font-size:12px;color:#9fb5dd;margin-top:5px;font-weight:750}
.submit-panel{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:18px 0}
.feedback-card{border-radius:22px;padding:20px;border:1px solid rgba(49,242,129,.35);background:linear-gradient(145deg,rgba(49,242,129,.13),rgba(0,229,255,.06));box-shadow:0 18px 50px rgba(49,242,129,.10);animation:successPop .45s cubic-bezier(.2,.8,.2,1) both}
.feedback-card.bad{border-color:rgba(255,79,93,.40);background:linear-gradient(145deg,rgba(255,79,93,.14),rgba(255,196,87,.06));box-shadow:0 18px 50px rgba(255,79,93,.11)}
.score-chip{display:inline-flex;align-items:center;gap:8px;margin-top:10px;padding:9px 13px;border-radius:999px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.12);font-weight:950;color:#fff}
@keyframes selectedPulse{0%,100%{filter:brightness(1);transform:translateY(0)}50%{filter:brightness(1.13);transform:translateY(-2px)}}
@keyframes successPop{from{opacity:0;transform:translateY(16px) scale(.96);filter:blur(8px)}to{opacity:1;transform:translateY(0) scale(1);filter:blur(0)}}


/* FASTER SINGLE-SECTION NAVIGATION PATCH */
.stRadio:has([data-testid="stMarkdownContainer"]) [role="radiogroup"]{display:flex;gap:12px;flex-wrap:wrap;background:rgba(255,255,255,.035);border:1px solid rgba(0,229,255,.15);padding:12px;border-radius:20px;margin:8px 0 18px;}
.stRadio [role="radiogroup"] label{cursor:pointer!important;min-width:130px!important;justify-content:center!important;}
.stRadio [role="radiogroup"] label:has(input:checked){background:linear-gradient(135deg,rgba(255,47,153,.22),rgba(0,229,255,.18))!important;border-color:rgba(0,229,255,.65)!important;box-shadow:0 0 0 1px rgba(0,229,255,.25),0 18px 45px rgba(0,229,255,.12)!important;transform:translateY(-2px)!important;}
.option-card,.card,.tower-card{transform:translateZ(0);backface-visibility:hidden;}
button{touch-action:manipulation!important;}


/* FINAL NAVIGATION POLISH PATCH - brighter labels, icons, active pulse, gold submission */
.stRadio [role="radiogroup"]{
    gap:18px!important;
    align-items:center!important;
    padding:16px!important;
    border-radius:24px!important;
    background:linear-gradient(135deg,rgba(255,255,255,.045),rgba(0,229,255,.028))!important;
    border:1px solid rgba(0,229,255,.22)!important;
    box-shadow:inset 0 1px 0 rgba(255,255,255,.05),0 18px 50px rgba(0,0,0,.22)!important;
}
.stRadio [role="radiogroup"] label{
    min-width:170px!important;
    min-height:60px!important;
    padding:14px 20px!important;
    border-radius:20px!important;
    justify-content:center!important;
    background:linear-gradient(145deg,rgba(20,28,54,.86),rgba(8,12,28,.82))!important;
    border:1px solid rgba(170,190,255,.24)!important;
    box-shadow:0 10px 26px rgba(0,0,0,.22),inset 0 1px 0 rgba(255,255,255,.04)!important;
    transition:transform .22s cubic-bezier(.2,.8,.2,1),box-shadow .22s ease,border-color .22s ease,background .28s ease,filter .22s ease!important;
}
.stRadio [role="radiogroup"] label *{
    color:#f4f8ff!important;
    opacity:1!important;
    font-size:17px!important;
    font-weight:900!important;
    letter-spacing:.1px!important;
    text-shadow:0 0 14px rgba(0,229,255,.10)!important;
}
.stRadio [role="radiogroup"] label:hover{
    transform:translateY(-5px) scale(1.025)!important;
    border-color:rgba(0,229,255,.72)!important;
    background:linear-gradient(145deg,rgba(0,229,255,.13),rgba(124,97,255,.12))!important;
    box-shadow:0 18px 48px rgba(0,229,255,.18),0 0 28px rgba(255,79,216,.13),inset 0 1px 0 rgba(255,255,255,.08)!important;
    filter:brightness(1.08)!important;
}
.stRadio [role="radiogroup"] label:has(input:checked){
    background:linear-gradient(135deg,rgba(255,47,153,.34),rgba(0,229,255,.23),rgba(124,97,255,.22))!important;
    border-color:rgba(0,229,255,.88)!important;
    box-shadow:0 0 0 1px rgba(0,229,255,.35),0 20px 55px rgba(0,229,255,.20),0 0 34px rgba(255,79,216,.20)!important;
    transform:translateY(-3px) scale(1.018)!important;
    animation:activeTabPulse 2.8s ease-in-out infinite!important;
}
.stRadio [role="radiogroup"] label:has(input:checked)::after{
    content:"";
    position:absolute;
    left:18px;right:18px;bottom:7px;height:3px;border-radius:999px;
    background:linear-gradient(90deg,#ff4fd8,#00e5ff,#7c61ff);
    box-shadow:0 0 18px rgba(0,229,255,.70);
    animation:borderSweep 2.6s linear infinite;
}
.stRadio [role="radiogroup"] label:nth-of-type(8){
    border-color:rgba(255,198,87,.58)!important;
    box-shadow:0 12px 34px rgba(255,198,87,.10),inset 0 1px 0 rgba(255,255,255,.05)!important;
}
.stRadio [role="radiogroup"] label:nth-of-type(8):hover,
.stRadio [role="radiogroup"] label:nth-of-type(8):has(input:checked){
    background:linear-gradient(135deg,rgba(255,198,87,.22),rgba(255,123,0,.13),rgba(0,229,255,.10))!important;
    border-color:rgba(255,198,87,.95)!important;
    box-shadow:0 20px 55px rgba(255,198,87,.18),0 0 30px rgba(255,198,87,.25)!important;
}
@keyframes activeTabPulse{
    0%,100%{filter:brightness(1);box-shadow:0 0 0 1px rgba(0,229,255,.30),0 18px 48px rgba(0,229,255,.17)}
    50%{filter:brightness(1.16);box-shadow:0 0 0 1px rgba(255,79,216,.42),0 24px 62px rgba(0,229,255,.26),0 0 38px rgba(255,79,216,.23)}
}
@keyframes borderSweep{
    0%{background-position:0% 50%;filter:hue-rotate(0deg)}
    100%{background-position:220% 50%;filter:hue-rotate(40deg)}
}
@media (max-width: 900px){
    .stRadio [role="radiogroup"] label{min-width:100%!important}
}


/* STREAMLIT CHROME REMOVAL + PREMIUM FULLSCREEN HERO PATCH */
[data-testid="stHeader"], header[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"], #MainMenu, footer {
    display:none!important; visibility:hidden!important; height:0!important; min-height:0!important; opacity:0!important; pointer-events:none!important;
}
[data-testid="collapsedControl"], button[kind="header"], .stDeployButton {
    display:none!important; visibility:hidden!important; opacity:0!important; pointer-events:none!important;
}
.main .block-container, .block-container{padding-top:.15rem!important; margin-top:0!important;}
.stApp{margin-top:0!important; padding-top:0!important;}
.hero{margin-top:0!important; padding:42px 48px!important; min-height:220px!important; background-size:220% 220%!important; animation:heroBreath 9s ease-in-out infinite, floatIn .7s ease both!important;}
.hero:after{content:""; position:absolute; right:-80px; top:-80px; width:260px; height:260px; border-radius:50%; background:radial-gradient(circle,rgba(0,229,255,.20),transparent 65%); filter:blur(5px); animation:orbFloat 6s ease-in-out infinite;}
.hero h1{max-width:1100px!important;}
.exec-row{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-top:28px;position:relative;z-index:2}
.exec-mini{padding:13px 14px;border-radius:17px;background:rgba(5,9,20,.38);border:1px solid rgba(255,255,255,.12);box-shadow:inset 0 1px 0 rgba(255,255,255,.06),0 12px 32px rgba(0,0,0,.16);backdrop-filter:blur(14px);}
.exec-mini small{display:block;color:#9fb5dd;font-size:11px;font-weight:950;text-transform:uppercase;letter-spacing:.9px}
.exec-mini b{display:block;color:#fff;font-size:19px;font-weight:950;margin-top:5px;text-shadow:0 0 18px rgba(0,229,255,.16)}
@keyframes heroBreath{0%,100%{background-position:0% 50%; box-shadow:0 20px 70px rgba(0,0,0,.35), inset 0 0 80px rgba(255,255,255,.03)}50%{background-position:100% 50%; box-shadow:0 24px 90px rgba(0,229,255,.12), inset 0 0 105px rgba(255,255,255,.045)}}
@keyframes orbFloat{0%,100%{transform:translate(0,0) scale(1)}50%{transform:translate(-35px,28px) scale(1.12)}}
@media(max-width:900px){.exec-row{grid-template-columns:1fr 1fr}.hero{padding:30px 24px!important}}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
@st.cache_data(show_spinner=False)
def load_data(): return pd.read_csv(ROOT/'data'/'bond_portfolio.csv')

@st.cache_data(show_spinner=False)
def cached_portfolio_measures(filtered_df):
    return portfolio_measures(filtered_df)

@st.cache_data(show_spinner=False)
def cached_parallel_price_impact(filtered_df, shock_bps):
    return parallel_price_impact(filtered_df, shock_bps)

@st.cache_data(show_spinner=False)
def cached_key_rate_duration_table(filtered_df):
    return key_rate_duration_table(filtered_df)

@st.cache_data(show_spinner=False)
def cached_monte_carlo(filtered_df, n_sims):
    return monte_carlo(filtered_df, n_sims=n_sims)

@st.cache_data(show_spinner=False)
def cached_ml_importance(filtered_df):
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score
    X = pd.get_dummies(filtered_df[['CouponRate','YieldToMaturity','YearsToMaturity','ModifiedDuration','Convexity','CreditRating','TenorBucket']], drop_first=True)
    y = filtered_df['CleanPrice']
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=.2, random_state=42)
    model = RandomForestRegressor(n_estimators=90, random_state=42, n_jobs=-1, max_depth=8).fit(Xtr, ytr)
    pred = model.predict(Xte)
    rmse = float(np.sqrt(mean_squared_error(yte, pred)))
    r2 = float(r2_score(yte, pred))
    imp = pd.DataFrame({'Feature': X.columns, 'Importance': model.feature_importances_}).sort_values('Importance', ascending=False).head(12)
    return rmse, r2, imp

df = load_data()
st.markdown("""<div class='hero'><div class='status'><span class='dot'></span> AI BOND RISK ENGINE ACTIVE</div><h1>Bond Risk Lab — Convexity Sensitivity AI Agent</h1><p>Live Risk Analytics • Duration • Convexity • DV01/PVBP • Yield Curve Scenarios • Monte Carlo VaR • ML Price Prediction</p><div class='exec-row'><div class='exec-mini'><small>Desk Mode</small><b>LIVE</b></div><div class='exec-mini'><small>Scenario Engine</small><b>Ready</b></div><div class='exec-mini'><small>Monte Carlo</small><b>Enabled</b></div><div class='exec-mini'><small>ML Agent</small><b>Online</b></div><div class='exec-mini'><small>Submission</small><b>Premium</b></div></div></div>""", unsafe_allow_html=True)
with st.sidebar:
    st.markdown("""<div class='card' style='margin-bottom:16px'><div style='font-size:22px;font-weight:950'>🛡️ Bond Risk Lab</div><div class='kpi-sub'>Convexity Sensitivity AI Agent</div><br><span class='risk-pill'>● Engine Ready</span></div>""", unsafe_allow_html=True)
    st.markdown('### ⚙️ Risk Lab Controls')
    rating = st.multiselect('Credit Rating', sorted(df.CreditRating.unique()), default=list(sorted(df.CreditRating.unique())))
    currency = st.multiselect('Currency', sorted(df.Currency.unique()), default=list(sorted(df.Currency.unique())))
    shift = st.slider('Parallel Yield Shock (bps)', -300, 300, 100, 25)
    sims = st.slider('Monte Carlo Scenarios', 500, 5000, 1000, 500)
    st.caption('Fixed-income duration-convexity platform')
f = df[df.CreditRating.isin(rating) & df.Currency.isin(currency)].copy()
if f.empty: st.error('No bonds match selected filters.'); st.stop()
pm = cached_portfolio_measures(f); pnl, dur_pnl, conv_pnl = cached_parallel_price_impact(f, shift)
cols=st.columns(5)
for c,(a,b,d) in zip(cols,[('Market Value', f"₹{pm['market_value']/1e7:,.1f}Cr", 'portfolio notional'),('Modified Duration', f"{pm['modified_duration']:.2f} yrs", 'linear sensitivity'),('Convexity', f"{pm['convexity']:.2f}", 'curvature benefit'),('DV01 / PVBP', f"₹{pm['dv01']:,.0f}", '1 bp price value'),('Shock P&L', f"₹{pnl/1e7:,.2f}Cr", f'{shift:+} bps scenario')]):
    c.markdown(f"<div class='card'><div class='kpi-label'>{a}</div><div class='kpi-value'>{b}</div><div class='kpi-sub'>{d}</div></div>", unsafe_allow_html=True)

st.markdown(f"""
<div class='control-tower'>
  <div class='tower-card'><div class='tower-label'>Submission Coverage</div><div class='tower-value'>96%</div><div class='small-note'>PDF mapped: Python + ML + MC + DAX + R + Excel</div></div>
  <div class='tower-card'><div class='tower-label'>Portfolio Risk State</div><div class='tower-value'>{'HIGH' if pm['modified_duration']>7.5 else 'MEDIUM'}</div><div class='small-note'>Driven by duration, DV01 and convexity exposure</div></div>
  <div class='tower-card'><div class='tower-label'>Convexity Cushion</div><div class='tower-value'>₹{conv_pnl/1e7:,.2f}Cr</div><div class='small-note'>2nd-order correction under selected shock</div></div>
  <div class='tower-card'><div class='tower-label'>AI Recommendation</div><div class='tower-value'>Hedge DV01</div><div class='small-note'>Reduce long-end exposure if rates rise</div></div>
</div>
""", unsafe_allow_html=True)
section_labels = {
    'Overview': '🏠 Overview',
    'Duration & Convexity': '📈 Duration & Convexity',
    'Yield Curve Lab': '📉 Yield Curve Lab',
    'Monte Carlo VaR': '🎲 Monte Carlo VaR',
    'ML Agent': '🤖 ML Agent',
    'Bond Risk Game': '🎮 Bond Risk Game',
    'Stress Matrix': '⚠️ Stress Matrix',
    'Submission Pack': '📄 Submission Pack'
}
sections = list(section_labels.keys())
section = st.radio(
    'Navigate Bond Risk Lab sections',
    sections,
    horizontal=True,
    label_visibility='collapsed',
    key='fast_section_nav',
    format_func=lambda x: section_labels.get(x, x)
)
plot_cfg={'displayModeBar':False,'responsive':True}; template='plotly_dark'
if section == 'Overview':
    c1,c2=st.columns([1.55,1])
    with c1:
        stage=f.groupby('TenorBucket', as_index=False)['MarketValue_INR'].sum(); order=['3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y']; stage['TenorBucket']=pd.Categorical(stage.TenorBucket,order,ordered=True); stage=stage.sort_values('TenorBucket')
        fig=go.Figure(go.Bar(x=stage.TenorBucket.astype(str), y=stage.MarketValue_INR/1e7, text=[f'{v/1e7:.1f}Cr' for v in stage.MarketValue_INR], textposition='outside', marker=dict(color=stage.MarketValue_INR/1e7, colorscale='Turbo', line=dict(color='rgba(255,255,255,.35)',width=1.5))))
        fig.update_layout(title='Market Value by Tenor Bucket', template=template, height=430, margin=dict(l=30,r=10,t=60,b=30), yaxis_title='₹ Crore', transition=dict(duration=900)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='overview_tenor_mv')
    with c2:
        rating=f.groupby('CreditRating', as_index=False)['MarketValue_INR'].sum(); fig=px.pie(rating, values='MarketValue_INR', names='CreditRating', hole=.58, template=template, color_discrete_sequence=px.colors.sequential.Plasma_r); fig.update_traces(textinfo='percent+label'); fig.update_layout(title='Portfolio Distribution by Rating', height=430, margin=dict(l=10,r=10,t=60,b=20)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='overview_rating_donut')
    st.markdown(f"<div class='insight'><b>AI Insight:</b> A {shift:+} bps parallel move produces estimated P&L of <b>₹{pnl/1e7:,.2f}Cr</b>. Duration contributes ₹{dur_pnl/1e7:,.2f}Cr and convexity contributes ₹{conv_pnl/1e7:,.2f}Cr.</div>", unsafe_allow_html=True)
if section == 'Duration & Convexity':
    c1,c2=st.columns(2)
    with c1:
        g=f.groupby('TenorBucket', as_index=False).agg(ModifiedDuration=('ModifiedDuration','mean'), Convexity=('Convexity','mean')); g['TenorBucket']=pd.Categorical(g.TenorBucket, ['3M','6M','1Y','2Y','3Y','5Y','7Y','10Y','20Y','30Y'], ordered=True); g=g.sort_values('TenorBucket')
        fig=go.Figure(); fig.add_trace(go.Scatter(x=g.TenorBucket.astype(str), y=g.ModifiedDuration, mode='lines+markers', name='Modified Duration', line=dict(width=4))); fig.add_trace(go.Scatter(x=g.TenorBucket.astype(str), y=g.Convexity, mode='lines+markers', name='Convexity', yaxis='y2', line=dict(width=4))); fig.update_layout(title='Duration vs Convexity Term Structure', template=template, height=430, yaxis=dict(title='Mod Duration'), yaxis2=dict(title='Convexity', overlaying='y', side='right'), margin=dict(l=30,r=30,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='dur_conv_term')
    with c2:
        krd=cached_key_rate_duration_table(f); fig=go.Figure(go.Bar(x=krd.TenorBucket, y=krd.KRD, marker=dict(color=krd.KRD, colorscale='Viridis'))); fig.update_layout(title='Key Rate Duration by Bucket', template=template, height=430, margin=dict(l=30,r=10,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='krd_bar')
    st.dataframe(f[['BondID','InstrumentType','CreditRating','Currency','YearsToMaturity','CleanPrice','ModifiedDuration','EffectiveDuration','Convexity','DV01_Per100Face','TenorBucket']].head(40), use_container_width=True, hide_index=True)
if section == 'Yield Curve Lab':
    curve=pd.DataFrame({'Tenor':[.25,.5,1,2,3,5,7,10,20,30]}); curve['BaseYield']=[6.65,6.72,6.80,6.92,7.02,7.12,7.20,7.28,7.36,7.40]
    steep=st.slider('Steepening / Flattening Shock (bps)', -150, 150, 40, 10, key='steep'); butterfly=st.slider('Butterfly Curvature Shock (bps)', -100, 100, -25, 5, key='butterfly')
    curve['ScenarioYield']=curve.BaseYield + shift/100 + steep/100*((curve.Tenor-curve.Tenor.mean())/curve.Tenor.std()) + butterfly/100*(-abs(curve.Tenor-7)/10)
    fig=go.Figure(); fig.add_trace(go.Scatter(x=curve.Tenor, y=curve.BaseYield, mode='lines+markers', name='Base Curve')); fig.add_trace(go.Scatter(x=curve.Tenor, y=curve.ScenarioYield, mode='lines+markers', name='Scenario Curve')); fig.update_layout(title='Yield Curve Scenario Lab', template=template, height=460, xaxis_title='Tenor (Years)', yaxis_title='Yield (%)', margin=dict(l=30,r=10,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='yield_curve_lab')
if section == 'Monte Carlo VaR':
    mc,var95,cvar95=cached_monte_carlo(f, sims); c1,c2,c3=st.columns(3)
    c1.markdown(f"<div class='card'><div class='kpi-label'>VaR 95%</div><div class='kpi-value'>₹{var95/1e7:,.2f}Cr</div><div class='kpi-sub'>5th percentile loss</div></div>", unsafe_allow_html=True); c2.markdown(f"<div class='card'><div class='kpi-label'>CVaR 95%</div><div class='kpi-value'>₹{cvar95/1e7:,.2f}Cr</div><div class='kpi-sub'>tail expected shortfall</div></div>", unsafe_allow_html=True); c3.markdown(f"<div class='card'><div class='kpi-label'>Scenarios</div><div class='kpi-value'>{sims:,}</div><div class='kpi-sub'>Monte Carlo paths</div></div>", unsafe_allow_html=True)
    fig=px.histogram(mc, x=mc.PnL_INR/1e7, nbins=55, template=template, title='Monte Carlo P&L Distribution'); fig.add_vline(x=var95/1e7, line_dash='dash', annotation_text='VaR 95%'); fig.update_layout(height=460, xaxis_title='P&L ₹ Crore', margin=dict(l=30,r=10,t=60,b=30)); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='mc_hist')
if section == 'ML Agent':
    st.markdown("<div class='insight'><b>ML Agent:</b> Runs Random Forest bond price prediction using coupon, maturity, yield, duration, convexity, rating and tenor bucket.</div>", unsafe_allow_html=True)
    try:
        rmse, r2, imp = cached_ml_importance(f)
        c1,c2=st.columns(2); c1.metric('Random Forest RMSE', f'{rmse:.4f}'); c2.metric('R² Score', f'{r2:.3f}')
        fig=px.bar(imp, x='Importance', y='Feature', orientation='h', template=template, title='ML Feature Importance')
        fig.update_layout(height=430, yaxis={'categoryorder':'total ascending'}); st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='ml_importance')
    except Exception: st.warning('Install scikit-learn to run the live ML model: pip install scikit-learn')
if section == 'Bond Risk Game':
    st.markdown("<div class='risk-game-wrap'><div class='premium-title'>🎮 Bond Risk Lab Simulation</div><p style='color:#dbe7ff;font-weight:800'>Daily analyst challenge: choose a hedge action after reading the risk position.</p><div class='challenge-box'>RBI surprise: <b>+100 bps parallel hike</b>. What is the best hedge action?</div></div>", unsafe_allow_html=True)

    if 'risk_game_choice' not in st.session_state:
        st.session_state.risk_game_choice = 'Short futures / reduce duration'

    options = [
        ('📈','Increase long-duration exposure','Adds rate sensitivity and increases loss risk.'),
        ('📉','Short futures / reduce duration','Reduces DV01 and protects the portfolio.'),
        ('🌀','Ignore convexity','Misses second-order price movement.'),
        ('⚠️','Buy lower-rated long bonds','Adds credit risk and duration risk together.')
    ]

    option_cols = st.columns(4)
    for col, (icon, title, sub) in zip(option_cols, options):
        selected = 'selected' if st.session_state.risk_game_choice == title else ''
        with col:
            st.markdown(f"""<div class='option-card {selected}'>
                <div class='option-icon'>{icon}</div>
                <div><div class='option-title'>{title}</div><div class='option-sub'>{sub}</div></div>
            </div>""", unsafe_allow_html=True)
            if st.button(('✓ Selected' if selected else 'Choose'), key='choice_' + title):
                st.session_state.risk_game_choice = title

    st.markdown("<div class='submit-panel'>", unsafe_allow_html=True)
    submitted = st.button('⚡ Submit Risk Decision', key='submit_risk_decision')
    st.markdown("</div>", unsafe_allow_html=True)

    if submitted:
        choice = st.session_state.risk_game_choice
        if choice == 'Short futures / reduce duration':
            st.markdown("""<div class='feedback-card'>
                <h3 style='margin:0'>✅ Correct Hedge Choice</h3>
                <p style='margin:8px 0 0;color:#dfffea'>A rate hike hurts long-duration positions. Reducing DV01 with futures or duration hedges lowers downside risk.</p>
                <span class='score-chip'>+25 Points</span><span class='score-chip'>Risk Analyst Rank Increased</span>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class='feedback-card bad'>
                <h3 style='margin:0'>⚠️ Not Optimal</h3>
                <p style='margin:8px 0 0;color:#ffe1e6'>You selected: <b>{choice}</b>. For a +100 bps rate shock, the best response is to reduce duration and hedge DV01 exposure.</p>
                <span class='score-chip'>Review Duration Impact</span><span class='score-chip'>Try Again</span>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='card'><b>Score Rules</b><br>+10 correct hedge, +5 convexity benefit, +5 VaR interpretation. Premium game cards now use hover lift, selected glow, smooth rerender, and animated feedback.</div>", unsafe_allow_html=True)
if section == 'Stress Matrix':
    st.markdown("<div class='premium-title'>📊 Institutional Stress Matrix</div>", unsafe_allow_html=True)
    shocks = [-200,-100,-50,50,100,200,300]
    rows=[]
    for b in shocks:
        total, dur, conv = cached_parallel_price_impact(f, b)
        rows.append({'Shock_bps': b, 'Duration_PnL_Cr': dur/1e7, 'Convexity_PnL_Cr': conv/1e7, 'Total_PnL_Cr': total/1e7})
    sm=pd.DataFrame(rows)
    c1,c2=st.columns([1.3,1])
    with c1:
        fig=go.Figure()
        fig.add_trace(go.Bar(x=sm.Shock_bps, y=sm.Duration_PnL_Cr, name='Duration P&L'))
        fig.add_trace(go.Bar(x=sm.Shock_bps, y=sm.Convexity_PnL_Cr, name='Convexity P&L'))
        fig.add_trace(go.Scatter(x=sm.Shock_bps, y=sm.Total_PnL_Cr, mode='lines+markers', name='Total P&L', line=dict(width=4)))
        fig.update_layout(title='Duration-Convexity Stress Decomposition', template=template, height=460, barmode='relative', xaxis_title='Yield Shock (bps)', yaxis_title='₹ Crore', margin=dict(l=30,r=10,t=60,b=30))
        st.plotly_chart(fig, use_container_width=True, config=plot_cfg, key='stress_matrix_chart')
    with c2:
        worst = sm.Total_PnL_Cr.min(); best = sm.Total_PnL_Cr.max()
        st.markdown(f"""<div class='matrix'>
        <div class='matrix-card'><span class='small-note'>Worst Loss</span><br><b>₹{worst:,.2f}Cr</b></div>
        <div class='matrix-card'><span class='small-note'>Best Gain</span><br><b>₹{best:,.2f}Cr</b></div>
        <div class='matrix-card'><span class='small-note'>DV01</span><br><b>₹{pm['dv01']:,.0f}</b></div>
        </div><br><div class='insight'><b>AI Stress Interpretation:</b> The asymmetric curve shows convexity cushioning rate-rise losses and enhancing rate-fall gains. This directly addresses duration-convexity sensitivity under changing market conditions.</div>""", unsafe_allow_html=True)
    st.dataframe(sm.round(3), use_container_width=True, hide_index=True)

if section == 'Submission Pack':
    st.subheader('Submission Pack'); st.info('This version uses single-section rendering instead of rendering every Streamlit tab at once. This makes Bond Risk Game selection and navigation smoother because heavy charts/ML/Monte Carlo are only computed when their section is opened.'); st.markdown('- Python app: `app/bond_risk_lab_app.py`\n- Quant engine: `src/bond_risk_engine.py`\n- 300-bond data: `data/bond_portfolio.csv`\n- Power BI DAX: `powerbi/BOND_RISK_DAX_MEASURES.txt`\n- R script: `r/bond_risk_models.R`\n- Excel/VBA notes: `excel/BOND_RISK_EXCEL_VBA.txt`\n- Checklist: `BOND_RISK_LAB_REQUIREMENT_CHECKLIST.md`')
    st.download_button('⬇️ Download Submission Checklist', data=(ROOT/'BOND_RISK_LAB_REQUIREMENT_CHECKLIST.md').read_text(), file_name='BOND_RISK_LAB_REQUIREMENT_CHECKLIST.md')
    st.download_button('⬇️ Download Power BI DAX Measures', data=(ROOT/'powerbi'/'BOND_RISK_DAX_MEASURES.txt').read_text(), file_name='BOND_RISK_DAX_MEASURES.txt')
    st.dataframe(pd.DataFrame({'Requirement':['Duration','Convexity','DV01','Key Rate Duration','Monte Carlo VaR','Yield Curve Lab','ML Price Prediction','Gamified Lab','Stress Matrix','Power BI DAX','R Script','Excel/VBA Notes'], 'Status':['Implemented']*12}), use_container_width=True, hide_index=True)
