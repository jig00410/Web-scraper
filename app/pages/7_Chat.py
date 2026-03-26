"""
app/pages/7_Chat.py — WebScraper Pro · AI Chat Assistant

FIXES:
  1. groq_client.call_llm_api now correctly forwards list prompts (system +
     history + user) without stringifying them. Chat history works properly.
  2. Layout rebuilt: sessions in left panel using native Streamlit containers,
     chat messages using st.chat_message() for correct visual alignment.
  3. st.chat_input() placed at page level (not inside st.columns) so it always
     sticks to the bottom and doesn't break on rerun.
"""

import streamlit as st
import time, sys, os

_here = os.path.dirname(os.path.abspath(__file__))
_app  = os.path.dirname(_here)
_root = os.path.dirname(_app)
for _p in (_root, _app):
    if _p not in sys.path:
        sys.path.insert(0, _p)

st.set_page_config(
    page_title="Chat — WebScraper Pro",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.layout import setup_page
from utils.icons  import icon
from llm.groq_client import call_llm_api

# ── System prompt ─────────────────────────────────────────────────────────────
_SYSTEM = """You are the AI assistant for WebScraper Pro, an AI-driven web scraping platform.

Your role:
- Help users design scraping strategies (CSS selectors, HTML tags, class names)
- Explain Dashboard features: URL input, query box, export buttons
- Advise on Data Analysis: chart types, column selection, AI Analysis tab
- Explain Scheduler: frequency options (hourly/daily/weekly), export format
- Answer questions about export formats: CSV, JSON, Excel
- Debug scraping issues: 0 items extracted, wrong data, selector problems

Key platform facts:
- Uses Playwright headless browser + Groq LLaMA 3.3 70B for intelligence
- Scraping modes: E-commerce, News, Job Listings, Custom
- Data Analysis Canvas: Table View, Charts (bar/line), AI Analysis
- Cache layer prevents duplicate LLM calls (saves tokens)

Tone: concise, expert, friendly. Use markdown. Show selector examples like:
{"tag": "span", "attrs": {"class": "price_color"}}
"""


def _llm_response(user_msg: str, history: list) -> str:
    """Call Groq with system prompt + full history."""
    messages = [{"role": "system", "content": _SYSTEM}]
    for m in history[-40:]:   # cap at 20 exchanges
        messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": user_msg})
    try:
        reply = call_llm_api(prompt=messages, temperature=0.45, max_tokens=1024)
        return reply or "I couldn't generate a response. Please try again."
    except Exception as e:
        err = str(e)
        if "GROQ_API_KEY" in err or "not configured" in err.lower():
            return ("⚠️ **Groq API key not found.**\n\n"
                    "Add it to `.env`:\n```\nGROQ_API_KEY=gsk_...\n```\n"
                    "Get a free key at [console.groq.com](https://console.groq.com).")
        return f"⚠️ LLM error: {err}"


# ── Session helpers ───────────────────────────────────────────────────────────
def _init():
    st.session_state.setdefault("chat_sessions", [])
    st.session_state.setdefault("active_sid", None)
    st.session_state.setdefault("chat_messages", {})


def _new_session():
    sid = f"s_{int(time.time()*1000)}"
    st.session_state.chat_sessions.insert(0, {
        "id": sid, "title": "New Chat", "ts": time.strftime("%b %d, %H:%M")
    })
    st.session_state.chat_messages[sid] = []
    st.session_state.active_sid = sid


_init()
t, main = setup_page("Chat")

# ── Ensure a session exists ───────────────────────────────────────────────────
if not st.session_state.chat_sessions:
    _new_session()
ids = [s["id"] for s in st.session_state.chat_sessions]
if st.session_state.active_sid not in ids:
    st.session_state.active_sid = st.session_state.chat_sessions[0]["id"]

sid      = st.session_state.active_sid
messages = st.session_state.chat_messages.get(sid, [])

# ════════════════════════════════════════════════════════════════════════════════
#  Page layout: header + two columns
# ════════════════════════════════════════════════════════════════════════════════
with main:

    # ── Page header ───────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="padding:0.9rem 1.4rem 0.5rem;">
  <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:40px;height:40px;flex-shrink:0;
         background:linear-gradient(135deg,{t['accent']},{t['purple']});
         border-radius:12px;display:flex;align-items:center;justify-content:center;">
      {icon('bot', 20, '#fff')}
    </div>
    <div>
      <div class="PT" style="margin:0;">AI Chat Assistant</div>
      <div class="PS" style="margin:0;">Powered by Groq · LLaMA 3.3 70B</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    left_col, right_col = st.columns([1, 3], gap="small")

    # ══════════════════════════════════════════════════════════════════════════
    #  LEFT — Session panel
    # ══════════════════════════════════════════════════════════════════════════
    with left_col:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.75rem;height:78vh;overflow-y:auto;">
  <div style="font-size:0.7rem;font-weight:700;color:{t['muted']};
       text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.6rem;
       padding-bottom:0.4rem;border-bottom:1px solid {t['border']};">
    {icon('clock', 10, t['muted'])}&nbsp; Sessions
  </div>
""", unsafe_allow_html=True)

        if st.button("＋  New Chat", key="new_chat_btn", use_container_width=True):
            _new_session()
            st.rerun()

        st.markdown("<div style='margin-top:0.4rem;'>", unsafe_allow_html=True)

        for sess in st.session_state.chat_sessions:
            is_active = sess["id"] == sid
            msgs      = st.session_state.chat_messages.get(sess["id"], [])
            preview   = next((m["content"][:30] + "…" for m in msgs if m["role"] == "user"), "")

            accent_border = f"border-left:3px solid {t['accent']};" if is_active else ""
            bg            = t.get("card_hover", t["bg2"]) if is_active else "transparent"

            st.markdown(f"""
<div style="background:{bg};{accent_border}border-radius:8px;
     padding:0.5rem 0.65rem;margin-bottom:0.25rem;">
  <div style="font-size:0.75rem;font-weight:{'700' if is_active else '500'};
       color:{t['accent'] if is_active else t['text']};
       white-space:nowrap;overflow:hidden;text-overflow:ellipsis;
       max-width:100%;">{sess['title']}</div>
  <div style="font-size:0.65rem;color:{t['muted']};margin-top:2px;">{sess['ts']}</div>
  {f'<div style="font-size:0.64rem;color:{t["text2"]};margin-top:2px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{preview}</div>' if preview else ''}
</div>
""", unsafe_allow_html=True)

            if not is_active:
                if st.button("Open", key=f"open_{sess['id']}", use_container_width=True):
                    st.session_state.active_sid = sess["id"]
                    st.rerun()

        st.markdown("</div></div>", unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    #  RIGHT — Chat area
    # ══════════════════════════════════════════════════════════════════════════
    with right_col:

        # ── Chat message window ───────────────────────────────────────────────
        chat_container = st.container(height=560, border=False)

        with chat_container:
            if not messages:
                # Welcome screen
                st.markdown(f"""
<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
     padding:3rem 1rem;text-align:center;min-height:400px;">
  <div style="width:60px;height:60px;
       background:linear-gradient(135deg,{t['accent']},{t['purple']});
       border-radius:16px;display:flex;align-items:center;justify-content:center;
       margin-bottom:1rem;box-shadow:0 8px 24px rgba(0,0,0,0.2);">
    {icon('sparkles', 28, '#fff')}
  </div>
  <div style="font-size:1.15rem;font-weight:700;color:{t['text']};margin-bottom:0.4rem;">
    How can I help you today?</div>
  <div style="font-size:0.84rem;color:{t['text2']};max-width:400px;line-height:1.6;">
    Ask me about scraping strategies, data analysis, scheduling, or debugging.</div>
  <div style="display:flex;flex-wrap:wrap;gap:0.5rem;justify-content:center;margin-top:1.2rem;">
    {''.join(f'<span style="background:{t["bg2"]};border:1px solid {t["border"]};'
             f'border-radius:20px;padding:5px 14px;font-size:0.76rem;'
             f'color:{t["text2"]};cursor:pointer;">{h}</span>'
             for h in ["How do I scrape a site?","Fix 0 items extracted",
                       "Schedule a daily job","What selectors work for Amazon?"])}
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                # Render conversation with native st.chat_message
                for msg in messages:
                    if msg["role"] == "user":
                        with st.chat_message("user"):
                            st.markdown(msg["content"])
                    else:
                        with st.chat_message("assistant", avatar="🤖"):
                            st.markdown(msg["content"])

        # ── Input bar (always at bottom of right column) ──────────────────────
        user_input = st.chat_input(
            "Ask anything about scraping, data, or automation…",
            key=f"chat_input_{sid}",
        )

        if user_input:
            # Auto-title session from first message
            for s in st.session_state.chat_sessions:
                if s["id"] == sid and s["title"] == "New Chat":
                    s["title"] = user_input[:30] + ("…" if len(user_input) > 30 else "")
                    break

            # Store user message
            st.session_state.chat_messages[sid].append(
                {"role": "user", "content": user_input}
            )

            # Get LLM response (history without the just-appended message)
            history_for_llm = st.session_state.chat_messages[sid][:-1]

            with st.spinner("Thinking…"):
                ai_reply = _llm_response(user_input, history_for_llm)

            # Store assistant message
            st.session_state.chat_messages[sid].append(
                {"role": "assistant", "content": ai_reply}
            )
            st.rerun()