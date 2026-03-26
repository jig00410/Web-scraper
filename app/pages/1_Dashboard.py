import streamlit as st, time, sys, os, io
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
st.set_page_config(page_title="Dashboard — WebScraper Pro", page_icon="🌐",
                   layout="wide", initial_sidebar_state="collapsed")
from utils.layout import setup_page
from utils.icons import icon
from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_processor import process_html
from scraper.tag_tree_builder import build_tag_tree
from scraper.tag_tree_optimizer import optimize_tag_tree
from scraper.content_extractor import extract_content_by_tags
from scraper.url_validator import validate_url
from llm.tag_selector import select_relevant_tags
from llm.data_processor import process_extracted_data

def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Data")
    return buf.getvalue()

def gen_ai_analysis(df):
    n_rows, n_cols = df.shape
    lines = [
        "Dataset Overview", "================",
        f"Rows: {n_rows}    Columns: {n_cols}",
        f"Columns: {', '.join(df.columns.tolist())}", "",
        "Column Summaries", "----------------",
    ]
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            lines.append(f"{col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}, nulls={df[col].isna().sum()}")
        else:
            top = df[col].value_counts().head(3).index.tolist()
            lines.append(f"{col}: {df[col].nunique()} unique. Top: {', '.join(str(v) for v in top)}. Nulls: {df[col].isna().sum()}")
    lines += [
        "", "Recommendations", "---------------",
        f"* {n_rows} rows — {'sufficient' if n_rows > 50 else 'small dataset, consider collecting more'}.",
        f"* {sum(1 for c in df.columns if df[c].isna().any())} columns contain nulls.",
        f"* Numeric cols for charting: {', '.join(c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])) or 'none detected'}.",
    ]
    return "\n".join(lines)

t, main = setup_page("Dashboard")

# Extra CSS specific to dashboard layout
st.markdown(f"""
<style>
/* Give main content area consistent padding */
.dash-wrap {{ padding: 1rem 1.4rem; }}
/* Metric row gap control */
[data-testid="stHorizontalBlock"] [data-testid="stColumn"] {{
    padding: 0 0.3rem !important;
}}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child {{
    padding-left: 0 !important;
}}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child {{
    padding-right: 0 !important;
}}
/* Prevent nav column from getting inner padding override */
[data-testid="stAppViewContainer"] > .main
  [data-testid="stHorizontalBlock"]:first-child
  > [data-testid="stColumn"]:first-child {{
    padding: 0 !important;
}}
/* Tighten vertical gap between Streamlit elements inside main */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"] > div.element-container {{
    margin-bottom: 0 !important;
    padding-bottom: 0 !important;
}}
</style>
""", unsafe_allow_html=True)

