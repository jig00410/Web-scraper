import streamlit as st
import os, sys

current_dir  = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(app_dir)
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from theme_config import init_theme, get_theme_vars, get_bg_css

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

theme = init_theme()
tv = get_theme_vars(theme)
bg_style = get_bg_css(tv, theme)

if "auth_mode" not in st.session_state:
    st.session_state["auth_mode"] = "signin"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}

html, body, [data-testid="stAppViewContainer"], .stApp {{
    {bg_style}
    font-family: 'Inter', sans-serif !important;
    color: {tv['text']} !important;
    min-height: 100vh;
}}

#MainMenu, footer, header,
[data-testid="stSidebarNav"], [data-testid="stSidebar"],
[data-testid="stToolbar"], .stDeployButton {{ display:none !important; }}

.block-container {{
    padding: 2rem 1rem 2rem !important;
    max-width: 440px !important;
}}
[data-testid="stVerticalBlock"] > div {{ gap: 0 !important; }}
div[data-testid="stVerticalBlock"] > div:has(> div:empty) {{ display:none !important; }}

body::before {{
    content:''; position:fixed; width:450px; height:450px;
    top:-150px; left:-100px; border-radius:50%;
    background:radial-gradient(circle,{tv['aurora1']},transparent 70%);
    filter:blur(110px); pointer-events:none; z-index:0; opacity:.5;
}}
body::after {{
    content:''; position:fixed; width:350px; height:350px;
    bottom:-80px; right:-60px; border-radius:50%;
    background:radial-gradient(circle,{tv['aurora2']},transparent 70%);
    filter:blur(100px); pointer-events:none; z-index:0; opacity:.5;
}}

.stApp [data-testid="stAppViewBlockContainer"] > div > div > div > div {{
    position: relative; z-index: 1;
}}

