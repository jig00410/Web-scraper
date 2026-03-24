import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(
    page_title="WebScraper Pro — Advanced Web Data Extraction",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styles import apply_theme, theme_selector, get_theme
from utils.icons import icon

t = apply_theme()

# ── Extra CSS for landing page ─────────────────────────────────────────────────
st.markdown(f"""
<style>
/* Hide sidebar completely on landing */
[data-testid="stSidebar"] {{ display: none !important; }}

/* Remove ALL default padding so layout fills edge to edge */
.block-container {{
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}}

/* Hero CTA button */
.cta-btn > button {{
    background: {t['accent']} !important;
    color: #fff !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 0.8rem 2.5rem !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 6px 28px {t['accent_glow']} !important;
    letter-spacing: 0.02em !important;
    width: 100% !important;
}}
.cta-btn > button:hover {{
    filter: brightness(1.12) !important;
    transform: translateY(-2px) !important;
}}

/* Feature cards */
.feat-card {{
    background: {t['card']};
    border: 1px solid {t['border']};
    border-radius: 16px;
    padding: 1.6rem;
    height: 100%;
    transition: border-color 0.25s, transform 0.25s;
}}
.feat-card:hover {{
    border-color: {t['accent']};
    transform: translateY(-4px);
}}
.feat-icon {{
    width: 46px; height: 46px;
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    margin-bottom: 1rem;
}}
.feat-title {{
    font-size: 0.97rem; font-weight: 700;
    color: {t['text']}; margin-bottom: 0.45rem;
}}
.feat-desc {{
    font-size: 0.82rem; color: {t['text2']}; line-height: 1.65;
}}

/* Step circle */
.step-circle {{
    width: 58px; height: 58px; border-radius: 50%;
    border: 2px solid {t['accent']};
    background: {t['card']};
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 1rem;
    font-size: 1.25rem; font-weight: 800; color: {t['accent']};
    box-shadow: 0 0 22px {t['accent_glow']};
}}

/* Stat numbers */
.stat-num {{
    font-size: 2rem; font-weight: 800;
    letter-spacing: -0.04em; color: {t['accent']};
    text-align: center;
}}
.stat-lbl {{
    font-size: 0.7rem; color: {t['text2']};
    text-transform: uppercase; letter-spacing: 0.08em;
    text-align: center; margin-top: 3px;
}}

/* Section labels */
.sec-label {{
    font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.12em;
    color: {t['accent']}; text-align: center; margin-bottom: 0.4rem;
}}
.sec-title {{
    font-size: 2rem; font-weight: 800;
    letter-spacing: -0.04em; color: {t['text']};
    text-align: center; margin-bottom: 0.65rem;
}}
.sec-sub {{
    font-size: 0.95rem; color: {t['text2']};
    text-align: center; line-height: 1.7;
    max-width: 560px; margin: 0 auto 2.5rem;
}}

/* Tech badge */
.tech-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 0.4rem 1rem;
    background: {t['card']}; border: 1px solid {t['border']};
    border-radius: 99px; font-size: 0.82rem;
    color: {t['text2']}; font-weight: 500;
    margin: 0.3rem;
}}

/* Nav link */
.nav-link {{
    color: {t['text2']}; font-size: 0.88rem;
    font-weight: 500; text-decoration: none;
    transition: color 0.2s;
}}
.nav-link:hover {{ color: {t['text']}; }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  NAVBAR
# ══════════════════════════════════════════════════════════
nav_l, nav_m, nav_r = st.columns([3, 4, 3])

with nav_l:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:10px;padding:1rem 0 0.5rem 1rem;
         font-weight:700;font-size:1.05rem;color:{t['text']};">
      <div style="width:36px;height:36px;
           background:linear-gradient(135deg,{t['accent']},{t['accent_h']});
           border-radius:10px;display:flex;align-items:center;justify-content:center;
           box-shadow:0 0 16px {t['accent_glow']};">
        {icon('globe',18,'#fff')}
      </div>
      WebScraper Pro
    </div>
    """, unsafe_allow_html=True)

with nav_m:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:center;
         gap:2.5rem;padding:1.1rem 0 0.5rem;">
      <a class="nav-link" href="#features">Features</a>
      <a class="nav-link" href="#how">How It Works</a>
      <a class="nav-link" href="#tech">Tech Stack</a>
    </div>
    """, unsafe_allow_html=True)

with nav_r:
    tc1, tc2 = st.columns([1, 1])
    with tc1:
        st.write("")
        theme_selector("home_theme")
    with tc2:
        st.write("")
        if st.button("Sign In", key="nav_signin"):
            st.switch_page("pages/0_Sign_In.py")

st.markdown(f'<hr style="margin:0;border-color:{t["border"]};">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  HERO
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center;padding:5rem 2rem 3rem;
     background:radial-gradient(ellipse 70% 55% at 50% 25%,
       {t['accent_glow']} 0%, transparent 70%);">

  <div style="display:inline-flex;align-items:center;gap:7px;
       background:{t['card']};border:1px solid {t['border']};
       border-radius:99px;padding:5px 18px 5px 10px;
       font-size:0.72rem;font-weight:600;color:{t['text2']};
       margin-bottom:1.75rem;letter-spacing:0.06em;text-transform:uppercase;">
    <span style="width:7px;height:7px;border-radius:50%;
          background:{t['accent']};display:inline-block;"></span>
    Intelligent Extraction Engine
  </div>

  <h1 style="font-size:clamp(2.4rem,5.5vw,4rem);font-weight:800;
      line-height:1.08;letter-spacing:-0.04em;
      color:{t['text']};margin-bottom:1.25rem;">
    Extract&nbsp;
    <span style="color:{t['accent']};">Structured Data</span>
    <br>from Any Website
  </h1>

  <p style="font-size:1.05rem;color:{t['text2']};max-width:540px;
     margin:0 auto 2.5rem;line-height:1.7;">
    Enterprise-grade web scraping powered by Playwright &amp; AI.
    Automated scheduling, AI-powered cleaning, and multi-format export.
  </p>
</div>
""", unsafe_allow_html=True)

