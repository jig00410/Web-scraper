import streamlit as st
import pandas as pd
import json, io, os, sys
from datetime import datetime

current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from services.scraper_service import scrape_website_data
except Exception:
    def scrape_website_data(url):
        return {"success":False,"error":"Scraper not available. Run: pip install -r requirements.txt && playwright install chromium","title":"","headings":[]}

try:
    from database.firebase_config import save_scrape_to_history
    db_enabled = True
except Exception:
    db_enabled = False
    def save_scrape_to_history(*a,**kw): return False

st.set_page_config(page_title="Dashboard | WebScraper", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("authenticated"):
    st.switch_page("main.py")

for k,v in [("scrape_history",[]),("last_df",None),("scraper_df",None),("total_rows",0),("total_jobs",0)]:
    if k not in st.session_state: st.session_state[k] = v

user_name  = st.session_state.get("user_name","User")
user_email = st.session_state.get("user_email","")
av = (user_name[0] if user_name else "U").upper()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');
*,*::before,*::after{margin:0;padding:0;box-sizing:border-box}
:root{
    --surface:#08090d; --card:#0d1117; --card2:#111820;
    --border:rgba(255,255,255,.07); --border2:rgba(255,255,255,.12);
    --accent:#00e5ff; --accent2:#7b61ff; --accent3:#00ff9d;
    --text:#c8d6e5; --muted:#4a5a6a; --danger:#ff4d6d;
}
html,body,[data-testid="stAppViewContainer"],.stApp{
    background:var(--surface) !important;
    font-family:'DM Sans',sans-serif !important;
    color:var(--text) !important;
}
#MainMenu,footer,header,[data-testid="stToolbar"],.stDeployButton{display:none !important}

/* SIDEBAR */
[data-testid="stSidebar"]{background:var(--card) !important;border-right:1px solid var(--border) !important;}
[data-testid="stSidebarContent"]{padding:0 !important}
[data-testid="stRadio"]>div{gap:2px !important}
[data-testid="stRadio"] label{
    background:transparent !important;border:none !important;border-radius:8px !important;
    padding:10px 16px !important;color:var(--muted) !important;font-size:.88rem !important;
    font-family:'DM Sans',sans-serif !important;font-weight:500 !important;
    transition:all .2s ease !important;cursor:pointer !important;
}
[data-testid="stRadio"] label:hover{background:rgba(255,255,255,.05) !important;color:var(--text) !important;}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked){
    background:rgba(0,229,255,.07) !important;color:var(--accent) !important;
    border-left:2px solid var(--accent) !important;
}
[data-testid="stRadio"] [data-baseweb="radio"]>div:first-child{display:none !important}

/* INPUT */
.stTextInput label,.stTextInput>label{display:none !important}
.stTextInput>div>div>input{
    background:rgba(255,255,255,.05) !important;border:1px solid var(--border) !important;
    border-radius:10px !important;color:#fff !important;padding:12px 15px !important;
    font-size:.9rem !important;font-family:'DM Sans',sans-serif !important;
    transition:all .2s ease !important;caret-color:var(--accent) !important;
}
.stTextInput>div>div>input::placeholder{color:var(--muted) !important}
.stTextInput>div>div>input:focus{
    background:rgba(0,229,255,.05) !important;
    border-color:rgba(0,229,255,.4) !important;
    box-shadow:0 0 0 3px rgba(0,229,255,.07) !important;outline:none !important;
}

/* BUTTONS */
div.stButton>button{
    font-family:'DM Sans',sans-serif !important;font-weight:700 !important;
    border-radius:9px !important;border:none !important;
    transition:all .3s cubic-bezier(.22,1,.36,1) !important;font-size:.88rem !important;
}
div.stButton>button[kind="primary"]{
    background:linear-gradient(135deg,var(--accent),var(--accent2)) !important;
    color:#000 !important;padding:12px 20px !important;
    box-shadow:0 0 20px rgba(0,229,255,.18) !important;
}
div.stButton>button[kind="primary"]:hover{transform:translateY(-2px) !important;box-shadow:0 6px 22px rgba(0,229,255,.35) !important;}
div.stButton>button[kind="secondary"]{
    background:rgba(255,255,255,.05) !important;color:var(--text) !important;
    border:1px solid var(--border) !important;padding:10px 16px !important;
}
div.stButton>button[kind="secondary"]:hover{background:rgba(255,255,255,.09) !important;transform:translateY(-1px) !important;}

