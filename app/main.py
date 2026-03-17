import streamlit as st
import os, sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from theme_config import init_theme, get_theme_vars, get_bg_css, render_theme_toggle_css

st.set_page_config(
    page_title="WebScraper | Intelligent Data Extraction",
    layout="wide",
    initial_sidebar_state="collapsed"
)

theme = init_theme()
tv = get_theme_vars(theme)
bg_style = get_bg_css(tv, theme)

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}

:root {{
    --surface:{tv['surface']}; --card:{tv['card']}; --border:{tv['border']};
    --accent:{tv['accent']}; --accent2:{tv['accent2']}; --accent3:{tv['accent3']};
    --text:{tv['text']}; --muted:{tv['muted']}; --heading:{tv['heading']};
}}

html,body,[data-testid="stAppViewContainer"],.stApp {{
    {bg_style}
    font-family:'Inter',sans-serif !important;
    color:var(--text) !important;
    overflow-x:hidden;
}}

#MainMenu,footer,header,[data-testid="stSidebarNav"],[data-testid="stSidebar"],
[data-testid="stToolbar"],.stDeployButton {{ display:none !important; }}

.stApp>div {{ padding:0 !important; }}
[data-testid="stAppViewBlockContainer"] {{ padding:0 !important; max-width:100% !important; }}
.block-container {{ padding:0 !important; max-width:100% !important; }}
[data-testid="stVerticalBlock"]>div:empty {{ display:none !important; }}

/* subtle aurora */
.aurora {{ position:fixed; border-radius:50%; filter:blur(120px); pointer-events:none; z-index:0; opacity:.6; }}
.a1 {{ width:500px;height:500px;top:-150px;left:-100px;background:radial-gradient(circle,{tv['aurora1']},transparent 70%);animation:drift 25s ease-in-out infinite alternate; }}
.a2 {{ width:400px;height:400px;bottom:-80px;right:-80px;background:radial-gradient(circle,{tv['aurora2']},transparent 70%);animation:drift 30s ease-in-out infinite alternate-reverse; }}
@keyframes drift{{0%{{transform:translate(0,0)}}100%{{transform:translate(30px,-25px)}}}}
[data-testid="stVerticalBlock"]>div {{ position:relative; z-index:1; }}

/* NAV */
.nav {{
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 48px;
    background:{tv['nav_bg']}; backdrop-filter:blur(24px) saturate(1.2);
    border-bottom:1px solid {tv['border']};
    position:sticky; top:0; z-index:999;
    animation:slideDown .5s cubic-bezier(.22,1,.36,1) both;
}}
@keyframes slideDown{{from{{opacity:0;transform:translateY(-16px)}}to{{opacity:1;transform:none}}}}
.nav-logo {{ display:flex;align-items:center;gap:10px;font-family:'Inter',sans-serif;font-size:1.15rem;font-weight:800;color:{tv['heading']}; }}
.nav-logo-icon {{ width:32px;height:32px;border-radius:8px;background:linear-gradient(135deg,{tv['accent']},{tv['accent2']});display:flex;align-items:center;justify-content:center; }}
.nav-logo-icon svg {{ width:18px;height:18px;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round; }}
.nav-logo span {{ font-weight:300;opacity:.5; }}
.nav-right {{ display:flex;align-items:center;gap:10px; }}
.nav-link {{ color:{tv['text']};text-decoration:none;font-size:.85rem;font-weight:500;padding:7px 16px;border-radius:8px;border:1px solid transparent;transition:all .2s ease; }}
.nav-link:hover {{ background:{tv['hover']};border-color:{tv['border']};color:{tv['heading']}; }}

{render_theme_toggle_css(tv)}

