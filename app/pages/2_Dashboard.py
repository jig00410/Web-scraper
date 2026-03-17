import streamlit as st
import pandas as pd
import json, io, os, sys
from datetime import datetime, timedelta

current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from theme_config import init_theme, get_theme_vars, get_bg_css

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

try:
    from llm.llm_processor import extract_with_llm
    llm_enabled = True
except Exception:
    llm_enabled = False
    def extract_with_llm(content, instructions=""): return {"success":False,"data":[],"error":"LLM not configured"}

st.set_page_config(page_title="Dashboard | WebScraper", layout="wide", initial_sidebar_state="expanded")

if not st.session_state.get("authenticated"):
    st.switch_page("main.py")

defaults = [
    ("scrape_history",[]),("last_df",None),("scraper_df",None),("total_rows",0),("total_jobs",0),
    ("chat_messages",[]),("chat_drawer_open",False),("chat_histories",[]),
    ("uploaded_files",[]),("canvas_data",None),
    ("schedules",[]),
]
for k,v in defaults:
    if k not in st.session_state: st.session_state[k] = v

user_name  = st.session_state.get("user_name","User")
user_email = st.session_state.get("user_email","")
av = (user_name[0] if user_name else "U").upper()
theme = init_theme()
tv = get_theme_vars(theme)
bg_css = get_bg_css(tv, theme)

# SVG Icons
ICONS = {
    "spider": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>',
    "home": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "search": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "history": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 3v5h5"/><path d="M3.05 13A9 9 0 1 0 6 5.3L3 8"/><path d="M12 7v5l4 2"/></svg>',
    "key": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="m21 2-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.78 7.78 5.5 5.5 0 0 1 7.78-7.78zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/></svg>',
    "settings": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "chat": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>',
    "upload": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/></svg>',
    "calendar": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "download": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "canvas": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/></svg>',
    "send": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>',
    "clock": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "play": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"/></svg>',
    "pause": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>',
    "trash": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
    "logout": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>',
    "file": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "image": '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>',
}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
:root{{
    --surface:{tv['surface']}; --card:{tv['card']}; --card2:{tv['card2']};
    --border:{tv['border']}; --border2:{tv['border2']};
    --accent:{tv['accent']}; --accent2:{tv['accent2']}; --accent3:{tv['accent3']};
    --text:{tv['text']}; --muted:{tv['muted']}; --danger:#ff4d6d; --heading:{tv['heading']};
}}
html,body,[data-testid="stAppViewContainer"],.stApp{{
    {bg_css}
    font-family:'DM Sans',sans-serif !important;
    color:var(--text) !important;
}}
#MainMenu,footer,header,[data-testid="stToolbar"],.stDeployButton{{display:none !important}}

/* SIDEBAR */
[data-testid="stSidebar"]{{background:var(--card) !important;border-right:1px solid var(--border) !important;}}
[data-testid="stSidebarContent"]{{padding:0 !important}}
[data-testid="stRadio"]>div{{gap:2px !important}}
[data-testid="stRadio"] label{{
    background:transparent !important;border:none !important;border-radius:8px !important;
    padding:10px 16px !important;color:var(--muted) !important;font-size:.88rem !important;
    font-family:'DM Sans',sans-serif !important;font-weight:500 !important;
    transition:all .2s ease !important;cursor:pointer !important;
}}
[data-testid="stRadio"] label:hover{{background:{tv['hover']} !important;color:var(--text) !important;}}
[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked){{
    background:rgba(0,229,255,.07) !important;color:var(--accent) !important;
    border-left:2px solid var(--accent) !important;
}}
[data-testid="stRadio"] [data-baseweb="radio"]>div:first-child{{display:none !important}}

/* INPUT */
.stTextInput label,.stTextInput>label{{display:none !important}}
.stTextInput>div>div>input{{
    background:{tv['input_bg']} !important;border:1px solid var(--border) !important;
    border-radius:10px !important;color:var(--heading) !important;padding:12px 15px !important;
    font-size:.9rem !important;font-family:'DM Sans',sans-serif !important;
    transition:all .2s ease !important;caret-color:var(--accent) !important;
}}
.stTextInput>div>div>input::placeholder{{color:var(--muted) !important}}
.stTextInput>div>div>input:focus{{
    background:rgba(0,229,255,.05) !important;
    border-color:rgba(0,229,255,.4) !important;
    box-shadow:0 0 0 3px rgba(0,229,255,.07) !important;outline:none !important;
}}

/* BUTTONS */
div.stButton>button{{
    font-family:'DM Sans',sans-serif !important;font-weight:700 !important;
    border-radius:9px !important;border:none !important;
    transition:all .3s cubic-bezier(.22,1,.36,1) !important;font-size:.88rem !important;
}}
div.stButton>button[kind="primary"]{{
    background:linear-gradient(135deg,var(--accent),var(--accent2)) !important;
    color:#000 !important;padding:12px 20px !important;
    box-shadow:0 0 20px rgba(0,229,255,.18) !important;
}}
div.stButton>button[kind="primary"]:hover{{transform:translateY(-2px) !important;box-shadow:0 6px 22px rgba(0,229,255,.35) !important;}}
div.stButton>button[kind="secondary"]{{
    background:{tv['input_bg']} !important;color:var(--text) !important;
    border:1px solid var(--border) !important;padding:10px 16px !important;
}}
div.stButton>button[kind="secondary"]:hover{{background:{tv['hover']} !important;transform:translateY(-1px) !important;}}

