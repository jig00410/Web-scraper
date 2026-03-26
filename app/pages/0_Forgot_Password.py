import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.styles import apply_theme
from utils.icons import icon

t = apply_theme()

st.markdown(f"""
<style>
[data-testid="stSidebar"] {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)

_, col, _ = st.columns([1, 2, 1])
with col:
    st.markdown(f"""
    <div style="text-align:center;padding:2rem 0 1rem;">
      <div style="font-size:1.5rem;font-weight:800;color:{t['text']};">Reset Password</div>
      <div style="font-size:0.85rem;color:{t['muted']};margin-top:0.3rem;">
        Enter your email to receive a reset link
      </div>
    </div>
    """, unsafe_allow_html=True)

    email = st.text_input("Email Address", placeholder="Enter your email", key="fp_email")

    if st.button("Send Reset Link", use_container_width=True, key="fp_send"):
        if not email:
            st.error("Please enter your email.")
        elif "@" not in email:
            st.error("Please enter a valid email.")
        else:
            st.success(f"✅ Reset link sent to {email}!")
            st.info("Check your inbox. (Firebase integration needed for real emails)")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Sign In", use_container_width=True, key="fp_back"):
        st.switch_page("pages/0_Sign_In.py")