/* DOWNLOAD */
div.stDownloadButton>button{
    font-family:'DM Sans',sans-serif !important;font-weight:600 !important;
    border-radius:9px !important;background:var(--card2) !important;
    color:var(--text) !important;border:1px solid var(--border) !important;
    padding:10px 12px !important;font-size:.83rem !important;
    transition:all .2s ease !important;width:100% !important;
}
div.stDownloadButton>button:hover{
    background:rgba(0,229,255,.09) !important;
    border-color:rgba(0,229,255,.3) !important;color:var(--accent) !important;
    transform:translateY(-1px) !important;
}

/* DATAFRAME */
[data-testid="stDataFrame"]{border:1px solid var(--border) !important;border-radius:12px !important;overflow:hidden !important;}

/* ALERTS */
.stAlert{border-radius:10px !important}
[data-testid="stSuccess"]{background:rgba(0,255,157,.07) !important;border-color:rgba(0,255,157,.2) !important}
[data-testid="stError"]{background:rgba(255,77,109,.07) !important;border-color:rgba(255,77,109,.2) !important}
[data-testid="stWarning"]{background:rgba(255,179,71,.07) !important;border-color:rgba(255,179,71,.2) !important}
[data-testid="stInfo"]{background:rgba(0,229,255,.07) !important;border-color:rgba(0,229,255,.18) !important}

/* TOGGLE */
[data-testid="stToggle"] label{color:var(--text) !important;font-family:'DM Sans',sans-serif !important}

/* SIDEBAR PROFILE */
.sb-profile{padding:22px 16px 16px;border-bottom:1px solid var(--border);margin-bottom:6px}
.sb-avatar{
    width:44px;height:44px;border-radius:11px;
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    display:flex;align-items:center;justify-content:center;
    font-family:'Syne',sans-serif;font-size:1.1rem;font-weight:800;
    color:#000;margin-bottom:10px;
}
.sb-name{font-family:'Syne',sans-serif;font-weight:700;color:#fff;font-size:.92rem}
.sb-email{color:var(--muted);font-size:.75rem;margin-top:2px;word-break:break-all}
.sb-badge{
    display:inline-flex;align-items:center;gap:4px;
    background:rgba(0,255,157,.07);border:1px solid rgba(0,255,157,.18);
    color:var(--accent3);border-radius:20px;padding:3px 9px;
    font-size:.68rem;font-weight:600;margin-top:8px;letter-spacing:.3px;
}
.sb-badge::before{content:'';width:5px;height:5px;border-radius:50%;background:var(--accent3);box-shadow:0 0 5px var(--accent3)}
.sb-section{padding:0 10px;margin:10px 0 4px}
.sb-section-lbl{font-size:.62rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);padding:0 4px}

