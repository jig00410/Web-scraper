import streamlit as st
import os, sys

current_dir  = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from database.firebase_config import initialize_firebase, create_user_in_firebase
    firebase_enabled = True
except ImportError:
    firebase_enabled = False
    def initialize_firebase(): pass
    def create_user_in_firebase(email, password):
        return {"success": True, "user": None}

try:
    if firebase_enabled:
        initialize_firebase()
except Exception:
    pass

st.set_page_config(page_title="Auth | WebScraper", layout="centered", initial_sidebar_state="collapsed")

if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "signin"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: #08090d !important;
    font-family: 'DM Sans', sans-serif !important;
    color: #c8d6e5 !important;
    min-height: 100vh;
}

#MainMenu, footer, header,
[data-testid="stSidebarNav"], [data-testid="stSidebar"],
[data-testid="stToolbar"], .stDeployButton { display:none !important; }

/* kill ALL default streamlit padding/gaps */
.block-container {
    padding: 2rem 1rem 2rem !important;
    max-width: 460px !important;
}
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }
div[data-testid="stVerticalBlock"] > div:has(> div:empty) { display:none !important; }

/* aurora blobs */
body::before {
    content:''; position:fixed; width:500px; height:500px;
    top:-150px; left:-100px; border-radius:50%;
    background:radial-gradient(circle,rgba(0,229,255,.09),transparent 70%);
    filter:blur(100px); pointer-events:none; z-index:0;
}
body::after {
    content:''; position:fixed; width:400px; height:400px;
    bottom:-80px; right:-60px; border-radius:50%;
    background:radial-gradient(circle,rgba(123,97,255,.11),transparent 70%);
    filter:blur(90px); pointer-events:none; z-index:0;
}

/* card wrapper — applied via CSS on the block container */
.stApp [data-testid="stAppViewBlockContainer"] > div > div > div > div {
    position: relative; z-index: 1;
}

