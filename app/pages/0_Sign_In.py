import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="Sign In — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.styles import apply_theme, theme_selector
from utils.icons import icon

t = apply_theme()

if st.session_state.get("logged_in"):
    st.switch_page("pages/1_Dashboard.py")

# ── Supabase config ──
SUPABASE_URL = "https://srpzboswuixqzzyhsytq.supabase.co"

# ── Handle OAuth callback (tokens come in URL fragment → JS sends as query param) ──
token_from_params = st.query_params.get("access_token")
if token_from_params:
    st.session_state["logged_in"] = True
    st.session_state["supabase_token"] = token_from_params
    user_email = st.query_params.get("user_email", "OAuth User")
    st.session_state["user_email"] = user_email
    st.query_params.clear()
    st.success("Signed in via social login! Redirecting...")
    st.switch_page("pages/1_Dashboard.py")

# Build OAuth URLs — redirect_to sends user back to this page
import urllib.parse
_base = st.query_params.get("_host_url", "http://localhost:8501")
REDIRECT_URL = f"{_base}Sign_In"

def oauth_url(provider: str) -> str:
    return (
        f"{SUPABASE_URL}/auth/v1/authorize?"
        f"provider={provider}&redirect_to={urllib.parse.quote(REDIRECT_URL, safe='')}"
    )

GOOGLE_AUTH   = oauth_url("google")
GITHUB_AUTH   = oauth_url("github")
FACEBOOK_AUTH = oauth_url("facebook")
LINKEDIN_AUTH = oauth_url("linkedin_oidc")

st.markdown(f"""
<style>
[data-testid="stSidebar"] {{ display: none !important; }}
.block-container {{
    padding: 1rem 2rem 2rem !important;
    max-width: 100% !important;
}}
[data-testid="stTextInput"] > div > div > input {{
    background: {t['bg']} !important;
    border: 1.5px solid {t['border_l']} !important;
    border-radius: 10px !important;
    color: {t['text']} !important;
    padding: 0.7rem 1rem !important;
    font-size: 0.92rem !important;
}}
[data-testid="stTextInput"] > div > div > input:focus {{
    border-color: {t['accent']} !important;
    box-shadow: 0 0 0 3px {t['accent_glow']} !important;
}}
[data-testid="stTextInput"] > div > div > input::placeholder {{
    color: {t['muted']} !important;
}}
.signin-btn > div > button {{
    background: linear-gradient(135deg, {t['accent']}, {t['accent_h']}) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.75rem !important;
    box-shadow: 0 4px 20px {t['accent_glow']} !important;
    width: 100% !important;
    transform: none !important;
    filter: none !important;
}}
.signin-btn > div > button:hover {{
    background: linear-gradient(135deg, {t['accent_h']}, {t['accent']}) !important;
    box-shadow: 0 6px 28px {t['accent_glow']} !important;
}}
.signup-btn > div > button {{
    background: transparent !important;
    color: #fff !important;
    border: 2.5px solid #fff !important;
    border-radius: 10px !important;
    font-size: 0.9rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 0.65rem !important;
    box-shadow: none !important;
    width: 100% !important;
    transform: none !important;
    filter: none !important;
}}
.signup-btn > div > button:hover {{
    background: rgba(255,255,255,0.18) !important;
}}
.social-row {{
    display: flex;
    gap: 0.75rem;
    justify-content: center;
    margin: 0.75rem 0 1rem;
}}
.soc-btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 48px;
    height: 48px;
    border-radius: 12px;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.15s;
    text-decoration: none;
    flex-shrink: 0;
}}
.soc-btn:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}}
.soc-google {{
    background: #fff;
    border: 1.5px solid #ddd;
}}
.soc-facebook {{
    background: #1877F2;
}}
.soc-github {{
    background: #24292e;
}}
.soc-linkedin {{
    background: #0A66C2;
}}
</style>
""", unsafe_allow_html=True)

# ── JS: capture OAuth hash fragment and redirect with query params ──
st.markdown("""
<script>
(function() {
    if (window.location.hash && window.location.hash.includes('access_token')) {
        var hash = window.location.hash.substring(1);
        var params = new URLSearchParams(hash);
        var token = params.get('access_token');
        if (token) {
            var url = new URL(window.location.href.split('#')[0]);
            url.searchParams.set('access_token', token);
            window.location.replace(url.toString());
        }
    }
})();
</script>
""", unsafe_allow_html=True)

tb1, tb2, tb3 = st.columns([1, 7, 1])
with tb1:
    if st.button("Back", key="back_home"):
        st.switch_page("Home.py")