.auth-logo {{
    font-family:'Inter',sans-serif; font-size:1rem; font-weight:800;
    display:flex; align-items:center; gap:8px;
    margin-bottom:28px;
}}
.auth-logo-icon {{
    width:28px; height:28px; border-radius:7px;
    background:linear-gradient(135deg,{tv['accent']},{tv['accent2']});
    display:flex; align-items:center; justify-content:center;
}}
.auth-logo-icon svg {{ width:16px; height:16px; fill:none; stroke:#fff; stroke-width:2; stroke-linecap:round; stroke-linejoin:round; }}
.auth-logo em {{
    font-style:normal;
    background:linear-gradient(135deg,{tv['accent']},{tv['accent2']});
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
}}
.auth-title {{
    font-family:'Inter',sans-serif; font-size:1.6rem; font-weight:800;
    color:{tv['heading']}; letter-spacing:-.5px; margin-bottom:4px;
}}
.auth-sub {{ color:{tv['muted']}; font-size:.85rem; margin-bottom:22px; }}

.socials {{ display:flex; gap:8px; margin-bottom:18px; }}
.soc-btn {{
    flex:1; height:40px; border-radius:8px;
    background:{tv['input_bg']}; border:1px solid {tv['border']};
    display:flex; align-items:center; justify-content:center;
    font-size:.82rem; font-weight:600; color:{tv['text']}; cursor:pointer; transition:all .2s ease;
}}
.soc-btn:hover {{ background:{tv['hover']}; }}

.divider {{
    display:flex; align-items:center; gap:10px;
    color:{tv['muted']}; font-size:.75rem; margin-bottom:18px;
}}
.divider::before,.divider::after {{ content:''; flex:1; height:1px; background:{tv['border']}; }}

.forgot {{ text-align:right; margin-bottom:14px; }}
.forgot a {{ font-size:.78rem; color:{tv['accent']}; cursor:pointer; text-decoration:none; }}

.switch-row {{ text-align:center; margin-top:12px; font-size:.82rem; color:{tv['muted']}; }}

div[data-testid="stTextInput"] {{ margin-bottom:10px !important; }}
div[data-testid="stTextInput"] label {{ display:none !important; }}
div[data-testid="stTextInput"] > div > div > input {{
    background: {tv['input_bg']} !important;
    border: 1px solid {tv['border']} !important;
    border-radius: 8px !important;
    color: {tv['heading']} !important;
    padding: 12px 14px !important;
    font-size: .88rem !important;
    font-family: 'Inter', sans-serif !important;
    caret-color: {tv['accent']} !important;
    transition: border .2s, box-shadow .2s, background .2s !important;
}}
div[data-testid="stTextInput"] > div > div > input::placeholder {{ color:{tv['muted']} !important; }}
div[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: {tv['accent']} !important;
    box-shadow: 0 0 0 3px rgba({','.join(str(int(tv['accent'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},.1) !important;
    outline: none !important;
}}

div.stButton > button {{
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    border: none !important;
    width: 100% !important;
    transition: all .25s cubic-bezier(.22,1,.36,1) !important;
}}
div.stButton.pri > button {{
    background: linear-gradient(135deg,{tv['accent']},{tv['accent2']}) !important;
    color: #fff !important; padding: 12px !important; font-size: .88rem !important;
    box-shadow: 0 4px 16px rgba(0,0,0,.12) !important;
}}
div.stButton.pri > button:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(0,0,0,.2) !important;
}}
div.stButton.ghost > button {{
    background: {tv['input_bg']} !important;
    color: {tv['text']} !important;
    border: 1px solid {tv['border']} !important;
    padding: 10px !important; font-size: .85rem !important;
}}
div.stButton.ghost > button:hover {{
    background: {tv['hover']} !important;
}}
div.stButton.back > button {{
    background: transparent !important;
    color: {tv['muted']} !important;
    border: 1px solid {tv['border']} !important;
    padding: 7px 14px !important; font-size: .78rem !important;
    width: auto !important; border-radius: 7px !important;
}}

div[data-testid="stAlert"] {{ border-radius:8px !important; margin-top:8px !important; }}
hr {{ border-color: {tv['border']} !important; margin: 20px 0 !important; }}
</style>
""", unsafe_allow_html=True)

mode = st.session_state["auth_mode"]

st.markdown('<div class="back">', unsafe_allow_html=True)
if st.button("← Home", key="back_home"):
    st.switch_page("main.py")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

spider_svg = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="3"/><path d="M12 2v4m0 12v4M2 12h4m12 0h4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>'

if mode == "signin":
    st.markdown(f"""
    <div class="auth-logo"><div class="auth-logo-icon">{spider_svg}</div>Web<em>Scraper</em></div>
    <div class="auth-title">Welcome back</div>
    <div class="auth-sub">Sign in to access your dashboard</div>
    <div class="socials">
        <div class="soc-btn">Google</div>
        <div class="soc-btn">GitHub</div>
        <div class="soc-btn">LinkedIn</div>
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
    st.markdown(f"""
    <div class="auth-logo"><div class="auth-logo-icon">{spider_svg}</div>Web<em>Scraper</em></div>
    <div class="auth-title">Create account</div>
    <div class="auth-sub">Start extracting data for free today</div>
    <div class="socials">
        <div class="soc-btn">Google</div>
        <div class="soc-btn">GitHub</div>
        <div class="soc-btn">LinkedIn</div>
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
                    st.success("Account created! Please sign in.")
                    st.session_state["auth_mode"] = "signin"
                    st.rerun()
                else:
                    st.error(f"{res.get('error','Unknown error')}")
        else:
            st.error("Fill all fields. Password must be at least 6 characters.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="switch-row">Already have an account?</div>', unsafe_allow_html=True)
    st.markdown('<div class="ghost" style="margin-top:8px">', unsafe_allow_html=True)
    if st.button("Sign in instead", key="go_signin", use_container_width=True):
        st.session_state["auth_mode"] = "signin"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