/* PAGE */
.pg-header{
    display:flex;align-items:flex-end;justify-content:space-between;
    margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border);
}
.pg-title{font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:#fff;letter-spacing:-.5px}
.pg-sub{color:var(--muted);font-size:.82rem;margin-top:3px}
.live-dot{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(0,255,157,.07);border:1px solid rgba(0,255,157,.18);
    color:var(--accent3);border-radius:7px;padding:5px 11px;font-size:.73rem;font-family:'DM Mono',monospace;
}
.live-dot::before{content:'';width:5px;height:5px;border-radius:50%;background:var(--accent3);box-shadow:0 0 5px var(--accent3)}

/* METRIC CARDS */
.m-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.m-card{
    background:var(--card);border:1px solid var(--border);border-radius:14px;
    padding:20px 18px;position:relative;overflow:hidden;
    transition:all .3s ease;
}
.m-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--mg,linear-gradient(90deg,var(--accent),transparent))}
.m-card:hover{transform:translateY(-4px);border-color:rgba(0,229,255,.15)}
.m-card:nth-child(2){--mg:linear-gradient(90deg,var(--accent2),transparent)}
.m-card:nth-child(3){--mg:linear-gradient(90deg,var(--accent3),transparent)}
.m-lbl{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-bottom:7px}
.m-val{font-family:'Syne',sans-serif;font-size:1.9rem;font-weight:800;color:#fff;letter-spacing:-1px;line-height:1}
.m-sub{font-size:.72rem;color:var(--muted);margin-top:4px}

/* PANEL */
.panel{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px}
.panel+.panel{margin-top:14px}
.panel-ttl{
    font-family:'Syne',sans-serif;font-size:.95rem;font-weight:700;
    color:#fff;margin-bottom:14px;display:flex;align-items:center;gap:7px;
}
.panel-ttl .ac{color:var(--accent)}

/* SCHEMA TABLE */
.stbl{width:100%;border-collapse:collapse;font-size:.82rem}
.stbl th{
    background:rgba(0,229,255,.05);color:var(--accent);padding:8px 12px;
    text-align:left;font-size:.7rem;letter-spacing:.8px;text-transform:uppercase;
    border-bottom:1px solid var(--border);font-weight:600;
}
.stbl td{padding:8px 12px;border-bottom:1px solid rgba(255,255,255,.04);color:var(--text);font-family:'DM Mono',monospace;font-size:.78rem}
.stbl tr:last-child td{border:none}
.stbl tr:hover td{background:rgba(255,255,255,.02)}

/* ACTIVITY */
.act-item{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.04)}
.act-item:last-child{border:none;padding-bottom:0}
.act-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--accent);box-shadow:0 0 6px var(--accent)}
.act-url{font-size:.82rem;color:var(--text);font-family:'DM Mono',monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:280px}
.act-meta{font-size:.7rem;color:var(--muted);margin-top:1px}
.act-ok{font-size:.72rem;font-weight:600;color:var(--accent3);white-space:nowrap}

/* EMPTY */
.empty{text-align:center;padding:40px 20px;color:var(--muted)}
.empty-icon{font-size:2rem;margin-bottom:10px}
.empty-txt{font-size:.85rem;line-height:1.6}