/* DOWNLOAD */
div.stDownloadButton>button{{
    font-family:'DM Sans',sans-serif !important;font-weight:600 !important;
    border-radius:9px !important;background:var(--card2) !important;
    color:var(--text) !important;border:1px solid var(--border) !important;
    padding:10px 12px !important;font-size:.83rem !important;
    transition:all .2s ease !important;width:100% !important;
}}
div.stDownloadButton>button:hover{{
    background:rgba(0,229,255,.09) !important;
    border-color:rgba(0,229,255,.3) !important;color:var(--accent) !important;
    transform:translateY(-1px) !important;
}}

/* DATAFRAME */
[data-testid="stDataFrame"]{{border:1px solid var(--border) !important;border-radius:12px !important;overflow:hidden !important;}}

/* ALERTS */
.stAlert{{border-radius:10px !important}}
[data-testid="stSuccess"]{{background:rgba(0,255,157,.07) !important;border-color:rgba(0,255,157,.2) !important}}
[data-testid="stError"]{{background:rgba(255,77,109,.07) !important;border-color:rgba(255,77,109,.2) !important}}
[data-testid="stWarning"]{{background:rgba(255,179,71,.07) !important;border-color:rgba(255,179,71,.2) !important}}
[data-testid="stInfo"]{{background:rgba(0,229,255,.07) !important;border-color:rgba(0,229,255,.18) !important}}

/* TOGGLE */
[data-testid="stToggle"] label{{color:var(--text) !important;font-family:'DM Sans',sans-serif !important}}

/* SIDEBAR PROFILE */
.sb-profile{{padding:22px 16px 16px;border-bottom:1px solid var(--border);margin-bottom:6px}}
.sb-avatar{{
    width:44px;height:44px;border-radius:11px;
    background:linear-gradient(135deg,var(--accent),var(--accent2));
    display:flex;align-items:center;justify-content:center;
    font-family:'Inter',sans-serif;font-size:1.1rem;font-weight:800;
    color:#000;margin-bottom:10px;
}}
.sb-name{{font-family:'Inter',sans-serif;font-weight:700;color:var(--heading);font-size:.92rem}}
.sb-email{{color:var(--muted);font-size:.75rem;margin-top:2px;word-break:break-all}}
.sb-badge{{
    display:inline-flex;align-items:center;gap:4px;
    background:rgba(0,255,157,.07);border:1px solid rgba(0,255,157,.18);
    color:var(--accent3);border-radius:20px;padding:3px 9px;
    font-size:.68rem;font-weight:600;margin-top:8px;letter-spacing:.3px;
}}
.sb-badge::before{{content:'';width:5px;height:5px;border-radius:50%;background:var(--accent3);box-shadow:0 0 5px var(--accent3)}}
.sb-section{{padding:0 10px;margin:10px 0 4px}}
.sb-section-lbl{{font-size:.62rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);padding:0 4px}}

/* PAGE */
.pg-header{{
    display:flex;align-items:flex-end;justify-content:space-between;
    margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid var(--border);
}}
.pg-title{{font-family:'Inter',sans-serif;font-size:1.5rem;font-weight:800;color:var(--heading);letter-spacing:-.5px}}
.pg-sub{{color:var(--muted);font-size:.82rem;margin-top:3px}}
.live-dot{{
    display:inline-flex;align-items:center;gap:6px;
    background:rgba(0,255,157,.07);border:1px solid rgba(0,255,157,.18);
    color:var(--accent3);border-radius:7px;padding:5px 11px;font-size:.73rem;font-family:'DM Mono',monospace;
}}
.live-dot::before{{content:'';width:5px;height:5px;border-radius:50%;background:var(--accent3);box-shadow:0 0 5px var(--accent3)}}

/* METRIC CARDS */
.m-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}}
.m-card{{
    background:var(--card);border:1px solid var(--border);border-radius:14px;
    padding:20px 18px;position:relative;overflow:hidden;
    transition:all .3s ease;
}}
.m-card::before{{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:var(--mg,linear-gradient(90deg,var(--accent),transparent))}}
.m-card:hover{{transform:translateY(-4px);border-color:rgba(0,229,255,.15)}}
.m-card:nth-child(2){{--mg:linear-gradient(90deg,var(--accent2),transparent)}}
.m-card:nth-child(3){{--mg:linear-gradient(90deg,var(--accent3),transparent)}}
.m-lbl{{font-size:.7rem;color:var(--muted);text-transform:uppercase;letter-spacing:.8px;margin-bottom:7px}}
.m-val{{font-family:'Inter',sans-serif;font-size:1.9rem;font-weight:800;color:var(--heading);letter-spacing:-1px;line-height:1}}
.m-sub{{font-size:.72rem;color:var(--muted);margin-top:4px}}

