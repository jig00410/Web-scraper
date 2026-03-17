"""
Shared theme configuration for WebScraper.
Provides consistent professional theming across all pages.
"""
import streamlit as st

THEME_OPTIONS = {
    "dark": {
        "label": "Dark",
        "surface": "#0a0b0f",
        "card": "#12141a",
        "card2": "#181b22",
        "border": "rgba(255,255,255,0.06)",
        "border2": "rgba(255,255,255,0.10)",
        "text": "#b0bec5",
        "muted": "#546e7a",
        "heading": "#eceff1",
        "input_bg": "rgba(255,255,255,0.04)",
        "hover": "rgba(255,255,255,0.05)",
        "aurora1": "rgba(0,200,230,.08)",
        "aurora2": "rgba(100,80,220,.08)",
        "nav_bg": "rgba(10,11,15,.95)",
        "accent": "#00bcd4",
        "accent2": "#7c4dff",
        "accent3": "#00e676",
    },
    "light": {
        "label": "Light",
        "surface": "#f8f9fb",
        "card": "#ffffff",
        "card2": "#f1f3f5",
        "border": "rgba(0,0,0,0.07)",
        "border2": "rgba(0,0,0,0.10)",
        "text": "#37474f",
        "muted": "#78909c",
        "heading": "#1a1a2e",
        "input_bg": "rgba(0,0,0,0.03)",
        "hover": "rgba(0,0,0,0.03)",
        "aurora1": "rgba(0,200,230,.04)",
        "aurora2": "rgba(100,80,220,.04)",
        "nav_bg": "rgba(248,249,251,.96)",
        "accent": "#0097a7",
        "accent2": "#651fff",
        "accent3": "#00c853",
    },
    "multi": {
        "label": "Vivid",
        "surface": "#0d0a1f",
        "card": "rgba(18,14,40,0.92)",
        "card2": "rgba(26,22,52,0.90)",
        "border": "rgba(255,255,255,0.08)",
        "border2": "rgba(255,255,255,0.12)",
        "text": "#c5c0e0",
        "muted": "#7a75a0",
        "heading": "#ede8ff",
        "input_bg": "rgba(255,255,255,0.05)",
        "hover": "rgba(255,255,255,0.06)",
        "aurora1": "rgba(236,64,122,.10)",
        "aurora2": "rgba(0,200,200,.10)",
        "nav_bg": "rgba(13,10,31,.95)",
        "accent": "#ec407a",
        "accent2": "#26c6da",
        "accent3": "#69f0ae",
    },
}

def init_theme():
    """Initialize theme in session state if not set."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"
    return st.session_state["theme"]

def get_theme_vars(theme=None):
    """Return theme variables dict for current or given theme."""
    if theme is None:
        theme = st.session_state.get("theme", "dark")
    return THEME_OPTIONS.get(theme, THEME_OPTIONS["dark"])

def get_bg_css(tv, theme=None):
    """Return background CSS for body."""
    if theme is None:
        theme = st.session_state.get("theme", "dark")
    if theme == "multi":
        return f"background:linear-gradient(135deg, #0d0a1f, #1a1040, #0d0a1f) !important; background-attachment:fixed !important;"
    return f"background:{tv['surface']} !important;"

def render_theme_toggle_css(tv):
    """Return CSS for the professional theme toggle."""
    return f"""
    .theme-toggle {{
        display:flex; gap:2px;
        background:{tv['input_bg']};
        border-radius:8px; padding:3px;
        border:1px solid {tv['border']};
    }}
    .theme-btn {{
        padding:6px 14px; border-radius:6px; border:none; cursor:pointer;
        font-family:'DM Sans',sans-serif; font-size:.75rem; font-weight:600;
        letter-spacing:.3px; transition:all .25s ease;
    }}
    .theme-btn.active {{
        background:linear-gradient(135deg,{tv['accent']},{tv['accent2']});
        color:#000; box-shadow:0 2px 8px rgba(0,0,0,.2);
    }}
    .theme-btn:not(.active) {{
        background:transparent; color:{tv['muted']};
    }}
    .theme-btn:not(.active):hover {{
        color:{tv['heading']}; background:{tv['hover']};
    }}
    """

def render_theme_toggle_html():
    """Render the theme toggle as HTML. Must be paired with Streamlit buttons for actual switching."""
    theme = st.session_state.get("theme", "dark")
    dark_cls = "active" if theme == "dark" else ""
    light_cls = "active" if theme == "light" else ""
    multi_cls = "active" if theme == "multi" else ""
    return f"""
    <div class="theme-toggle">
        <button class="theme-btn {dark_cls}" onclick="void(0)" id="theme-dark">Dark</button>
        <button class="theme-btn {light_cls}" onclick="void(0)" id="theme-light">Light</button>
        <button class="theme-btn {multi_cls}" onclick="void(0)" id="theme-multi">Vivid</button>
    </div>
    """

def theme_switcher_buttons(location="nav", key_prefix="main"):
    """Render Streamlit columns with theme switching buttons."""
    theme = st.session_state.get("theme", "dark")
    cols = st.columns(3)
    changed = False
    with cols[0]:
        if st.button("◼ Dark" if theme == "dark" else "Dark", key=f"{key_prefix}_dark", use_container_width=True):
            st.session_state["theme"] = "dark"
            changed = True
    with cols[1]:
        if st.button("◻ Light" if theme == "light" else "Light", key=f"{key_prefix}_light", use_container_width=True):
            st.session_state["theme"] = "light"
            changed = True
    with cols[2]:
        if st.button("◈ Vivid" if theme == "multi" else "Vivid", key=f"{key_prefix}_multi", use_container_width=True):
            st.session_state["theme"] = "multi"
            changed = True
    if changed:
        st.rerun()