with tb3:
    theme_selector("si_theme")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

gap, left_col, right_col, gap2 = st.columns([0.5, 2.2, 1.8, 0.5])

with left_col:
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-radius:20px 20px 0 0;padding:2.5rem 2.5rem 1.2rem;
         text-align:center;">
      <div style="font-size:1.8rem;font-weight:800;letter-spacing:-0.03em;
           color:{t['text']};margin-bottom:0.25rem;">Sign In</div>
      <div style="font-size:0.82rem;color:{t['muted']};margin-bottom:0.75rem;">
        or use your email account
      </div>

      <!-- Social auth buttons — real OAuth links -->
      <div class="social-row">
        <a class="soc-btn soc-google" title="Continue with Google"
           href="{GOOGLE_AUTH}" target="_self">
          <svg width="22" height="22" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
        </a>
        <a class="soc-btn soc-facebook" title="Continue with Facebook"
           href="{FACEBOOK_AUTH}" target="_self">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="white">
            <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
          </svg>
        </a>
        <a class="soc-btn soc-github" title="Continue with GitHub"
           href="{GITHUB_AUTH}" target="_self">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="white">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0 24 12c0-6.63-5.37-12-12-12z"/>
          </svg>
        </a>
        <a class="soc-btn soc-linkedin" title="Continue with LinkedIn"
           href="{LINKEDIN_AUTH}" target="_self">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="white">
            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
          </svg>
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{t['card']};border-left:1px solid {t['border']};
         border-right:1px solid {t['border']};padding:0.5rem 2rem 0;">
    </div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown(f'<div style="background:{t["card"]};border-left:1px solid {t["border"]};border-right:1px solid {t["border"]};padding:0 2rem;">', unsafe_allow_html=True)
        email    = st.text_input("Email", placeholder="Your Email",  key="si_email", label_visibility="collapsed")
        password = st.text_input("Password", placeholder="Password", key="si_pass",  type="password", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{t['card']};border-left:1px solid {t['border']};
         border-right:1px solid {t['border']};padding:0.5rem 2rem 0;text-align:center;">
      <a href="/Forgot_Password" target="_self"
         style="font-size:0.88rem;color:{t['accent']};text-decoration:none;font-weight:600;
                display:inline-block;padding:0.3rem 1.5rem;">
        Forgot password?
      </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-top:none;border-radius:0 0 20px 20px;padding:0.5rem 2rem 1rem;">
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="signin-btn">', unsafe_allow_html=True)
    if st.button("SIGN IN", key="signin_btn", use_container_width=True):
        if email and password:
            st.session_state["logged_in"]  = True
            st.session_state["user_email"] = email
            st.success("Signed in! Redirecting...")
            st.switch_page("pages/1_Dashboard.py")
        else:
            st.error("Please enter your email and password.")
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    st.markdown(f"""
    <div style="background:linear-gradient(150deg,#12b8b0 0%,#0c7a90 45%,#0a4f72 100%);
         border-radius:20px;padding:3.5rem 2.5rem;min-height:420px;
         display:flex;flex-direction:column;align-items:center;
         justify-content:center;text-align:center;position:relative;overflow:hidden;">
      <div style="position:absolute;top:-60px;left:-50px;width:240px;height:240px;
           background:rgba(255,255,255,0.07);border-radius:50%;"></div>
      <div style="position:absolute;bottom:-80px;right:-40px;width:270px;height:270px;
           background:rgba(255,255,255,0.04);border-radius:50%;"></div>
      <div style="position:relative;z-index:2;">
        <div style="font-size:1.9rem;font-weight:800;color:#fff;
             margin-bottom:1rem;line-height:1.2;">Hello, Friend!</div>
        <p style="font-size:0.9rem;color:rgba(255,255,255,0.88);
             line-height:1.7;max-width:220px;margin:0 auto 2rem;">
          Register with your personal details to use all of the site features
        </p>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="signup-btn">', unsafe_allow_html=True)
    if st.button("SIGN UP", key="goto_signup", use_container_width=True):
        st.switch_page("pages/0_Sign_Up.py")
    st.markdown('</div>', unsafe_allow_html=True)

_, lnk, _ = st.columns([2, 3, 2])
with lnk:
    st.markdown(f"""
    <div style="text-align:center;margin-top:1.25rem;font-size:0.85rem;color:{t['text2']};">
      Don't have an account?&nbsp;
      <a href="/Sign_Up" style="color:{t['accent']};font-weight:600;text-decoration:none;">
        Create one now
      </a>
    </div>
    """, unsafe_allow_html=True)