/* PANEL */
.panel{{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:20px}}
.panel+.panel{{margin-top:14px}}
.panel-ttl{{
    font-family:'Inter',sans-serif;font-size:.95rem;font-weight:700;
    color:var(--heading);margin-bottom:14px;display:flex;align-items:center;gap:7px;
}}
.panel-ttl .ac{{color:var(--accent)}}

/* SCHEMA TABLE */
.stbl{{width:100%;border-collapse:collapse;font-size:.82rem}}
.stbl th{{
    background:rgba(0,229,255,.05);color:var(--accent);padding:8px 12px;
    text-align:left;font-size:.7rem;letter-spacing:.8px;text-transform:uppercase;
    border-bottom:1px solid var(--border);font-weight:600;
}}
.stbl td{{padding:8px 12px;border-bottom:1px solid rgba(255,255,255,.04);color:var(--text);font-family:'DM Mono',monospace;font-size:.78rem}}
.stbl tr:last-child td{{border:none}}
.stbl tr:hover td{{background:{tv['hover']}}}

/* ACTIVITY */
.act-item{{display:flex;align-items:center;gap:12px;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.04)}}
.act-item:last-child{{border:none;padding-bottom:0}}
.act-dot{{width:7px;height:7px;border-radius:50%;flex-shrink:0;background:var(--accent);box-shadow:0 0 6px var(--accent)}}
.act-url{{font-size:.82rem;color:var(--text);font-family:'DM Mono',monospace;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:280px}}
.act-meta{{font-size:.7rem;color:var(--muted);margin-top:1px}}
.act-ok{{font-size:.72rem;font-weight:600;color:var(--accent3);white-space:nowrap}}

/* EMPTY */
.empty{{text-align:center;padding:40px 20px;color:var(--muted)}}
.empty-icon{{font-size:2rem;margin-bottom:10px;display:flex;justify-content:center}}
.empty-txt{{font-size:.85rem;line-height:1.6}}

/* LOGOUT */
.logout-wrap>div>button{{
    background:rgba(255,77,109,.06) !important;color:var(--danger) !important;
    border:1px solid rgba(255,77,109,.15) !important;font-size:.84rem !important;padding:9px !important;
}}
hr{{border-color:var(--border) !important;margin:14px 0 !important}}