# CTA button centred
_, cta_col, _ = st.columns([3, 2, 3])
with cta_col:
    st.markdown('<div class="cta-btn">', unsafe_allow_html=True)
    if st.button("Get Started Free", key="hero_cta", use_container_width=True):
        st.switch_page("pages/0_Sign_In.py")
    st.markdown('</div>', unsafe_allow_html=True)

# Stats row
st.markdown("<br>", unsafe_allow_html=True)
s1, s2, s3, s4 = st.columns(4)
for col, num, lbl in [
    (s1, "10K+",  "URLs Processed"),
    (s2, "500K+", "Data Points"),
    (s3, "99.8%", "Uptime"),
    (s4, "<2s",   "Avg. Response"),
]:
    with col:
        st.markdown(f'<div class="stat-num">{num}</div>'
                    f'<div class="stat-lbl">{lbl}</div>', unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f'<hr style="border-color:{t["border"]};margin:0;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  FEATURES — built with native Streamlit columns
# ══════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="sec-label">What We Offer</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-title">Everything You Need to Extract Data</div>', unsafe_allow_html=True)
st.markdown('<div class="sec-sub">From static pages to complex JavaScript apps — WebScraper Pro handles it all with AI-powered cleaning.</div>', unsafe_allow_html=True)

features = [
    ("zap",       t['accent_glow'],                        t['accent'],  "Automated Extraction",
     "Just enter a URL. Playwright handles JavaScript-rendered pages, SPAs, and lazy-loaded content automatically."),
    ("bot",       "rgba(59,130,246,0.14)",                 t['blue'],    "AI-Powered Cleaning",
     "ExtractoML uses LLMs to strip noise (ads, scripts, headers) and structure raw HTML into 99% accurate data."),
    ("briefcase", "rgba(16,185,129,0.14)",                 t['green'],   "Business Insights",
     "Track e-commerce prices, monitor job listings, collect news articles — structured and ready for analysis."),
    ("monitor",   "rgba(139,92,246,0.14)",                 t['purple'],  "Professional UI",
     "Streamlit-powered real-time dashboard with live console output. Export as CSV, JSON, or Excel instantly."),
]

fc1, fc2, fc3, fc4 = st.columns(4)
for col, (ico, bg, clr, title, desc) in zip([fc1, fc2, fc3, fc4], features):
    with col:
        st.markdown(f"""
        <div class="feat-card">
          <div class="feat-icon" style="background:{bg};">
            {icon(ico, 22, clr)}
          </div>
          <div class="feat-title">{title}</div>
          <div class="feat-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(f'<hr style="border-color:{t["border"]};margin:0;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  HOW IT WORKS — native columns
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="background:{t['bg2']};padding:3.5rem 2rem 2rem;">
  <div class="sec-label">Simple Process</div>
  <div class="sec-title">How It Works</div>
  <div class="sec-sub">Three steps to get structured data from any website.</div>
</div>
""", unsafe_allow_html=True)

hw1, hw2, hw3 = st.columns(3)
for col, num, title, desc in [
    (hw1, "1", "Enter URL",            "Paste any website URL into the dashboard. Choose your category and export format."),
    (hw2, "2", "AI Extracts & Cleans", "Playwright renders the page. ExtractoML cleans with 99% accuracy using LLM processing."),
    (hw3, "3", "Download Data",        "Clean structured data ready as CSV, JSON, or Excel — ready for analysis or integration."),
]:
    with col:
        st.markdown(f"""
        <div style="text-align:center;padding:0 1rem 2.5rem;background:{t['bg2']};">
          <div class="step-circle">{num}</div>
          <div style="font-size:0.97rem;font-weight:700;color:{t['text']};margin-bottom:0.4rem;">{title}</div>
          <div style="font-size:0.83rem;color:{t['text2']};line-height:1.65;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f'<hr style="border-color:{t["border"]};margin:0;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  TECH STACK
# ══════════════════════════════════════════════════════════
tech_items = [
    ("cpu","Python"), ("layers","Playwright"), ("bot","ExtractoML / LLM"),
    ("bar-chart","Streamlit"), ("database","Pandas"), ("file-text","CSV / JSON / Excel"),
    ("shield","Proxy Support"), ("zap","Async Processing"),
]
badges = "".join(
    f'<span class="tech-badge">{icon(ic,14,t["accent"])} {lbl}</span>'
    for ic, lbl in tech_items
)
st.markdown(f"""
<div style="padding:3.5rem 2rem;text-align:center;">
  <div class="sec-label">Tech Stack</div>
  <div class="sec-title">Built with Modern Tools</div>
  <div style="margin-top:1.5rem;">{badges}</div>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<hr style="border-color:{t["border"]};margin:0;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  CTA BANNER
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="text-align:center;padding:4rem 2rem;background:{t['bg2']};">
  <div style="font-size:2rem;font-weight:800;letter-spacing:-0.04em;
       color:{t['text']};margin-bottom:0.75rem;">Ready to Start Scraping?</div>
  <div style="color:{t['text2']};margin-bottom:2rem;font-size:0.95rem;">
    Join thousands of developers using WebScraper Pro to automate data collection.</div>
</div>
""", unsafe_allow_html=True)
_, cta2, _ = st.columns([3, 2, 3])
with cta2:
    st.markdown('<div class="cta-btn">', unsafe_allow_html=True)
    if st.button("Launch Dashboard", key="cta2_btn", use_container_width=True):
        st.switch_page("pages/0_Sign_In.py")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(f'<hr style="border-color:{t["border"]};margin:0;">', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════
st.markdown(f"""
<div style="padding:1.75rem 3rem;display:flex;align-items:center;
     justify-content:space-between;flex-wrap:wrap;gap:1rem;">
  <div style="display:flex;align-items:center;gap:8px;font-weight:700;
       font-size:0.9rem;color:{t['text']};">
    {icon('globe',15,t['accent'])} WebScraper Pro
  </div>
  <div style="font-size:0.78rem;color:{t['muted']};">
    &copy; 2026 WebScraper Pro &middot; Powered by Playwright &amp; AI
  </div>
</div>
""", unsafe_allow_html=True)