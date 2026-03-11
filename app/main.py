import streamlit as st

st.set_page_config(
    page_title="WebScraper | Intelligent Data Extraction",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

:root {
    --surface:#08090d; --card:#0d1117; --border:rgba(255,255,255,0.07);
    --accent:#00e5ff; --accent2:#7b61ff; --accent3:#00ff9d;
    --text:#c8d6e5; --muted:#4a5a6a;
}

html,body,[data-testid="stAppViewContainer"],.stApp {
    background:var(--surface) !important;
    font-family:'DM Sans',sans-serif !important;
    color:var(--text) !important;
    overflow-x:hidden;
}

#MainMenu,footer,header,[data-testid="stSidebarNav"],[data-testid="stSidebar"],
[data-testid="stToolbar"],.stDeployButton { display:none !important; }

.stApp>div { padding:0 !important; }
[data-testid="stAppViewBlockContainer"] { padding:0 !important; max-width:100% !important; }
.block-container { padding:0 !important; max-width:100% !important; }
[data-testid="stVerticalBlock"]>div:empty { display:none !important; }

/* aurora */
.aurora { position:fixed; border-radius:50%; filter:blur(110px); pointer-events:none; z-index:0; }
.a1 { width:550px;height:550px;top:-120px;left:-80px;background:radial-gradient(circle,rgba(0,229,255,.1),transparent 70%);animation:drift 22s ease-in-out infinite alternate; }
.a2 { width:450px;height:450px;bottom:-60px;right:-60px;background:radial-gradient(circle,rgba(123,97,255,.12),transparent 70%);animation:drift 28s ease-in-out infinite alternate-reverse; }
@keyframes drift{0%{transform:translate(0,0)}100%{transform:translate(28px,-22px)}}
[data-testid="stVerticalBlock"]>div { position:relative; z-index:1; }

/* NAV */
.nav {
    display:flex; align-items:center; justify-content:space-between;
    padding:14px 48px;
    background:rgba(8,9,13,.92); backdrop-filter:blur(20px);
    border-bottom:1px solid var(--border);
    position:sticky; top:0; z-index:999;
    animation:slideDown .6s cubic-bezier(.22,1,.36,1) both;
}
@keyframes slideDown{from{opacity:0;transform:translateY(-18px)}to{opacity:1;transform:none}}
.nav-logo { display:flex;align-items:center;gap:10px;font-family:'Syne',sans-serif;font-size:1.2rem;font-weight:800;color:#fff; }
.nav-logo-icon { width:34px;height:34px;border-radius:9px;background:linear-gradient(135deg,var(--accent),var(--accent2));display:flex;align-items:center;justify-content:center;font-size:1rem; }
.nav-logo em { font-style:normal;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
.nav-right { display:flex;align-items:center;gap:10px; }
.nav-link { color:var(--text);text-decoration:none;font-size:.88rem;font-weight:500;padding:7px 16px;border-radius:8px;border:1px solid transparent;transition:all .2s ease; }
.nav-link:hover { background:rgba(255,255,255,.06);border-color:var(--border);color:#fff; }

/* HERO */
.hero { display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:80px 40px 60px;animation:fadeUp .7s cubic-bezier(.22,1,.36,1) .1s both; }
@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
.hero-badge { display:inline-flex;align-items:center;gap:6px;background:rgba(0,229,255,.07);border:1px solid rgba(0,229,255,.18);color:var(--accent);border-radius:20px;padding:5px 13px;font-size:.72rem;font-weight:600;letter-spacing:.8px;text-transform:uppercase;margin-bottom:22px; }
.hero h1 { font-family:'Syne',sans-serif;font-size:2.6rem;font-weight:800;line-height:1.12;letter-spacing:-.5px;color:#fff;margin-bottom:16px;max-width:600px; }
.hero h1 .grad { background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
.hero-sub { font-size:.95rem;color:var(--muted);max-width:440px;line-height:1.7;margin-bottom:34px; }

/* BUTTONS */
div.stButton>button {
    font-family:'DM Sans',sans-serif !important; font-weight:700 !important;
    border-radius:10px !important; border:none !important;
    transition:all .3s cubic-bezier(.22,1,.36,1) !important;
}
div.stButton>button {
    background:linear-gradient(135deg,var(--accent),var(--accent2)) !important;
    color:#000 !important; padding:13px 32px !important; font-size:.95rem !important;
    box-shadow:0 0 28px rgba(0,229,255,.2) !important;
}
div.stButton>button:hover { transform:translateY(-2px) scale(1.01) !important; box-shadow:0 8px 28px rgba(0,229,255,.38) !important; }

/* STATS */
.stats-row { display:flex;justify-content:center;gap:48px;padding:24px 40px;border-top:1px solid var(--border);border-bottom:1px solid var(--border);animation:fadeUp .7s .25s both; }
.stat { text-align:center; }
.stat-num { font-family:'Syne',sans-serif;font-size:1.8rem;font-weight:800;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
.stat-lbl { font-size:.72rem;color:var(--muted);margin-top:2px;letter-spacing:.3px; }

/* FEATURES */
.features { display:grid;grid-template-columns:repeat(3,1fr);gap:16px;padding:40px 48px;animation:fadeUp .7s .35s both; }
.feat-card { background:var(--card);border:1px solid var(--border);border-radius:16px;padding:24px;position:relative;overflow:hidden;transition:all .3s ease; }
.feat-card::before { content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--fg,linear-gradient(90deg,var(--accent),transparent)); }
.feat-card:nth-child(2){--fg:linear-gradient(90deg,var(--accent2),transparent)}
.feat-card:nth-child(3){--fg:linear-gradient(90deg,var(--accent3),transparent)}
.feat-card:hover { transform:translateY(-5px);border-color:rgba(0,229,255,.15);box-shadow:0 12px 32px rgba(0,0,0,.3); }
.feat-icon { font-size:1.5rem;margin-bottom:12px; }
.feat-card h3 { font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;color:#fff;margin-bottom:8px; }
.feat-card p { font-size:.82rem;color:var(--muted);line-height:1.6; }

/* CTA */
.cta-strip { margin:0 48px 40px;background:linear-gradient(135deg,rgba(0,229,255,.07),rgba(123,97,255,.07));border:1px solid rgba(0,229,255,.12);border-radius:18px;padding:32px 36px;display:flex;align-items:center;justify-content:space-between;animation:fadeUp .7s .45s both; }
.cta-strip h2 { font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:#fff;margin-bottom:4px; }
.cta-strip p { font-size:.83rem;color:var(--muted); }

/* FOOTER */
.footer { padding:18px 48px;border-top:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;color:var(--muted);font-size:.78rem; }
.footer-logo { font-family:'Syne',sans-serif;font-weight:800;color:#fff;font-size:.92rem; }
.footer-logo em { font-style:normal;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text; }
.footer a { color:var(--muted);text-decoration:none; }
.footer a:hover { color:var(--text); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="aurora a1"></div><div class="aurora a2"></div>', unsafe_allow_html=True)

# NAV
st.markdown("""
<nav class="nav">
    <div class="nav-logo"><div class="nav-logo-icon">🕷️</div>Web<em>Scraper</em></div>
    <div class="nav-right">
        <a class="nav-link" href="#">Features</a>
        <a class="nav-link" href="#">Docs</a>
        <a class="nav-link" href="#">Pricing</a>
    </div>
</nav>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero">
    <div class="hero-badge">⚡ Powered by Playwright & AI</div>
    <h1>Extract Any Web Data<br><span class="grad">In Seconds</span></h1>
    <p class="hero-sub">WebScraper turns any website into a structured, clean dataset in seconds. No code required.</p>
</div>
""", unsafe_allow_html=True)

_,col,_ = st.columns([2.6,1,2.6])
with col:
    if st.button("🚀  Get Started Free", use_container_width=True):
        st.switch_page("pages/1_Login.py")

# STATS
st.markdown("""
<div class="stats-row">
    <div class="stat"><div class="stat-num">99.2%</div><div class="stat-lbl">Accuracy Rate</div></div>
    <div class="stat"><div class="stat-num">&lt;3s</div><div class="stat-lbl">Avg Scrape Time</div></div>
    <div class="stat"><div class="stat-num">50+</div><div class="stat-lbl">Items Per Page</div></div>
    <div class="stat"><div class="stat-num">∞</div><div class="stat-lbl">Scalable</div></div>
</div>
""", unsafe_allow_html=True)

# FEATURES
st.markdown("""
<div class="features">
    <div class="feat-card">
        <div class="feat-icon">⚡</div>
        <h3>Instant Extraction</h3>
        <p>Headless Chromium handles JavaScript-heavy pages with a 1.5s wait for full render.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon">🧠</div>
        <h3>Smart Parsing</h3>
        <p>15+ CSS selectors automatically detect headings, titles, products and article content.</p>
    </div>
    <div class="feat-card">
        <div class="feat-icon">📊</div>
        <h3>Export Anywhere</h3>
        <p>Download your data instantly as CSV, JSON, or Excel with one click.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# CTA
st.markdown("""
<div class="cta-strip">
    <div>
        <h2>Ready to start scraping?</h2>
        <p>Join thousands of developers and analysts who trust WebScraper.</p>
    </div>
</div>
""", unsafe_allow_html=True)

_,col2,_ = st.columns([3.2,1,3.2])
with col2:
    if st.button("→  Sign Up Free", use_container_width=True, key="cta2"):
        st.switch_page("pages/1_Login.py")

st.markdown("<br>", unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="footer">
    <div class="footer-logo">Web<em>Scraper</em></div>
    <div>© 2025 WebScraper. All rights reserved.</div>
    <div style="display:flex;gap:16px;"><a href="#">Privacy</a><a href="#">Terms</a><a href="#">Docs</a></div>
</div>
""", unsafe_allow_html=True)