/* LOGOUT */
.logout-wrap>div>button{
    background:rgba(255,77,109,.06) !important;color:var(--danger) !important;
    border:1px solid rgba(255,77,109,.15) !important;font-size:.84rem !important;padding:9px !important;
}
hr{border-color:var(--border) !important;margin:14px 0 !important}
</style>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown(f"""
    <div class="sb-profile">
        <div class="sb-avatar">{av}</div>
        <div class="sb-name">{user_name}</div>
        <div class="sb-email">{user_email or "demo@webscraper.io"}</div>
        <div class="sb-badge">Active</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="sb-section"><span class="sb-section-lbl">Menu</span></div>', unsafe_allow_html=True)
    menu = st.radio("nav", ["🏠  Dashboard","🕷️  Scraper","📋  History","🔑  API Keys","⚙️  Settings"], label_visibility="collapsed", key="nav_menu")
    st.markdown("<br>"*3, unsafe_allow_html=True)
    st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
    if st.button("🚪  Sign Out", use_container_width=True, key="logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.switch_page("main.py")
    st.markdown('</div>', unsafe_allow_html=True)

page = menu.split("  ",1)[1].strip()

# ═══ DASHBOARD ═══
if page == "Dashboard":
    st.markdown(f"""
    <div class="pg-header">
        <div><div class="pg-title">Dashboard</div><div class="pg-sub">Your scraping overview</div></div>
        <div class="live-dot">Live</div>
    </div>
    <div class="m-grid">
        <div class="m-card"><div class="m-lbl">Data Accuracy %</div><div class="m-val">98</div><div class="m-sub">↑ +0.4% this week</div></div>
        <div class="m-card"><div class="m-lbl">Total Rows Extracted</div><div class="m-val">{st.session_state['total_rows']:,}</div><div class="m-sub">{st.session_state['total_jobs']} job(s) this session</div></div>
        <div class="m-card"><div class="m-lbl">Proxy Status</div><div class="m-val" style="color:var(--accent3);font-size:1.3rem;">● Active</div><div class="m-sub">Headless Chromium ready</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_main, col_side = st.columns([1.6,1], gap="large")

    with col_main:
        st.markdown('<div class="panel"><div class="panel-ttl">Enter Website URL to Scrape</div>', unsafe_allow_html=True)
        url = st.text_input("u", placeholder="https://quotes.toscrape.com", key="dash_url")
        if st.button("⚙️  Submit", type="primary", use_container_width=True, key="dash_go"):
            if url.strip():
                with st.spinner("🔄 Extracting…"):
                    r = scrape_website_data(url.strip())
                if r["success"]:
                    df = pd.DataFrame(r["headings"], columns=["Scraped Content"])
                    st.session_state.update({"last_df":df,"last_title":r["title"],"total_rows":st.session_state["total_rows"]+len(df),"total_jobs":st.session_state["total_jobs"]+1})
                    st.session_state["scrape_history"].insert(0,{"url":url.strip(),"title":r["title"],"rows":len(df),"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
                    if db_enabled: save_scrape_to_history(user_email, url.strip(), r["title"], len(df))
                    st.success(f"✅ Extracted **{len(df)} items** — {r['title']}")
                    st.dataframe(df, use_container_width=True, height=260)
                else:
                    st.error("❌ " + r["error"])
            else:
                st.warning("Please enter a URL.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown("""
        <div class="panel"><div class="panel-ttl">Data Schema</div>
        <table class="stbl">
            <tr><th>Field</th><th>Sample Data</th></tr>
            <tr><td>Product Name</td><td>Text</td></tr>
            <tr><td>Price</td><td>Number</td></tr>
            <tr><td>Description</td><td>29.99</td></tr>
        </table></div>
        """, unsafe_allow_html=True)

        if st.session_state["last_df"] is not None:
            df = st.session_state["last_df"]
            st.markdown("<br>", unsafe_allow_html=True)
            c1,c2,c3 = st.columns(3)
            with c1:
                st.download_button("Download as CSV", df.to_csv(index=False).encode(), "data.csv","text/csv", use_container_width=True, key="dl_csv_d")
            with c2:
                st.download_button("JSON", json.dumps(df.to_dict("records"),indent=2).encode(), "data.json","application/json", use_container_width=True, key="dl_json_d")
            with c3:
                buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
                st.download_button("Excel", buf.getvalue(),"data.xlsx", use_container_width=True, key="dl_xlsx_d")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-ttl">🕐 Recent Activity</div>', unsafe_allow_html=True)
    hist = st.session_state["scrape_history"]
    colors=["var(--accent)","var(--accent2)","var(--accent3)"]
    if hist:
        for i,item in enumerate(hist[:5]):
            c=colors[i%3]
            st.markdown(f'<div class="act-item"><div class="act-dot" style="background:{c};box-shadow:0 0 6px {c}"></div><div style="flex:1;min-width:0"><div class="act-url">{item["url"]}</div><div class="act-meta">{item["rows"]} rows · {item["time"]}</div></div><div class="act-ok">✓ Done</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty"><div class="empty-icon">🕷️</div><div class="empty-txt">No activity yet. Run your first scrape above!</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══ SCRAPER ═══
elif page == "Scraper":
    st.markdown('<div class="pg-header"><div><div class="pg-title">Web Scraper</div><div class="pg-sub">Extract data from any URL</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-ttl">🔍 Target URL</div>', unsafe_allow_html=True)
    url = st.text_input("su", placeholder="https://quotes.toscrape.com", key="scraper_url")
    c1,c2 = st.columns([2,1])
    with c1:
        run = st.button("⚙️  Run Extraction", type="primary", use_container_width=True, key="run_btn")
    with c2:
        if st.button("🗑  Clear", type="secondary", use_container_width=True, key="clear_btn"):
            st.session_state["scraper_df"]=None; st.rerun()
    if run:
        if url.strip():
            with st.spinner("🔄 Launching browser…"):
                r = scrape_website_data(url.strip())
            if r["success"]:
                df=pd.DataFrame(r["headings"],columns=["Scraped Content"])
                st.session_state.update({"scraper_df":df,"scraper_title":r["title"],"total_rows":st.session_state["total_rows"]+len(df),"total_jobs":st.session_state["total_jobs"]+1})
                st.session_state["scrape_history"].insert(0,{"url":url.strip(),"title":r["title"],"rows":len(df),"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
                if db_enabled: save_scrape_to_history(user_email,url.strip(),r["title"],len(df))
                st.success(f"✅ **{r['title']}** — {len(df)} items extracted")
            else:
                st.error("❌ "+r["error"])
        else:
            st.warning("Enter a URL.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["scraper_df"] is not None:
        df=st.session_state["scraper_df"]
        st.markdown(f'<br><div class="panel"><div class="panel-ttl">📊 Results — <span class="ac">{len(df)} rows</span></div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="panel"><div class="panel-ttl">📥 Export</div>', unsafe_allow_html=True)
        c1,c2,c3,_=st.columns([1,1,1,1.5])
        with c1:
            st.download_button("⬇ CSV",df.to_csv(index=False).encode(),"data.csv","text/csv",use_container_width=True,key="sc_csv")
        with c2:
            st.download_button("⬇ JSON",json.dumps(df.to_dict("records"),indent=2).encode(),"data.json",use_container_width=True,key="sc_json")
        with c3:
            buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
            st.download_button("⬇ Excel",buf.getvalue(),"data.xlsx",use_container_width=True,key="sc_xlsx")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<br><div class="panel"><div class="empty"><div class="empty-icon">🌐</div><div class="empty-txt">Enter a URL above and click <b>Run Extraction</b><br>Try: <code>https://quotes.toscrape.com</code></div></div></div>', unsafe_allow_html=True)

# ═══ HISTORY ═══
elif page == "History":
    st.markdown('<div class="pg-header"><div><div class="pg-title">Scrape History</div><div class="pg-sub">All extraction jobs this session</div></div></div>', unsafe_allow_html=True)
    _,cb=st.columns([3,1])
    with cb:
        if st.session_state["scrape_history"] and st.button("🗑  Clear",type="secondary",use_container_width=True):
            st.session_state["scrape_history"]=[]; st.rerun()
    hist=st.session_state["scrape_history"]
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if hist:
        for i,item in enumerate(hist):
            c=colors[i%3]
            st.markdown(f'<div class="act-item"><div class="act-dot" style="background:{c};box-shadow:0 0 6px {c}"></div><div style="flex:1;min-width:0"><div class="act-url">{item["url"]}</div><div class="act-meta">{item.get("title","")[:50]} · {item["rows"]} rows · {item["time"]}</div></div><div class="act-ok">✓ Done</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty"><div class="empty-icon">📋</div><div class="empty-txt">No history yet. Scrape some URLs!</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if not db_enabled: st.info("💡 Connect Firebase to persist history across sessions.")

# ═══ API KEYS ═══
elif page == "API Keys":
    st.markdown('<div class="pg-header"><div><div class="pg-title">API Keys</div><div class="pg-sub">Manage your credentials</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-ttl">🔑 Active Keys</div><table class="stbl"><tr><th>Name</th><th>Key</th><th>Created</th><th>Status</th></tr><tr><td>Default</td><td style="font-family:\'DM Mono\',monospace">ws_live_••••••••3f2a</td><td>2025-06-01</td><td style="color:var(--accent3);font-weight:600">● Active</td></tr></table></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("＋ Generate New Key", type="primary"):
        st.info("API key generation requires backend integration.")

# ═══ SETTINGS ═══
elif page == "Settings":
    st.markdown('<div class="pg-header"><div><div class="pg-title">Settings</div><div class="pg-sub">Manage account & preferences</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-ttl">👤 Profile</div>', unsafe_allow_html=True)
    new_name = st.text_input("Display Name", value=user_name, key="s_name")
    st.text_input("Email", value=user_email or "demo@webscraper.io", key="s_email", disabled=True)
    if st.button("💾  Save Changes", type="primary", key="save_p"):
        if new_name.strip():
            st.session_state["user_name"]=new_name.strip(); st.success("✅ Saved.")
        else: st.warning("Name cannot be empty.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel"><div class="panel-ttl">🔔 Notifications</div>', unsafe_allow_html=True)
    st.toggle("Email alerts on scrape completion", value=True, key="n1")
    st.toggle("Weekly usage report", value=False, key="n2")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel" style="border-color:rgba(255,77,109,.18)"><div class="panel-ttl" style="color:var(--danger)">⚠️ Danger Zone</div>', unsafe_allow_html=True)
    if st.button("🗑  Clear All Session Data", type="secondary", key="clear_all"):
        for k in ["scrape_history","last_df","scraper_df","total_rows","total_jobs"]:
            st.session_state[k]=[] if k=="scrape_history" else (0 if "total" in k else None)
        st.success("✅ Cleared.")
    st.markdown('</div>', unsafe_allow_html=True)
