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

# ── Full page CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
[data-testid="stSidebar"] {{ display: none !important; }}

.block-container {{
    padding: 1rem 2rem 2rem !important;
    max-width: 100% !important;
}}

/* Back button */
div[data-testid="stButton"] button[kind="secondary"],
.back-btn > div > button {{
    background: {t['bg2']} !important;
    color: {t['text2']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    padding: 0.35rem 0.9rem !important;
    transform: none !important;
}}

/* All inputs on this page */
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

/* SIGN IN button */
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

/* SIGN UP button (teal outline) */
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
    gap: 0.65rem;
    justify-content: center;
    margin: 0.5rem 0 1rem;
}}
.soc-icon {{
    width: 44px; height: 44px;
    border-radius: 10px;
    border: 1.5px solid {t['border_l']};
    background: {t['bg']};
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; transition: all 0.2s; text-decoration: none;
    font-weight: 800; font-size: 15px;
}}
.soc-icon:hover {{
    border-color: #12b8b0;
    transform: translateY(-2px);
    background: {t['bg2']};
}}
</style>
""", unsafe_allow_html=True)

# ── Top bar ────────────────────────────────────────────────────────────────────
tb1, tb2, tb3 = st.columns([1, 7, 1])
with tb1:
    if st.button("← Back", key="back_home"):
        st.switch_page("Home.py")
with tb3:
    theme_selector("si_theme")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Two-column card layout ─────────────────────────────────────────────────────
# Each side is a full self-contained column — NO nested HTML with inputs inside
gap, left_col, right_col, gap2 = st.columns([0.5, 2.2, 1.8, 0.5])

# ══════════════════════════════════════════
#  LEFT COL — dark panel with sign-in form
# ══════════════════════════════════════════
with left_col:
    # Top dark card shell
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-radius:20px 20px 0 0;padding:2.5rem 2.5rem 1.5rem;
         text-align:center;">

      <div style="font-size:1.8rem;font-weight:800;letter-spacing:-0.03em;
           color:{t['text']};margin-bottom:0.25rem;">Sign In</div>
      <div style="font-size:0.82rem;color:{t['muted']};margin-bottom:1rem;">
        or use your email account
      </div>

      <!-- Social icons -->
      <div class="social-row">
        <a class="soc-icon" title="Google">
          <span style="color:#EA4335;font-family:Georgia,serif;">G</span>
        </a>
        <a class="soc-icon" title="Facebook">
          <span style="color:#1877F2;">f</span>
        </a>
        <a class="soc-icon" title="GitHub">
          <svg width="17" height="17" viewBox="0 0 24 24" fill="{t['text2']}">
            <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205
            11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555
            -3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02
            -.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305
            3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925
            0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315
            3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23
            3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225
            0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22
            0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0 0
            24 12c0-6.63-5.37-12-12-12z"/>
          </svg>
        </a>
        <a class="soc-icon" title="LinkedIn">
          <span style="color:#0A66C2;font-size:13px;font-weight:900;">in</span>
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Form area — continuation of dark card
    st.markdown(f"""
    <div style="background:{t['card']};border-left:1px solid {t['border']};
         border-right:1px solid {t['border']};padding:0 2.5rem;">
    </div>
    """, unsafe_allow_html=True)

    # Streamlit inputs rendered directly in column (no wrapping div)
    with st.container():
        st.markdown(f'<div style="background:{t["card"]};border-left:1px solid {t["border"]};border-right:1px solid {t["border"]};padding:0 2rem;">', unsafe_allow_html=True)
        email    = st.text_input("Email", placeholder="Your Email",  key="si_email", label_visibility="collapsed")
        password = st.text_input("Password", placeholder="Password", key="si_pass", type="password", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)

    # Forgot password + Sign In button — bottom of dark card
    st.markdown(f"""
    <div style="background:{t['card']};border:1px solid {t['border']};
         border-top:none;border-radius:0 0 20px 20px;
         padding:0.25rem 2.5rem 0.5rem;text-align:center;">
    </div>
    """, unsafe_allow_html=True)

    # Button logic for switching page
    if st.button("Forgot Your Password?", key="forgot_pw", type="secondary"):
        st.switch_page("pages/0_Forgot_Password.py")

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

    st.markdown(f"""
    <div style="text-align:center;margin-top:0.5rem;
         font-size:0.75rem;color:{t['muted']};">
      Demo: enter any email + password
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════
#  RIGHT COL — teal gradient welcome panel
# ══════════════════════════════════════════
with right_col:
    st.markdown(f"""
    <div style="background:linear-gradient(150deg,#12b8b0 0%,#0c7a90 45%,#0a4f72 100%);
         border-radius:20px;padding:3.5rem 2.5rem;min-height:420px;
         display:flex;flex-direction:column;align-items:center;
         justify-content:center;text-align:center;position:relative;overflow:hidden;">

      <!-- Decorative circles -->
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

# ── Bottom link ────────────────────────────────────────────────────────────────
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