/* logo */
.auth-logo {
    font-family:'Syne',sans-serif; font-size:1.05rem; font-weight:800;
    display:flex; align-items:center; gap:8px;
    margin-bottom:28px;
}
.auth-logo-icon {
    width:30px; height:30px; border-radius:8px;
    background:linear-gradient(135deg,#00e5ff,#7b61ff);
    display:flex; align-items:center; justify-content:center; font-size:.85rem;
}
.auth-logo em {
    font-style:normal;
    background:linear-gradient(135deg,#00e5ff,#7b61ff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}
.auth-title {
    font-family:'Syne',sans-serif; font-size:1.75rem; font-weight:800;
    color:#fff; letter-spacing:-.5px; margin-bottom:4px;
}
.auth-sub { color:#4a5a6a; font-size:.85rem; margin-bottom:22px; }

/* social buttons row */
.socials { display:flex; gap:8px; margin-bottom:18px; }
.soc-btn {
    flex:1; height:40px; border-radius:9px;
    background:rgba(255,255,255,.05); border:1px solid rgba(255,255,255,.08);
    display:flex; align-items:center; justify-content:center;
    font-size:.88rem; color:#fff; cursor:pointer; transition:all .2s ease;
}
.soc-btn:hover { background:rgba(255,255,255,.1); transform:translateY(-2px); }

/* divider */
.divider {
    display:flex; align-items:center; gap:10px;
    color:#4a5a6a; font-size:.75rem; margin-bottom:18px;
}
.divider::before,.divider::after { content:''; flex:1; height:1px; background:rgba(255,255,255,.08); }

/* forgot */
.forgot { text-align:right; margin-bottom:14px; }
.forgot a { font-size:.78rem; color:#00e5ff; cursor:pointer; text-decoration:none; }

/* switch */
.switch-row { text-align:center; margin-top:12px; font-size:.82rem; color:#4a5a6a; }

/* ── INPUT overrides ── */
div[data-testid="stTextInput"] { margin-bottom:10px !important; }
div[data-testid="stTextInput"] label { display:none !important; }
div[data-testid="stTextInput"] > div > div > input {
    background: rgba(255,255,255,.05) !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    border-radius: 10px !important;
    color: #fff !important;
    padding: 12px 14px !important;
    font-size: .9rem !important;
    font-family: 'DM Sans', sans-serif !important;
    caret-color: #00e5ff !important;
    transition: border .2s, box-shadow .2s, background .2s !important;
}
div[data-testid="stTextInput"] > div > div > input::placeholder { color:#4a5a6a !important; }
div[data-testid="stTextInput"] > div > div > input:focus {
    background: rgba(0,229,255,.04) !important;
    border-color: rgba(0,229,255,.4) !important;
    box-shadow: 0 0 0 3px rgba(0,229,255,.07) !important;
    outline: none !important;
}

/* ── BUTTON overrides ── */
div.stButton > button {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    width: 100% !important;
    transition: all .3s cubic-bezier(.22,1,.36,1) !important;
}
/* primary */
div.stButton.pri > button {
    background: linear-gradient(135deg,#00e5ff,#7b61ff) !important;
    color: #000 !important; padding: 13px !important; font-size: .92rem !important;
    box-shadow: 0 0 22px rgba(0,229,255,.18) !important;
}
div.stButton.pri > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 22px rgba(0,229,255,.35) !important;
}
/* ghost */
div.stButton.ghost > button {
    background: rgba(255,255,255,.05) !important;
    color: #c8d6e5 !important;
    border: 1px solid rgba(255,255,255,.09) !important;
    padding: 11px !important; font-size: .88rem !important;
}
div.stButton.ghost > button:hover {
    background: rgba(255,255,255,.09) !important;
    transform: translateY(-1px) !important;
}
/* back */
div.stButton.back > button {
    background: transparent !important;
    color: #4a5a6a !important;
    border: 1px solid rgba(255,255,255,.08) !important;
    padding: 7px 14px !important; font-size: .78rem !important;
    width: auto !important; border-radius: 8px !important;
}

/* alert */
div[data-testid="stAlert"] { border-radius:10px !important; margin-top:8px !important; }

/* horizontal rule */
hr { border-color: rgba(255,255,255,.07) !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

mode = st.session_state["auth_mode"]

# ── BACK BUTTON ──────────────────────────
st.markdown('<div class="back">', unsafe_allow_html=True)
if st.button("← Home", key="back_home"):
    st.switch_page("main.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── LOGO + TITLE (pure HTML, no inputs inside) ──────────────────────
if mode == "signin":
    st.markdown("""
    <div class="auth-logo"><div class="auth-logo-icon">🕷️</div>Web<em>Scraper</em></div>
    <div class="auth-title">Welcome back</div>
    <div class="auth-sub">Sign in to access your dashboard</div>
    <div class="socials">
        <div class="soc-btn">G</div>
        <div class="soc-btn">f</div>
        <div class="soc-btn">in</div>
    </div>
    <div class="divider">or continue with email</div>
    """, unsafe_allow_html=True)

    email    = st.text_input("_email",    placeholder="you@example.com", key="si_email",   label_visibility="collapsed")
    password = st.text_input("_password", placeholder="Your password",   key="si_pass",    label_visibility="collapsed", type="password")

    st.markdown('<div class="forgot"><a>Forgot password?</a></div>', unsafe_allow_html=True)

    st.markdown('<div class="pri">', unsafe_allow_html=True)
    if st.button("Sign In →", key="do_signin", use_container_width=True):
        if email and password:
            st.session_state.update({"authenticated":True,"user_name":email.split("@")[0],"user_email":email})
            st.switch_page("pages/2_Dashboard.py")
        else:
            st.error("Please enter email and password.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="switch-row">Don\'t have an account?</div>', unsafe_allow_html=True)
    st.markdown('<div class="ghost" style="margin-top:8px">', unsafe_allow_html=True)
    if st.button("Create account", key="go_signup", use_container_width=True):
        st.session_state["auth_mode"] = "signup"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="auth-logo"><div class="auth-logo-icon">🕷️</div>Web<em>Scraper</em></div>
    <div class="auth-title">Create account</div>
    <div class="auth-sub">Start extracting data for free today</div>
    <div class="socials">
        <div class="soc-btn">G</div>
        <div class="soc-btn">f</div>
        <div class="soc-btn">in</div>
    </div>
    <div class="divider">or register with email</div>
    """, unsafe_allow_html=True)

    name     = st.text_input("_name",     placeholder="Full name",           key="su_name",    label_visibility="collapsed")
    email    = st.text_input("_email",    placeholder="you@example.com",     key="su_email",   label_visibility="collapsed")
    password = st.text_input("_password", placeholder="Min. 6 characters",   key="su_pass",    label_visibility="collapsed", type="password")
    confirm  = st.text_input("_confirm",  placeholder="Confirm password",    key="su_confirm", label_visibility="collapsed", type="password")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="pri">', unsafe_allow_html=True)
    if st.button("Create Account →", key="do_signup", use_container_width=True):
        if email and password and len(password) >= 6:
            if password != confirm:
                st.error("Passwords don't match.")
            else:
                res = create_user_in_firebase(email, password)
                if res["success"]:
                    st.success("✅ Account created! Please sign in.")
                    st.session_state["auth_mode"] = "signin"
                    st.rerun()
                else:
                    st.error(f"❌ {res.get('error','Unknown error')}")
        else:
            st.error("Fill all fields. Password ≥ 6 characters.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="switch-row">Already have an account?</div>', unsafe_allow_html=True)
    st.markdown('<div class="ghost" style="margin-top:8px">', unsafe_allow_html=True)
    if st.button("Sign in instead", key="go_signin", use_container_width=True):
        st.session_state["auth_mode"] = "signin"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