with main:

    # ── Page Header ───────────────────────────────────────────────────────────
    st.markdown(f"""
<div class="dash-wrap" style="padding-bottom:0.5rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.5rem;">
    <div>
      <div style="font-size:0.63rem;color:{t['muted']};font-weight:700;text-transform:uppercase;
           letter-spacing:0.1em;margin-bottom:3px;">AI-Powered Data</div>
      <div class="PT">Web Scraping Dashboard</div>
      <div class="PS" style="margin-bottom:0;">Extract, upload, and analyze website data in real-time.</div>
    </div>
    <span class="BG G">
      <span style="width:6px;height:6px;border-radius:50%;background:{t['green']};
            display:inline-block;box-shadow:0 0 5px {t['green']};"></span>
      Systems Online
    </span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Metrics Row ───────────────────────────────────────────────────────────
    st.markdown(f'<div class="dash-wrap" style="padding-top:0.6rem;padding-bottom:0.6rem;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        st.metric("Data Accuracy", "—", "ExtractoML")
    with c2:
        st.metric("Total Rows Extracted", "0", "No jobs yet")
    with c3:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.85rem 1.1rem;border-top:3px solid {t['accent']};height:100%;">
  <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
       letter-spacing:0.06em;color:{t['text2']};margin-bottom:0.3rem;">Proxy Status</div>
  <div style="display:flex;align-items:center;gap:8px;">
    <span style="width:9px;height:9px;border-radius:50%;background:{t['green']};
          box-shadow:0 0 6px {t['green']};display:inline-block;flex-shrink:0;"></span>
    <span style="font-size:1.3rem;font-weight:700;color:{t['text']};">Active</span>
  </div>
  <div style="font-size:0.68rem;color:{t['muted']};margin-top:3px;">3 proxies rotating</div>
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Main Content: Left (scraper form) + Right (schema/export) ─────────────
    st.markdown(f'<div class="dash-wrap" style="padding-top:0;">', unsafe_allow_html=True)
    lc, rc = st.columns([3, 1], gap="small")

    with lc:
        # New Project card header
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.75rem 1.1rem 0.5rem;margin-bottom:0.4rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.55rem;display:flex;align-items:center;gap:7px;">
    {icon('search',13,t['accent'])} New Project
  </div>
</div>
""", unsafe_allow_html=True)

        # URL + Category row
        uc, cc = st.columns([3, 1], gap="small")
        with uc:
            url = st.text_input("URL", placeholder="Enter Website URL to Scrape",
                                label_visibility="collapsed", key="dash_url")
            query = st.text_area("❓ Enter Query (What do you want to extract?)")
        with cc:
            st.selectbox("Category", ["E-commerce", "News Articles", "Job Listings", "Custom"],
                         label_visibility="collapsed", key="dash_cat")

        # Format + Buttons row
        fc, bc, dc = st.columns([1.5, 1, 1], gap="small")
        with fc:
            fmt = st.selectbox("Format", ["CSV", "JSON", "Excel"],
                               label_visibility="collapsed", key="dash_fmt")
        with bc:
            start = st.button("▶  Start Scraping", use_container_width=True, key="dash_start")

        if start:
            if not url:
                st.warning("⚠️ Please enter a URL first!")
                st.stop()

    # Query input
    query = st.text_input("What do you want to extract?",
                          placeholder="e.g. Get all product names and prices",
                          key="dash_query")

    if not query:
        st.info("👆 Enter what you want to extract, then click Start Scraping again.")
        st.stop()

    pb  = st.progress(0)
    st_t = st.empty()
    con  = st.empty()
    lines = []

    def log(msg, pct):
        pb.progress(pct)
        st_t.markdown(f'<p style="color:{t["text2"]};font-size:0.82rem;margin:0;">{msg}</p>',
                      unsafe_allow_html=True)
        lines.append(f'<span style="color:{t["muted"]};">[{time.strftime("%H:%M:%S")}]</span>'
                     f' <span style="color:{t["green"]};">{msg}</span>')
        con.markdown(f'<div class="CB">{"<br>".join(lines)}</div>', unsafe_allow_html=True)

    try:
        # Step 1: Validate URL
        log("🔍 Validating URL...", 10)
        is_valid = validate_url(url)
        if not is_valid:
            st.error("❌ Invalid or unreachable URL!")
            st.stop()

        # Step 2: Launch browser
        log("🚀 Launching Playwright browser...", 20)
        playwright, browser = launch_browser()

        try:
            # Step 3: Load page
            log("🌐 Loading page...", 35)
            raw_html = load_page(browser, url)

            # Step 4: Process HTML
            log("🧹 Cleaning HTML...", 50)
            soup = process_html(raw_html)

            # Step 5: Build tag tree
            log("🌳 Building tag tree...", 60)
            tag_tree = build_tag_tree(soup)
            tag_tree = optimize_tag_tree(tag_tree)

            # Step 6: LLM tag selection
            log("🤖 AI selecting relevant tags...", 72)
            selected_tags = select_relevant_tags(query, tag_tree)

            # Step 7: Extract content
            log("📦 Extracting content...", 85)
            extracted_data = extract_content_by_tags(soup, selected_tags)

            # Step 8: Final LLM processing
            log("✨ AI processing final output...", 95)
            final_output = process_extracted_data(query, extracted_data)

            log("✅ Done!", 100)
            pb.empty()
            st_t.empty()

            st.success(f"✅ Scraping complete! Extracted {len(extracted_data)} items.")

            # Show final output
            st.markdown("### 📊 Extracted Data")
            st.write(final_output)

            # Save to session for export
            if isinstance(extracted_data, list) and len(extracted_data) > 0:
                df = pd.DataFrame(extracted_data)
                st.session_state["dashboard_df"] = df

                # Export buttons
                dl1, dl2, dl3 = st.columns(3, gap="small")
                with dl1:
                    st.download_button("⬇ CSV", df.to_csv(index=False),
                                       "data.csv", "text/csv",
                                       use_container_width=True)
                with dl2:
                    st.download_button("⬇ JSON", df.to_json(orient="records"),
                                       "data.json", "application/json",
                                       use_container_width=True)
                with dl3:
                    st.download_button("⬇ Excel", to_excel(df),
                                       "data.xlsx",
                                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       use_container_width=True)

        finally:
            close_browser(playwright, browser)

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

    with rc:
        # Data Schema card — empty until data is loaded
        st.markdown(f"""
<div class="C" style="margin-bottom:0.5rem;">
  <div style="font-size:0.84rem;font-weight:700;color:{t['text']};
       margin-bottom:0.5rem;display:flex;align-items:center;gap:6px;">
    {icon('table',12,t['accent'])} Data Schema
  </div>
  <div style="font-size:0.78rem;color:{t['muted']};text-align:center;padding:1.5rem 0;">
    No data loaded yet.<br>Run a scrape or upload a file.
  </div>
</div>
""", unsafe_allow_html=True)

        # Export Data card
        st.markdown(f"""
<div class="C">
  <div style="font-size:0.84rem;font-weight:700;color:{t['text']};
       margin-bottom:0.6rem;display:flex;align-items:center;gap:6px;">
    {icon('download',12,t['accent'])} Export Data
  </div>
  <div style="font-size:0.78rem;color:{t['muted']};text-align:center;padding:1rem 0;">
    Load data first to enable export.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── Upload Section ────────────────────────────────────────────────────────
    st.markdown(f'<div class="dash-wrap" style="padding-top:0.3rem;">', unsafe_allow_html=True)
    st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem;margin-bottom:0.5rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.6rem;display:flex;align-items:center;gap:7px;">
    {icon('upload',13,t['accent'])} Upload & Analyze Data
  </div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop file here",
        type=["csv", "json", "xlsx", "xls", "png", "jpg", "jpeg", "pdf"],
        key="dash_uploader",
        label_visibility="visible",
        help="Supports CSV, JSON, Excel, Images, PDF",
    )

    if uploaded_file is not None:
        fname = uploaded_file.name
        fsize = uploaded_file.size
        ext = fname.rsplit(".", 1)[-1].lower()

        st.markdown(f"""
<div style="display:flex;align-items:center;gap:10px;background:{t['bg2']};
     border:1px solid {t['border']};border-radius:10px;padding:0.55rem 0.85rem;
     margin:0.4rem 0 0.5rem;">
  {icon('file-text',15,t['accent'])}
  <div style="flex:1;min-width:0;">
    <div style="font-size:0.81rem;font-weight:600;color:{t['text']};
         white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{fname}</div>
    <div style="font-size:0.68rem;color:{t['muted']};">{fsize/1024:.1f} KB · {ext.upper()}</div>
  </div>
  <span class="BG G">{icon('check-circle',9,t['green'])} Ready</span>
</div>
""", unsafe_allow_html=True)

        df = None
        if ext == "csv":
            try: df = pd.read_csv(uploaded_file)
            except Exception as e: st.error(f"CSV parse error: {e}")
        elif ext in ("xlsx", "xls"):
            try: df = pd.read_excel(uploaded_file, engine="openpyxl")
            except Exception as e: st.error(f"Excel parse error: {e}")
        elif ext == "json":
            try: df = pd.read_json(uploaded_file)
            except Exception as e: st.error(f"JSON parse error: {e}")
        elif ext in ("png", "jpg", "jpeg"):
            st.image(uploaded_file, caption=fname, width=380)
        elif ext == "pdf":
            st.info("PDF uploaded.")
            st.download_button("Download PDF", uploaded_file.read(), fname, "application/pdf")

        if df is not None:
            st.markdown(f"""
<div style="font-size:0.76rem;color:{t['text2']};margin-bottom:0.35rem;">
  Preview — <strong style="color:{t['text']};">{fname}</strong>
  &nbsp;·&nbsp; {df.shape[0]} rows × {df.shape[1]} columns
</div>
""", unsafe_allow_html=True)
            st.dataframe(df.head(5), use_container_width=True, height=185)
            st.session_state["dashboard_df"] = df

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Data Analysis Canvas ──────────────────────────────────────────────────
    canvas_df = st.session_state.get("dashboard_df")
    if canvas_df is not None:
        st.markdown(f'<div class="dash-wrap" style="padding-top:0.2rem;">', unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem 0.5rem;margin-bottom:0.5rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.6rem;display:flex;align-items:center;gap:7px;">
    {icon('bar-chart',13,t['accent'])} Data Analysis Canvas
    <span style="font-size:0.69rem;font-weight:500;color:{t['text2']};margin-left:auto;">
      {canvas_df.shape[0]} rows × {canvas_df.shape[1]} cols
    </span>
  </div>
""", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["📋  Table View", "📊  Charts", "🤖  AI Analysis"])

        with tab1:
            st.dataframe(canvas_df, use_container_width=True, height=280)
            dl_a, dl_b, dl_c = st.columns(3, gap="small")
            with dl_a:
                st.download_button("⬇ CSV", canvas_df.to_csv(index=False),
                                   "export.csv", "text/csv", use_container_width=True)
            with dl_b:
                st.download_button("⬇ JSON", canvas_df.to_json(orient="records"),
                                   "export.json", "application/json", use_container_width=True)
            with dl_c:
                st.download_button("⬇ Excel", to_excel(canvas_df), "export.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True)

        with tab2:
            all_cols = canvas_df.columns.tolist()
            num_cols = [c for c in all_cols if pd.api.types.is_numeric_dtype(canvas_df[c])]
            if len(all_cols) < 2:
                st.info("Need at least 2 columns for charts.")
            else:
                ch1, ch2 = st.columns(2, gap="small")
                with ch1:
                    x_col = st.selectbox("X Axis", all_cols, key="chart_x")
                with ch2:
                    y_col = st.selectbox("Y Axis (numeric)", num_cols if num_cols else all_cols,
                                         index=0, key="chart_y")
                cdf = canvas_df[[x_col, y_col]].copy()
                if not pd.api.types.is_numeric_dtype(cdf[y_col]):
                    cdf[y_col] = pd.to_numeric(cdf[y_col], errors="coerce")
                cdf = cdf.dropna().set_index(x_col)
                if cdf.empty:
                    st.warning("No plottable data with selected columns.")
                else:
                    bt1, bt2 = st.tabs(["Bar Chart", "Line Chart"])
                    with bt1: st.bar_chart(cdf, use_container_width=True)
                    with bt2: st.line_chart(cdf, use_container_width=True)

        with tab3:
            with st.spinner("Generating AI analysis…"):
                time.sleep(0.25)
                analysis_text = gen_ai_analysis(canvas_df)
            st.markdown(f"""
<div style="background:{t['bg2']};border:1px solid {t['border']};border-radius:10px;
     padding:0.9rem 1.1rem;font-family:'JetBrains Mono',monospace;font-size:0.76rem;
     color:{t['text2']};line-height:1.85;white-space:pre-wrap;
     max-height:280px;overflow-y:auto;margin-bottom:0.5rem;">
{analysis_text}
</div>
""", unsafe_allow_html=True)
            st.download_button("⬇ Download Analysis (.txt)", analysis_text,
                               "ai_analysis.txt", "text/plain")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Recent Jobs Table ─────────────────────────────────────────────────────
    st.markdown(f'<div class="dash-wrap" style="padding-top:0.2rem;">', unsafe_allow_html=True)

    jobs = st.session_state.get("recent_jobs", [])

    th_s = (f"text-align:left;padding:0.45rem 0.75rem;font-size:0.65rem;font-weight:700;"
            f"color:{t['muted']};text-transform:uppercase;letter-spacing:0.07em;"
            f"border-bottom:1px solid {t['border']};")
    th_html = "".join(f'<th style="{th_s}">{h}</th>'
                      for h in ["URL", "Category", "Rows", "Accuracy", "Status", "Time"])

    if jobs:
        bm = {"G": (t['accent_glow'], t['green']),
              "A": (t['accent_glow'],          t['accent']),
              "P": ("rgba(139,92,246,0.14)",   t['purple'])}
        cm = {"E-commerce": ("rgba(59,130,246,0.14)", t['blue']),
              "News":        ("rgba(139,92,246,0.14)", t['purple']),
              "Jobs":        (t['accent_glow'],        t['accent'])}
        td_s = f"padding:0.6rem 0.75rem;border-bottom:1px solid {t['border']};"
        rows_html = ""
        for u, cat, rn, acc, col, stat, dur in jobs:
            bg, fg = bm.get(col, bm["G"])
            cbg, cfg = cm.get(cat, bm["G"])
            rows_html += (
                f'<tr>'
                f'<td style="{td_s}font-family:monospace;font-size:0.7rem;color:{t["text"]};">{u}</td>'
                f'<td style="{td_s}"><span style="background:{cbg};color:{cfg};padding:2px 7px;border-radius:20px;font-size:0.67rem;font-weight:600;">{cat}</span></td>'
                f'<td style="{td_s}color:{t["text"]};font-weight:600;font-size:0.82rem;">{rn}</td>'
                f'<td style="{td_s}color:{t["text2"]};font-size:0.82rem;">{acc}</td>'
                f'<td style="{td_s}"><span style="background:{bg};color:{fg};padding:2px 7px;border-radius:20px;font-size:0.67rem;font-weight:600;">{stat}</span></td>'
                f'<td style="{td_s}color:{t["text2"]};font-size:0.82rem;">{dur}</td>'
                f'</tr>'
            )
        body_html = rows_html
    else:
        body_html = f'<tr><td colspan="6" style="text-align:center;padding:2.5rem;color:{t["muted"]};font-size:0.83rem;">No scraping jobs yet. Start a new project above.</td></tr>'

    st.markdown(f"""
<div class="C" style="overflow-x:auto;margin-bottom:1.2rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.65rem;display:flex;align-items:center;gap:7px;">
    {icon('list-checks',13,t['accent'])} Recent Scraping Jobs
  </div>
  <table style="width:100%;border-collapse:collapse;">
    <thead><tr>{th_html}</tr></thead>
    <tbody>{body_html}</tbody>
  </table>
</div>
""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