/* HERO */
.hero {{ display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:80px 40px 60px;animation:fadeUp .6s cubic-bezier(.22,1,.36,1) .1s both; }}
@keyframes fadeUp{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
.hero-badge {{ display:inline-flex;align-items:center;gap:6px;background:rgba({','.join(str(int(tv['accent'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},.08);border:1px solid rgba({','.join(str(int(tv['accent'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},.18);color:{tv['accent']};border-radius:20px;padding:5px 14px;font-size:.7rem;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:22px; }}
.hero h1 {{ font-family:'Inter',sans-serif;font-size:2.8rem;font-weight:900;line-height:1.1;letter-spacing:-1px;color:{tv['heading']};margin-bottom:16px;max-width:620px; }}
.hero h1 .grad {{ background:linear-gradient(135deg,{tv['accent']},{tv['accent2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }}
.hero-sub {{ font-size:.95rem;color:{tv['muted']};max-width:440px;line-height:1.7;margin-bottom:34px; }}

/* BUTTONS */
div.stButton>button {{
    font-family:'Inter',sans-serif !important; font-weight:600 !important;
    border-radius:10px !important; border:none !important;
    transition:all .25s cubic-bezier(.22,1,.36,1) !important;
}}
div.stButton>button {{
    background:linear-gradient(135deg,{tv['accent']},{tv['accent2']}) !important;
    color:#fff !important; padding:13px 32px !important; font-size:.9rem !important;
    box-shadow:0 4px 20px rgba(0,0,0,.15) !important;
}}
div.stButton>button:hover {{ transform:translateY(-2px) !important; box-shadow:0 8px 28px rgba(0,0,0,.25) !important; }}

/* STATS */
.stats-row {{ display:flex;justify-content:center;gap:48px;padding:24px 40px;border-top:1px solid {tv['border']};border-bottom:1px solid {tv['border']};animation:fadeUp .6s .2s both; }}
.stat {{ text-align:center; }}
.stat-num {{ font-family:'Inter',sans-serif;font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,{tv['accent']},{tv['accent2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }}
.stat-lbl {{ font-size:.7rem;color:{tv['muted']};margin-top:2px;letter-spacing:.5px;text-transform:uppercase; }}

/* FEATURES */
.features {{ display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:40px 48px;animation:fadeUp .6s .3s both; }}
.feat-card {{ background:{tv['card']};border:1px solid {tv['border']};border-radius:14px;padding:24px;position:relative;overflow:hidden;transition:all .25s ease; }}
.feat-card::before {{ content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--fg,linear-gradient(90deg,{tv['accent']},transparent)); }}
.feat-card:nth-child(2){{--fg:linear-gradient(90deg,{tv['accent2']},transparent)}}
.feat-card:nth-child(3){{--fg:linear-gradient(90deg,{tv['accent3']},transparent)}}
.feat-card:hover {{ transform:translateY(-4px);box-shadow:0 12px 32px rgba(0,0,0,.15); }}
.feat-icon {{ width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;margin-bottom:12px; }}
.feat-icon svg {{ width:22px;height:22px;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round; }}
.feat-icon.fi-1 {{ background:rgba({','.join(str(int(tv['accent'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},.1); }}
.feat-icon.fi-1 svg {{ stroke:{tv['accent']}; }}
.feat-icon.fi-2 {{ background:rgba({','.join(str(int(tv['accent2'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},.1); }}
.feat-icon.fi-2 svg {{ stroke:{tv['accent2']}; }}
.feat-icon.fi-3 {{ background:rgba({','.join(str(int(tv['accent3'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},.1); }}
.feat-icon.fi-3 svg {{ stroke:{tv['accent3']}; }}
.feat-card h3 {{ font-family:'Inter',sans-serif;font-size:.95rem;font-weight:700;color:{tv['heading']};margin-bottom:8px; }}
.feat-card p {{ font-size:.82rem;color:{tv['muted']};line-height:1.6; }}

/* CTA */
.cta-strip {{ margin:0 48px 40px;background:{tv['card']};border:1px solid {tv['border']};border-radius:16px;padding:32px 36px;display:flex;align-items:center;justify-content:space-between;animation:fadeUp .6s .4s both; }}
.cta-strip h2 {{ font-family:'Inter',sans-serif;font-size:1.25rem;font-weight:800;color:{tv['heading']};margin-bottom:4px; }}
.cta-strip p {{ font-size:.83rem;color:{tv['muted']}; }}

/* FOOTER */
.footer {{ padding:18px 48px;border-top:1px solid {tv['border']};display:flex;align-items:center;justify-content:space-between;color:{tv['muted']};font-size:.78rem; }}
.footer-logo {{ font-family:'Inter',sans-serif;font-weight:800;color:{tv['heading']};font-size:.9rem; }}
.footer-logo em {{ font-style:normal;background:linear-gradient(135deg,{tv['accent']},{tv['accent2']});-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }}

/* Theme switcher button overrides */
.theme-switch-row div.stButton>button {{
    background:{tv['input_bg']} !important;
    color:{tv['muted']} !important;
    padding:6px 12px !important;
    font-size:.75rem !important;
    font-weight:600 !important;
    border:1px solid {tv['border']} !important;
    box-shadow:none !important;
    letter-spacing:.3px !important;
}}
.theme-switch-row div.stButton>button:hover {{
    background:{tv['hover']} !important;
    color:{tv['heading']} !important;
    transform:none !important;
    box-shadow:none !important;
}}
</style>
""", unsafe_allow_html=True)

# ── AURORA ──
st.markdown('<div class="aurora a1"></div><div class="aurora a2"></div>', unsafe_allow_html=True)

# ── NAV ──
st.markdown(f"""
<div class="nav">
    <div class="nav-logo">
        <div class="nav-logo-icon">
            <svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>
        </div>
        Web<em>Scraper</em> <span>Pro</span>
    </div>
    <div class="nav-right">
        <a class="nav-link" href="#">Features</a>
        <a class="nav-link" href="#">Docs</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ── THEME SWITCHER ──
st.markdown('<div class="theme-switch-row" style="padding:8px 48px 0;display:flex;justify-content:flex-end">', unsafe_allow_html=True)
cols = st.columns([5,1,1,1])
changed = False
with cols[1]:
    if st.button("◼ Dark" if theme=="dark" else "Dark", key="m_dark", use_container_width=True):
        st.session_state["theme"]="dark"; changed=True
with cols[2]:
    if st.button("◻ Light" if theme=="light" else "Light", key="m_light", use_container_width=True):
        st.session_state["theme"]="light"; changed=True
with cols[3]:
    if st.button("◈ Vivid" if theme=="multi" else "Vivid", key="m_multi", use_container_width=True):
        st.session_state["theme"]="multi"; changed=True
if changed:
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

# ── HERO ──
st.markdown(f"""
<div class="hero">
    <div class="hero-badge">
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4"/></svg>
        Intelligent Extraction Engine
    </div>
    <h1>Extract <span class="grad">Structured Data</span> from Any Website</h1>
    <p class="hero-sub">Enterprise-grade web scraping with AI-powered data extraction, automated scheduling, and multi-format export.</p>
</div>
""", unsafe_allow_html=True)

if st.button("Get Started →", key="hero_cta"):
    st.switch_page("pages/1_Login.py")

# ── STATS ──
st.markdown("""
<div class="stats-row">
    <div class="stat"><div class="stat-num">10K+</div><div class="stat-lbl">URLs Processed</div></div>
    <div class="stat"><div class="stat-num">500K+</div><div class="stat-lbl">Data Points</div></div>
    <div class="stat"><div class="stat-num">99.8%</div><div class="stat-lbl">Uptime</div></div>
    <div class="stat"><div class="stat-num">&lt;2s</div><div class="stat-lbl">Avg. Response</div></div>
</div>
""", unsafe_allow_html=True)

# ── FEATURES ──
st.markdown(f"""
<div class="features">
    <div class="feat-card">
        <div class="feat-icon fi-1">
            <svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </div>
        <h3>Smart Extraction</h3>
        <p>Automatically detect and extract structured data from complex web pages using headless browser technology.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon fi-2">
            <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <h3>AI Analysis</h3>
        <p>Leverage LLM-powered analysis to transform raw data into actionable insights with natural language queries.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon fi-3">
            <svg viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <h3>Automated Scheduling</h3>
        <p>Configure recurring scrape jobs with flexible intervals, notifications, and automatic data export.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── CTA ──
st.markdown("""
<div class="cta-strip">
    <div>
        <h2>Ready to extract data at scale?</h2>
        <p>Start your first scrape in under 30 seconds.</p>
    </div>
</div>
""", unsafe_allow_html=True)
if st.button("Launch Dashboard →", key="cta_btn"):
    st.switch_page("pages/1_Login.py")

# ── FOOTER ──
st.markdown("""
<div class="footer">
    <div class="footer-logo">Web<em>Scraper</em></div>
    <div>© 2025 WebScraper. All rights reserved.</div>
</div>
""", unsafe_allow_html=True)