/* CHAT */
.chat-container{{max-height:400px;overflow-y:auto;padding:10px 0;}}
.chat-msg{{display:flex;gap:10px;margin-bottom:12px;animation:fadeIn .3s ease;}}
@keyframes fadeIn{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:none}}}}
.chat-msg.user{{flex-direction:row-reverse;}}
.chat-bubble{{max-width:75%;padding:10px 14px;border-radius:12px;font-size:.85rem;line-height:1.5;}}
.chat-bubble.user{{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#000;border-bottom-right-radius:4px;}}
.chat-bubble.assistant{{background:var(--card2);color:var(--text);border:1px solid var(--border);border-bottom-left-radius:4px;}}
.chat-avatar{{width:28px;height:28px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700;flex-shrink:0;}}
.chat-avatar.user{{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#000;}}
.chat-avatar.assistant{{background:var(--card2);border:1px solid var(--border);color:var(--accent);}}

/* CHAT HISTORY DRAWER */
.chat-history-item{{padding:10px 14px;border-radius:8px;border:1px solid var(--border);margin-bottom:6px;cursor:pointer;transition:all .2s;background:var(--card);}}
.chat-history-item:hover{{border-color:rgba(0,229,255,.3);background:rgba(0,229,255,.03);}}
.chat-history-title{{font-size:.82rem;font-weight:600;color:var(--heading);}}
.chat-history-meta{{font-size:.7rem;color:var(--muted);margin-top:2px;}}

/* UPLOAD ZONE */
.upload-zone{{border:2px dashed var(--border2);border-radius:14px;padding:30px;text-align:center;transition:all .3s;cursor:pointer;}}
.upload-zone:hover{{border-color:rgba(0,229,255,.3);background:rgba(0,229,255,.03);}}
.upload-icon{{margin-bottom:8px;color:var(--muted);display:flex;justify-content:center;}}
.upload-icon svg{{width:32px;height:32px;}}

/* CANVAS */
.canvas-area{{min-height:300px;border:1px solid var(--border);border-radius:14px;padding:20px;background:var(--card);}}

/* SCHEDULER */
.sched-card{{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;margin-bottom:10px;transition:all .3s;}}
.sched-card:hover{{border-color:rgba(0,229,255,.2);}}
.sched-header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;}}
.sched-url{{font-family:'DM Mono',monospace;font-size:.82rem;color:var(--heading);}}
.sched-badge{{font-size:.68rem;font-weight:600;padding:3px 8px;border-radius:12px;}}
.sched-badge.active{{background:rgba(0,255,157,.1);color:var(--accent3);border:1px solid rgba(0,255,157,.2);}}
.sched-badge.paused{{background:rgba(255,179,71,.1);color:#ffb347;border:1px solid rgba(255,179,71,.2);}}
.sched-details{{display:flex;gap:16px;font-size:.75rem;color:var(--muted);}}

/* FILE LIST */
.file-item{{display:flex;align-items:center;gap:10px;padding:8px 12px;border-radius:8px;border:1px solid var(--border);margin-bottom:6px;transition:all .2s;}}
.file-item:hover{{border-color:rgba(0,229,255,.2);}}
.file-icon{{color:var(--accent);display:flex;align-items:center;}}
.file-name{{font-size:.82rem;color:var(--heading);flex:1;}}
.file-size{{font-size:.72rem;color:var(--muted);}}
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
    menu = st.radio("nav", [
        "🏠  Dashboard","🔍  Scraper","💬  AI Chat","📁  Files & Media",
        "📊  Data Canvas","⏰  Scheduler","📋  History","🔑  API Keys","⚙️  Settings"
    ], label_visibility="collapsed", key="nav_menu")

    # Theme toggle in sidebar
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sb-section"><span class="sb-section-lbl">Appearance</span></div>', unsafe_allow_html=True)
    tc1, tc2, tc3 = st.columns(3)
    with tc1:
        lbl = "◼ Dark" if theme == "dark" else "Dark"
        if st.button(lbl, key="t_dark", use_container_width=True):
            st.session_state["theme"]="dark"; st.rerun()
    with tc2:
        lbl = "◻ Light" if theme == "light" else "Light"
        if st.button(lbl, key="t_light", use_container_width=True):
            st.session_state["theme"]="light"; st.rerun()
    with tc3:
        lbl = "◈ Vivid" if theme == "multi" else "Vivid"
        if st.button(lbl, key="t_multi", use_container_width=True):
            st.session_state["theme"]="multi"; st.rerun()

    st.markdown("<br>"*2, unsafe_allow_html=True)
    st.markdown('<div class="logout-wrap">', unsafe_allow_html=True)
    if st.button(f"{ICONS['logout']}  Sign Out", use_container_width=True, key="logout"):
        for k in list(st.session_state.keys()): del st.session_state[k]
        st.switch_page("main.py")
    st.markdown('</div>', unsafe_allow_html=True)

page = menu.split("  ",1)[1].strip()
colors=["var(--accent)","var(--accent2)","var(--accent3)"]

# ═══ DASHBOARD ═══
if page == "Dashboard":
    st.markdown(f"""
    <div class="pg-header">
        <div><div class="pg-title">{ICONS['home']} Dashboard</div><div class="pg-sub">Your scraping overview</div></div>
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
        st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["search"]} Enter Website URL to Scrape</div>', unsafe_allow_html=True)
        url = st.text_input("u", placeholder="https://quotes.toscrape.com", key="dash_url")
        if st.button("Run Extraction", type="primary", use_container_width=True, key="dash_go"):
            if url.strip():
                with st.spinner("Extracting…"):
                    r = scrape_website_data(url.strip())
                if r["success"]:
                    df = pd.DataFrame(r["headings"], columns=["Scraped Content"])
                    st.session_state.update({"last_df":df,"last_title":r["title"],"total_rows":st.session_state["total_rows"]+len(df),"total_jobs":st.session_state["total_jobs"]+1})
                    st.session_state["scrape_history"].insert(0,{"url":url.strip(),"title":r["title"],"rows":len(df),"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
                    if db_enabled: save_scrape_to_history(user_email, url.strip(), r["title"], len(df))
                    st.success(f"Extracted **{len(df)} items** — {r['title']}")
                    st.dataframe(df, use_container_width=True, height=260)
                else:
                    st.error(r["error"])
            else:
                st.warning("Please enter a URL.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_side:
        st.markdown(f"""
        <div class="panel"><div class="panel-ttl">{ICONS['canvas']} Data Schema</div>
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
                st.download_button("CSV", df.to_csv(index=False).encode(), "data.csv","text/csv", use_container_width=True, key="dl_csv_d")
            with c2:
                st.download_button("JSON", json.dumps(df.to_dict("records"),indent=2).encode(), "data.json","application/json", use_container_width=True, key="dl_json_d")
            with c3:
                buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
                st.download_button("Excel", buf.getvalue(),"data.xlsx", use_container_width=True, key="dl_xlsx_d")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["clock"]} Recent Activity</div>', unsafe_allow_html=True)
    hist = st.session_state["scrape_history"]
    if hist:
        for i,item in enumerate(hist[:5]):
            c=colors[i%3]
            st.markdown(f'<div class="act-item"><div class="act-dot" style="background:{c};box-shadow:0 0 6px {c}"></div><div style="flex:1;min-width:0"><div class="act-url">{item["url"]}</div><div class="act-meta">{item["rows"]} rows · {item["time"]}</div></div><div class="act-ok">✓ Done</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="empty"><div class="empty-icon">{ICONS["spider"]}</div><div class="empty-txt">No activity yet. Run your first scrape above!</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ═══ SCRAPER ═══
elif page == "Scraper":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["search"]} Web Scraper</div><div class="pg-sub">Extract data from any URL</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["search"]} Target URL</div>', unsafe_allow_html=True)
    url = st.text_input("su", placeholder="https://quotes.toscrape.com", key="scraper_url")
    c1,c2 = st.columns([2,1])
    with c1:
        run = st.button("Run Extraction", type="primary", use_container_width=True, key="run_btn")
    with c2:
        if st.button("Clear", type="secondary", use_container_width=True, key="clear_btn"):
            st.session_state["scraper_df"]=None; st.rerun()
    if run:
        if url.strip():
            with st.spinner("Launching browser…"):
                r = scrape_website_data(url.strip())
            if r["success"]:
                df=pd.DataFrame(r["headings"],columns=["Scraped Content"])
                st.session_state.update({"scraper_df":df,"scraper_title":r["title"],"total_rows":st.session_state["total_rows"]+len(df),"total_jobs":st.session_state["total_jobs"]+1})
                st.session_state["scrape_history"].insert(0,{"url":url.strip(),"title":r["title"],"rows":len(df),"time":datetime.now().strftime("%Y-%m-%d %H:%M")})
                if db_enabled: save_scrape_to_history(user_email,url.strip(),r["title"],len(df))
                st.success(f"**{r['title']}** — {len(df)} items extracted")
            else:
                st.error(r["error"])
        else:
            st.warning("Enter a URL.")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["scraper_df"] is not None:
        df=st.session_state["scraper_df"]
        st.markdown(f'<br><div class="panel"><div class="panel-ttl">{ICONS["canvas"]} Results — <span class="ac">{len(df)} rows</span></div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=400)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["download"]} Export</div>', unsafe_allow_html=True)
        c1,c2,c3,_=st.columns([1,1,1,1.5])
        with c1:
            st.download_button("CSV",df.to_csv(index=False).encode(),"data.csv","text/csv",use_container_width=True,key="sc_csv")
        with c2:
            st.download_button("JSON",json.dumps(df.to_dict("records"),indent=2).encode(),"data.json",use_container_width=True,key="sc_json")
        with c3:
            buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
            st.download_button("Excel",buf.getvalue(),"data.xlsx",use_container_width=True,key="sc_xlsx")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<br><div class="panel"><div class="empty"><div class="empty-icon">{ICONS["search"]}</div><div class="empty-txt">Enter a URL above and click <b>Run Extraction</b><br>Try: <code>https://quotes.toscrape.com</code></div></div></div>', unsafe_allow_html=True)

# ═══ AI CHAT ═══
elif page == "AI Chat":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["chat"]} AI Chat</div><div class="pg-sub">Analyze scraped data with AI assistance</div></div></div>', unsafe_allow_html=True)

    chat_col, history_col = st.columns([2.5, 1])

    with history_col:
        st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["history"]} Chat History</div>', unsafe_allow_html=True)
        if st.button("+ New Chat", type="primary", use_container_width=True, key="new_chat"):
            if st.session_state["chat_messages"]:
                title = st.session_state["chat_messages"][0]["content"][:40] + "..." if len(st.session_state["chat_messages"][0]["content"]) > 40 else st.session_state["chat_messages"][0]["content"]
                st.session_state["chat_histories"].insert(0, {
                    "title": title,
                    "messages": st.session_state["chat_messages"].copy(),
                    "time": datetime.now().strftime("%H:%M")
                })
            st.session_state["chat_messages"] = []
            st.rerun()

        for i, ch in enumerate(st.session_state["chat_histories"][:10]):
            st.markdown(f"""
            <div class="chat-history-item">
                <div class="chat-history-title">{ch['title']}</div>
                <div class="chat-history-meta">{len(ch['messages'])} messages · {ch['time']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Load", key=f"load_chat_{i}", use_container_width=True):
                st.session_state["chat_messages"] = ch["messages"].copy()
                st.rerun()

        if not st.session_state["chat_histories"]:
            st.markdown(f'<div class="empty"><div class="empty-icon">{ICONS["chat"]}</div><div class="empty-txt">No chat history yet</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with chat_col:
        st.markdown(f'<div class="panel">', unsafe_allow_html=True)

        # Display chat messages
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state["chat_messages"]:
            role = msg["role"]
            bubble_class = "user" if role == "user" else "assistant"
            avatar_text = av if role == "user" else "AI"
            st.markdown(f"""
            <div class="chat-msg {bubble_class}">
                <div class="chat-avatar {bubble_class}">{avatar_text}</div>
                <div class="chat-bubble {bubble_class}">{msg['content']}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Chat input
        user_input = st.text_input("msg", placeholder="Ask about your scraped data or request analysis...", key="chat_input", label_visibility="collapsed")
        ic1, ic2 = st.columns([4,1])
        with ic2:
            send = st.button("Send", type="primary", use_container_width=True, key="send_msg")

        if send and user_input:
            st.session_state["chat_messages"].append({"role":"user","content":user_input})

            # Check if there's scraped data to analyze
            df = st.session_state.get("last_df") or st.session_state.get("scraper_df")
            if df is not None:
                data_context = df.head(20).to_string()
                if llm_enabled:
                    result = extract_with_llm(data_context, user_input)
                    if result["success"]:
                        response = f"Based on the scraped data analysis:\n\n{json.dumps(result['data'], indent=2)}"
                    else:
                        response = f"I have access to {len(df)} rows of scraped data. To enable AI analysis, configure your OpenAI API key in the .env file.\n\nHere's a summary: The dataset contains {len(df)} entries with column(s): {', '.join(df.columns.tolist())}."
                else:
                    response = f"I can see {len(df)} rows of scraped data with columns: {', '.join(df.columns.tolist())}.\n\nTop entries:\n" + "\n".join([f"• {row}" for row in df.iloc[:5,0].tolist()]) + "\n\nTo enable full AI analysis, add OPENAI_API_KEY to your .env file."
            else:
                response = "No scraped data available yet. Please scrape a URL first from the Dashboard or Scraper page, then come back to analyze the results!"

            st.session_state["chat_messages"].append({"role":"assistant","content":response})
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ═══ FILES & MEDIA ═══
elif page == "Files & Media":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["file"]} Files & Media</div><div class="pg-sub">Upload, manage, and download files and images</div></div></div>', unsafe_allow_html=True)

    upload_col, files_col = st.columns([1.2, 1])

    with upload_col:
        st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["upload"]} Upload Files</div>', unsafe_allow_html=True)

        uploaded = st.file_uploader(
            "Upload files",
            type=["csv","json","xlsx","xls","txt","pdf","png","jpg","jpeg","gif","svg"],
            accept_multiple_files=True,
            key="file_uploader",
            label_visibility="collapsed"
        )

        if uploaded:
            for f in uploaded:
                file_info = {"name": f.name, "size": f.size, "type": f.type, "time": datetime.now().strftime("%H:%M")}
                # Avoid duplicates
                if not any(x["name"] == f.name for x in st.session_state["uploaded_files"]):
                    st.session_state["uploaded_files"].append(file_info)

                # Process based on type
                if f.name.endswith(".csv"):
                    try:
                        df = pd.read_csv(f)
                        st.session_state["canvas_data"] = df
                        st.success(f"Loaded **{f.name}** — {len(df)} rows, {len(df.columns)} columns")
                        st.dataframe(df.head(10), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error reading {f.name}: {e}")
                elif f.name.endswith(".json"):
                    try:
                        data = json.load(f)
                        if isinstance(data, list):
                            df = pd.DataFrame(data)
                            st.session_state["canvas_data"] = df
                            st.success(f"Loaded **{f.name}** — {len(df)} records")
                        else:
                            st.json(data)
                    except Exception as e:
                        st.error(f"Error reading {f.name}: {e}")
                elif f.name.endswith((".xlsx",".xls")):
                    try:
                        df = pd.read_excel(f)
                        st.session_state["canvas_data"] = df
                        st.success(f"Loaded **{f.name}** — {len(df)} rows")
                        st.dataframe(df.head(10), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error reading {f.name}: {e}")
                elif f.name.endswith((".png",".jpg",".jpeg",".gif")):
                    st.image(f, caption=f.name, use_container_width=True)
                else:
                    st.info(f"Uploaded: **{f.name}** ({f.size/1024:.1f} KB)")

        st.markdown('</div>', unsafe_allow_html=True)

        # Quick export from scraped data
        df = st.session_state.get("last_df") or st.session_state.get("scraper_df")
        if df is not None:
            st.markdown(f'<br><div class="panel"><div class="panel-ttl">{ICONS["download"]} Export Scraped Data</div>', unsafe_allow_html=True)
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                st.download_button("CSV", df.to_csv(index=False).encode(), "scraped_data.csv", "text/csv", use_container_width=True, key="fe_csv")
            with ec2:
                st.download_button("JSON", json.dumps(df.to_dict("records"),indent=2).encode(), "scraped_data.json", use_container_width=True, key="fe_json")
            with ec3:
                buf=io.BytesIO(); df.to_excel(buf,index=False,engine="openpyxl")
                st.download_button("Excel", buf.getvalue(), "scraped_data.xlsx", use_container_width=True, key="fe_xlsx")
            st.markdown('</div>', unsafe_allow_html=True)

    with files_col:
        st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["file"]} Uploaded Files</div>', unsafe_allow_html=True)
        if st.session_state["uploaded_files"]:
            for f in st.session_state["uploaded_files"]:
                ext = f["name"].rsplit(".",1)[-1].lower()
                icon = ICONS["image"] if ext in ("png","jpg","jpeg","gif","svg") else ICONS["file"]
                size_str = f"{f['size']/1024:.1f} KB" if f["size"] < 1024*1024 else f"{f['size']/(1024*1024):.1f} MB"
                st.markdown(f"""
                <div class="file-item">
                    <div class="file-icon">{icon}</div>
                    <div class="file-name">{f['name']}</div>
                    <div class="file-size">{size_str}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="empty"><div class="empty-icon">{ICONS["upload"]}</div><div class="empty-txt">No files uploaded yet.<br>Upload CSV, JSON, Excel, images, or PDFs.</div></div>', unsafe_allow_html=True)

        if st.session_state["uploaded_files"]:
            if st.button("Clear All Files", type="secondary", use_container_width=True, key="clear_files"):
                st.session_state["uploaded_files"] = []; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ═══ DATA CANVAS ═══
elif page == "Data Canvas":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["canvas"]} Data Canvas</div><div class="pg-sub">Visualize and analyze your data with interactive charts</div></div></div>', unsafe_allow_html=True)

    # Get available data
    df = st.session_state.get("canvas_data") or st.session_state.get("last_df") or st.session_state.get("scraper_df")

    if df is not None:
        st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["canvas"]} Data Overview — {len(df)} rows × {len(df.columns)} columns</div>', unsafe_allow_html=True)

        # Data summary
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.metric("Rows", len(df))
        with mc2:
            st.metric("Columns", len(df.columns))
        with mc3:
            st.metric("Data Types", df.dtypes.nunique())
        st.markdown('</div>', unsafe_allow_html=True)

        # Interactive table
        st.markdown(f'<br><div class="panel"><div class="panel-ttl">{ICONS["canvas"]} Data Table</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=300)
        st.markdown('</div>', unsafe_allow_html=True)

        # Charts
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        if numeric_cols:
            st.markdown(f'<br><div class="panel"><div class="panel-ttl">Charts</div>', unsafe_allow_html=True)
            chart_type = st.selectbox("Chart Type", ["Bar Chart", "Line Chart", "Area Chart"], key="chart_type")
            selected_col = st.selectbox("Column", numeric_cols, key="chart_col")
            if chart_type == "Bar Chart":
                st.bar_chart(df[selected_col])
            elif chart_type == "Line Chart":
                st.line_chart(df[selected_col])
            else:
                st.area_chart(df[selected_col])
            st.markdown('</div>', unsafe_allow_html=True)

        # Column statistics
        st.markdown(f'<br><div class="panel"><div class="panel-ttl">Column Statistics</div>', unsafe_allow_html=True)
        st.dataframe(df.describe(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Value counts for text columns
        text_cols = df.select_dtypes(include=["object"]).columns.tolist()
        if text_cols:
            st.markdown(f'<br><div class="panel"><div class="panel-ttl">Text Analysis</div>', unsafe_allow_html=True)
            text_col = st.selectbox("Column", text_cols, key="text_col")
            vc = df[text_col].value_counts().head(15)
            st.bar_chart(vc)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="panel">
            <div class="empty">
                <div class="empty-icon">{ICONS['canvas']}</div>
                <div class="empty-txt">No data available for visualization.<br>
                Scrape a URL from the Dashboard, or upload a file in Files & Media.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ═══ SCHEDULER ═══
elif page == "Scheduler":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["calendar"]} Scraping Scheduler</div><div class="pg-sub">Configure automated scraping jobs</div></div></div>', unsafe_allow_html=True)

    # Add new schedule
    st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["calendar"]} Create New Schedule</div>', unsafe_allow_html=True)

    sc1, sc2 = st.columns([2,1])
    with sc1:
        sched_url = st.text_input("Target URL", placeholder="https://quotes.toscrape.com", key="sched_url")
    with sc2:
        frequency = st.selectbox("Frequency", ["Every 15 min","Every 30 min","Hourly","Every 6 hours","Daily","Weekly"], key="sched_freq")

    sc3, sc4, sc5 = st.columns(3)
    with sc3:
        start_date = st.date_input("Start Date", value=datetime.now(), key="sched_start")
    with sc4:
        start_time = st.time_input("Start Time", value=datetime.now().time(), key="sched_time")
    with sc5:
        max_runs = st.number_input("Max Runs (0=unlimited)", min_value=0, value=0, key="sched_max")

    sc6, sc7 = st.columns([1,1])
    with sc6:
        notify = st.toggle("Email notification on completion", value=True, key="sched_notify")
    with sc7:
        auto_export = st.selectbox("Auto-export format", ["None","CSV","JSON","Excel"], key="sched_export")

    if st.button("Create Schedule", type="primary", use_container_width=True, key="create_sched"):
        if sched_url.strip():
            schedule = {
                "url": sched_url.strip(),
                "frequency": frequency,
                "start_date": str(start_date),
                "start_time": str(start_time),
                "max_runs": max_runs,
                "notify": notify,
                "auto_export": auto_export,
                "status": "active",
                "runs": 0,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "next_run": (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M"),
            }
            st.session_state["schedules"].insert(0, schedule)
            st.success(f"Schedule created for **{sched_url}** — {frequency}")
            st.rerun()
        else:
            st.warning("Please enter a target URL.")
    st.markdown('</div>', unsafe_allow_html=True)

    # Active schedules
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["clock"]} Active Schedules</div>', unsafe_allow_html=True)

    if st.session_state["schedules"]:
        for i, sched in enumerate(st.session_state["schedules"]):
            status_class = "active" if sched["status"] == "active" else "paused"
            status_label = "Active" if sched["status"] == "active" else "Paused"

            st.markdown(f"""
            <div class="sched-card">
                <div class="sched-header">
                    <div class="sched-url">{sched['url'][:50]}{'...' if len(sched['url'])>50 else ''}</div>
                    <div class="sched-badge {status_class}">● {status_label}</div>
                </div>
                <div class="sched-details">
                    <span>{ICONS['clock']} {sched['frequency']}</span>
                    <span>Next: {sched['next_run']}</span>
                    <span>Runs: {sched['runs']}/{sched['max_runs'] if sched['max_runs'] > 0 else '∞'}</span>
                    <span>Export: {sched['auto_export']}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                btn_label = "Pause" if sched["status"] == "active" else "Resume"
                if st.button(btn_label, key=f"toggle_{i}", use_container_width=True):
                    st.session_state["schedules"][i]["status"] = "paused" if sched["status"]=="active" else "active"
                    st.rerun()
            with bc2:
                if st.button("Run Now", key=f"run_{i}", type="primary", use_container_width=True):
                    with st.spinner("Running scheduled scrape…"):
                        r = scrape_website_data(sched["url"])
                    if r["success"]:
                        st.session_state["schedules"][i]["runs"] += 1
                        st.session_state["total_rows"] += len(r["headings"])
                        st.session_state["total_jobs"] += 1
                        st.success(f"Extracted {len(r['headings'])} items from {sched['url']}")
                    else:
                        st.error(r["error"])
            with bc3:
                if st.button("Delete", key=f"del_{i}", type="secondary", use_container_width=True):
                    st.session_state["schedules"].pop(i); st.rerun()
    else:
        st.markdown(f'<div class="empty"><div class="empty-icon">{ICONS["calendar"]}</div><div class="empty-txt">No scheduled jobs yet.<br>Create one above to automate your scraping.</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Scheduler info
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("**Note:** Scheduled jobs run while the app is active. For persistent scheduling, integrate with a task queue (Celery, APScheduler) or cron jobs on your server.")

# ═══ HISTORY ═══
elif page == "History":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["history"]} Scrape History</div><div class="pg-sub">All extraction jobs this session</div></div></div>', unsafe_allow_html=True)
    _,cb=st.columns([3,1])
    with cb:
        if st.session_state["scrape_history"] and st.button("Clear",type="secondary",use_container_width=True):
            st.session_state["scrape_history"]=[]; st.rerun()
    hist=st.session_state["scrape_history"]
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    if hist:
        for i,item in enumerate(hist):
            c=colors[i%3]
            st.markdown(f'<div class="act-item"><div class="act-dot" style="background:{c};box-shadow:0 0 6px {c}"></div><div style="flex:1;min-width:0"><div class="act-url">{item["url"]}</div><div class="act-meta">{item.get("title","")[:50]} · {item["rows"]} rows · {item["time"]}</div></div><div class="act-ok">✓ Done</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="empty"><div class="empty-icon">{ICONS["history"]}</div><div class="empty-txt">No history yet. Scrape some URLs!</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if not db_enabled: st.info("Connect Firebase to persist history across sessions.")

# ═══ API KEYS ═══
elif page == "API Keys":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["key"]} API Keys</div><div class="pg-sub">Manage your credentials</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><div class="panel-ttl">{ICONS["key"]} Active Keys</div><table class="stbl"><tr><th>Name</th><th>Key</th><th>Created</th><th>Status</th></tr><tr><td>Default</td><td style="font-family:\'DM Mono\',monospace">ws_live_••••••••3f2a</td><td>2025-06-01</td><td style="color:var(--accent3);font-weight:600">● Active</td></tr></table></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("+ Generate New Key", type="primary"):
        st.info("API key generation requires backend integration.")

# ═══ SETTINGS ═══
elif page == "Settings":
    st.markdown(f'<div class="pg-header"><div><div class="pg-title">{ICONS["settings"]} Settings</div><div class="pg-sub">Manage account & preferences</div></div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><div class="panel-ttl">Profile</div>', unsafe_allow_html=True)
    new_name = st.text_input("Display Name", value=user_name, key="s_name")
    st.text_input("Email", value=user_email or "demo@webscraper.io", key="s_email", disabled=True)
    if st.button("Save Changes", type="primary", key="save_p"):
        if new_name.strip():
            st.session_state["user_name"]=new_name.strip(); st.success("Saved.")
        else: st.warning("Name cannot be empty.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f'<div class="panel"><div class="panel-ttl">Notifications</div>', unsafe_allow_html=True)
    st.toggle("Email alerts on scrape completion", value=True, key="n1")
    st.toggle("Weekly usage report", value=False, key="n2")
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="panel" style="border-color:rgba(255,77,109,.18)"><div class="panel-ttl" style="color:var(--danger)">Danger Zone</div>', unsafe_allow_html=True)
    if st.button("Clear All Session Data", type="secondary", key="clear_all"):
        for k in ["scrape_history","last_df","scraper_df","total_rows","total_jobs","chat_messages","chat_histories","uploaded_files","canvas_data","schedules"]:
            st.session_state[k]=[] if k in ("scrape_history","chat_messages","chat_histories","uploaded_files","schedules") else (0 if "total" in k else None)
        st.success("Cleared.")
    st.markdown('</div>', unsafe_allow_html=True)
