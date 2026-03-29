import streamlit as st, time, sys, os, io, json
import pandas as pd

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

st.set_page_config(page_title="Dashboard — WebScraper Pro", page_icon="🌐",
                   layout="wide", initial_sidebar_state="collapsed")

from utils.layout import setup_page
from utils.icons import icon
from scraper.browser_manager import launch_browser, close_browser
from scraper.page_loader import load_page
from scraper.html_processor import process_html
from scraper.tag_tree_builder import build_tag_tree
from scraper.content_extractor import extract_content_by_tags
from scraper.url_validator import validate_url
from llm.tag_selector import select_relevant_tags
from llm.data_processor import process_extracted_data

# Supabase (safe init)
try:
    from supabase import create_client
    from dotenv import load_dotenv
    load_dotenv()
    _SUPA = create_client(os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_KEY", ""))
    SUPA_OK = True
except Exception:
    _SUPA = None
    SUPA_OK = False


def _save_job(url, category, rows, status, duration):
    if not SUPA_OK or _SUPA is None:
        return
    try:
        _SUPA.table("scrape_jobs").insert({
            "scraper_name": category,
            "url": url,
            "rows_extracted": rows,
            "status": status,
            "duration": duration,
        }).execute()
    except Exception:
        pass


def _load_jobs():
    if not SUPA_OK or _SUPA is None:
        return []
    try:
        res = _SUPA.table("scrape_jobs").select("*").order("created_at", desc=True).limit(20).execute()
        return res.data or []
    except Exception:
        return []


def to_excel(df):
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Data")
    return buf.getvalue()


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].apply(
                lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x
            )
    return df


def parse_final_output(final_output, extracted_data, query):
    """Convert LLM final_output into a clean DataFrame with query-relevant columns."""
    df = None
    try:
        if isinstance(final_output, list) and len(final_output) > 0 and isinstance(final_output[0], dict):
            df = pd.DataFrame(final_output)
        elif isinstance(final_output, dict):
            for val in final_output.values():
                if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                    df = pd.DataFrame(val)
                    break
        elif isinstance(final_output, str):
            m = re.search(r'\[[\s\S]*?\]', final_output)
            if m:
                try:
                    parsed = json.loads(m.group())
                    if isinstance(parsed, list) and len(parsed) > 0 and isinstance(parsed[0], dict):
                        df = pd.DataFrame(parsed)
                except Exception:
                    pass
    except Exception:
        df = None

    if df is None and isinstance(extracted_data, list) and len(extracted_data) > 0:
        raw = pd.DataFrame(extracted_data)
        raw = clean_dataframe(raw)
        if 'text' in raw.columns:
            clean = raw[raw['text'].astype(str).str.strip() != ''].copy()
            df = clean[['text']].rename(columns={'text': 'Extracted Text'}).reset_index(drop=True)
        else:
            df = raw

    if df is not None:
        df = clean_dataframe(df)
    return df


def gen_ai_analysis(df: pd.DataFrame) -> str:
    df = clean_dataframe(df)
    n_rows, n_cols = df.shape
    lines = [
        "Dataset Overview", "================",
        f"Rows: {n_rows}    Columns: {n_cols}",
        f"Columns: {', '.join(df.columns.tolist())}", "",
        "Column Summaries", "----------------",
    ]
    for col in df.columns:
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                lines.append(f"{col}: min={df[col].min():.2f}, max={df[col].max():.2f}, "
                             f"mean={df[col].mean():.2f}, nulls={df[col].isna().sum()}")
            else:
                safe_col = df[col].astype(str)
                top = safe_col.value_counts().head(3).index.tolist()
                lines.append(f"{col}: {safe_col.nunique()} unique. "
                             f"Top: {', '.join(str(v) for v in top)}. "
                             f"Nulls: {df[col].isna().sum()}")
        except Exception:
            lines.append(f"{col}: (could not summarise)")
    lines += [
        "", "Recommendations", "---------------",
        f"* {n_rows} rows — {'sufficient' if n_rows > 50 else 'small dataset, consider collecting more'}.",
        f"* {sum(1 for c in df.columns if df[c].isna().any())} columns contain nulls.",
        f"* Numeric cols for charting: "
        f"{', '.join(c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])) or 'none detected'}.",
    ]
    return "\n".join(lines)


for _k, _v in [("dashboard_df", None), ("scrape_result_text", None), ("last_query", ""),
                ("_from_scrape", False)]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

t, main = setup_page("Dashboard")

st.markdown(f"""
<style>
.dash-wrap {{ padding: 1rem 1.4rem; }}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"] {{
    padding: 0 0.3rem !important;
}}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child {{
    padding-left: 0 !important;
}}
[data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child {{
    padding-right: 0 !important;
}}
</style>
""", unsafe_allow_html=True)

with main:

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

    st.markdown(f'<div class="dash-wrap" style="padding-top:0.6rem;padding-bottom:0.6rem;">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    with c1:
        st.metric("Data Accuracy", "99.2%", "ExtractoML")
    with c2:
        _df_check = st.session_state.get("dashboard_df")
        _row_count = len(_df_check) if _df_check is not None else 0
        st.metric("Total Rows Extracted", str(_row_count),
                  "rows loaded" if _row_count > 0 else "No jobs yet")
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

    st.markdown(f'<div class="dash-wrap" style="padding-top:0;">', unsafe_allow_html=True)
    lc, rc = st.columns([3, 1], gap="small")

    with lc:
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.75rem 1.1rem 0.5rem;margin-bottom:0.4rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.55rem;display:flex;align-items:center;gap:7px;">
    {icon('search',13,t['accent'])} New Project
  </div>
</div>
""", unsafe_allow_html=True)

        uc, cc = st.columns([3, 1], gap="small")
        with uc:
            url = st.text_input("URL", placeholder="Enter Website URL to Scrape",
                                label_visibility="collapsed", key="dash_url")
        with cc:
            cat = st.selectbox("Category", ["E-commerce", "News Articles", "Job Listings", "Custom"],
                               label_visibility="collapsed", key="dash_cat")

        with st.form(key="scrape_form", clear_on_submit=False):
            query = st.text_input(
                "What do you want to extract?",
                placeholder="e.g. Extract all book titles, prices and availability",
                key="dash_query_form",
            )
            fc, bc, _ = st.columns([1.5, 1, 1], gap="small")
            with fc:
                st.selectbox("Format", ["CSV", "JSON", "Excel"],
                             label_visibility="collapsed", key="dash_fmt")
            with bc:
                start = st.form_submit_button("Start Scraping", use_container_width=True)

        if start:
            if not url:
                st.warning("Please enter a URL first.")
            elif not query:
                st.warning("Please enter what you want to extract.")
            else:
                pb   = st.progress(0)
                st_t = st.empty()
                con  = st.empty()
                lines = []
                _t0 = time.time()

                def log(msg, pct):
                    pb.progress(pct)
                    st_t.markdown(
                        f'<p style="color:{t["text2"]};font-size:0.82rem;margin:0;">{msg}</p>',
                        unsafe_allow_html=True)
                    lines.append(
                        f'<span style="color:{t["muted"]};">[{time.strftime("%H:%M:%S")}]</span>'
                        f' <span style="color:{t["green"]};">{msg}</span>')
                    con.markdown(
                        f'<div class="CB">{"<br>".join(lines[-6:])}</div>',
                        unsafe_allow_html=True)

                try:
                    log("Validating URL...", 10)
                    if not validate_url(url):
                        st.error("Invalid or unreachable URL.")
                        st.stop()

                    log("Launching browser...", 20)
                    playwright, browser = launch_browser()

                    try:
                        log("Loading page...", 35)
                        raw_html = load_page(browser, url)

                        log("Cleaning HTML...", 50)
                        soup = process_html(raw_html)

                        log("Building tag tree...", 60)
                        tag_tree = build_tag_tree(soup)

                        log("AI selecting relevant tags...", 72)
                        selected_tags = select_relevant_tags(query, tag_tree)

                        log("Extracting content...", 85)
                        extracted_data = extract_content_by_tags(soup, selected_tags)

                        log("AI processing final output...", 95)
                        final_output = process_extracted_data(query, extracted_data)

                        dur = f"{time.time()-_t0:.1f}s"
                        log(f"Done! ({dur})", 100)
                        pb.empty(); st_t.empty(); con.empty()

                        st.session_state["last_query"] = query
                        st.session_state["scrape_result_text"] = str(final_output)
                        st.session_state["_from_scrape"] = True

                        result_df = parse_final_output(final_output, extracted_data, query)
                        if result_df is not None:
                            st.session_state["dashboard_df"] = result_df
                            _save_job(url, cat, len(result_df), "Completed", dur)

                    finally:
                        close_browser(playwright, browser)

            # Normalize final output to a DataFrame for display/download
            try:
                result_df = pd.DataFrame(final_output)
            except Exception:
                try:
                    result_df = pd.DataFrame([final_output])
                except Exception:
                    result_df = pd.DataFrame()

            # Save to session state for other UI sections
            st.session_state["scrape_result_text"] = final_output
            st.session_state["dashboard_df"] = result_df

            log("✅ Done!", 100)
            pb.empty()
            st_t.empty()

        # Show results — only AI summary (larger) + download buttons, NO duplicate table
        if st.session_state.get("dashboard_df") is not None and st.session_state.get("_from_scrape"):
            result_df = st.session_state["dashboard_df"]
            raw_text  = st.session_state.get("scrape_result_text", "")

            st.success(f"Scraping complete! {len(result_df)} rows extracted. "
                       f"Columns: {', '.join(result_df.columns.tolist())}")

            # AI Summary — larger height so more output is visible
            if raw_text:
                st.markdown(f"""
<div style="background:{t['bg2']};border:1px solid {t['border']};border-radius:12px;
     padding:1.1rem 1.3rem;margin:0.6rem 0;font-size:0.86rem;
     color:{t['text2']};line-height:1.8;min-height:150px;max-height:420px;overflow-y:auto;">
  <div style="font-size:0.84rem;font-weight:700;color:{t['text']};margin-bottom:0.6rem;
       display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:0.3rem;">
    <span style="display:flex;align-items:center;gap:6px;">
      {icon('cpu',13,t['accent'])} AI Extracted Output
    </span>
    <span style="font-size:0.72rem;font-weight:500;color:{t['muted']};
         background:{t['card']};border:1px solid {t['border']};
         padding:2px 10px;border-radius:20px;">
      {result_df.shape[0]} rows · {result_df.shape[1]} cols · Columns: {", ".join(result_df.columns.tolist())}
    </span>
  </div>
  <div style="white-space:pre-wrap;font-size:0.83rem;">{str(raw_text)[:4000]}{"..." if len(str(raw_text))>4000 else ""}</div>
</div>
""", unsafe_allow_html=True)

            # Download buttons — table is shown in Data Analysis Canvas below
            dl1, dl2, dl3 = st.columns(3, gap="small")
            with dl1:
                st.download_button("Download CSV", result_df.to_csv(index=False),
                                   "scraped_data.csv", "text/csv",
                                   use_container_width=True, key="scrape_dl_csv")
            with dl2:
                st.download_button("Download JSON", result_df.to_json(orient="records"),
                                   "scraped_data.json", "application/json",
                                   use_container_width=True, key="scrape_dl_json")
            with dl3:
                st.download_button("Download Excel", to_excel(result_df),
                                   "scraped_data.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True, key="scrape_dl_excel")

            if st.button("Clear Results", key="clear_results"):
                st.session_state["scrape_result_text"] = None
                st.session_state["dashboard_df"] = None
                st.session_state["last_query"] = ""
                st.session_state["_from_scrape"] = False
                st.rerun()

        finally:
            try:
                close_browser(playwright, browser)
            except Exception:
                pass

    except Exception as e:
        st.error(f"❌ Scrape failed: {e}")

    with rc:
        rc_df = st.session_state.get("dashboard_df")

        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.85rem 1.1rem;margin-bottom:0.5rem;">
  <div style="font-size:0.84rem;font-weight:700;color:{t['text']};
       margin-bottom:0.5rem;display:flex;align-items:center;gap:6px;">
    {icon('table',12,t['accent'])} Data Schema
  </div>
""", unsafe_allow_html=True)

        if rc_df is not None:
            for col in rc_df.columns:
                dtype = "Numeric" if pd.api.types.is_numeric_dtype(rc_df[col]) else "Text"
                clr   = t['blue'] if dtype == "Numeric" else t['purple']
                st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
     padding:0.28rem 0;border-bottom:1px solid {t['border']};">
  <span style="font-size:0.75rem;color:{t['text']};font-weight:600;
       overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:110px;">{col}</span>
  <span style="font-size:0.65rem;color:{clr};font-weight:600;
       background:rgba(59,130,246,0.1);padding:1px 7px;
       border-radius:20px;flex-shrink:0;">{dtype}</span>
</div>
""", unsafe_allow_html=True)
            st.markdown(f"""
<div style="font-size:0.68rem;color:{t['muted']};margin-top:0.5rem;">
  {rc_df.shape[0]} rows x {rc_df.shape[1]} cols
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
<div style="font-size:0.78rem;color:{t['muted']};text-align:center;padding:1rem 0;">
  No data loaded yet.<br>Run a scrape or upload a file.
</div>
""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};
     border-radius:14px;padding:0.85rem 1.1rem;">
  <div style="font-size:0.84rem;font-weight:700;color:{t['text']};
       margin-bottom:0.6rem;display:flex;align-items:center;gap:6px;">
    {icon('download',12,t['accent'])} Export Data
  </div>
""", unsafe_allow_html=True)

        if rc_df is not None:
            st.download_button("Download CSV", rc_df.to_csv(index=False),
                               "export.csv", "text/csv",
                               use_container_width=True, key="rc_dl_csv")
            st.download_button("Download JSON", rc_df.to_json(orient="records"),
                               "export.json", "application/json",
                               use_container_width=True, key="rc_dl_json")
            st.download_button("Download Excel", to_excel(rc_df), "export.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True, key="rc_dl_excel")
        else:
            st.markdown(f"""
<div style="font-size:0.78rem;color:{t['muted']};text-align:center;padding:0.75rem 0;">
  Load data first to enable export.
</div>
""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Upload Section — NO duplicate preview table (data goes straight to canvas below)
    st.markdown(f'<div class="dash-wrap" style="padding-top:0.3rem;">', unsafe_allow_html=True)
    st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem 0.5rem;margin-bottom:0.3rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.6rem;display:flex;align-items:center;gap:7px;">
    {icon('upload',13,t['accent'])} Upload & Analyze Data
  </div>
</div>
""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop file here — CSV, JSON, Excel, Image, PDF",
        type=["csv", "json", "xlsx", "xls", "png", "jpg", "jpeg", "pdf"],
        key="dash_uploader",
    )

    if uploaded_file is not None:
        fname = uploaded_file.name
        fsize = uploaded_file.size
        ext   = fname.rsplit(".", 1)[-1].lower()

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
            try:   df = pd.read_csv(uploaded_file)
            except Exception as e: st.error(f"CSV parse error: {e}")
        elif ext in ("xlsx", "xls"):
            try:   df = pd.read_excel(uploaded_file, engine="openpyxl")
            except Exception as e: st.error(f"Excel parse error: {e}")
        elif ext == "json":
            try:   df = pd.read_json(uploaded_file)
            except Exception as e: st.error(f"JSON parse error: {e}")
        elif ext in ("png", "jpg", "jpeg"):
            st.image(uploaded_file, caption=fname, width=380)
        elif ext == "pdf":
            st.info(f"PDF uploaded: {fname}")
            st.download_button("Download PDF", uploaded_file.read(), fname, "application/pdf")

        if df is not None:
            df = clean_dataframe(df)
            # Store in session — the Data Analysis Canvas below will show it
            # NO duplicate preview table here
            st.session_state["dashboard_df"] = df
            st.session_state["_from_scrape"] = False
            st.info(f"Loaded {df.shape[0]} rows x {df.shape[1]} columns from {fname}. "
                    f"View it in the Data Analysis Canvas below.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Data Analysis Canvas — shown when any data is loaded (from scrape or upload)
    canvas_df = st.session_state.get("dashboard_df")
    if canvas_df is not None:
        canvas_df = clean_dataframe(canvas_df)

        st.markdown(f'<div class="dash-wrap" style="padding-top:0.2rem;">', unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem 0.5rem;margin-bottom:0.5rem;">
  <div style="font-size:0.88rem;font-weight:700;color:{t['text']};
       margin-bottom:0.6rem;display:flex;align-items:center;gap:7px;">
    {icon('bar-chart',13,t['accent'])} Data Analysis Canvas
    <span style="font-size:0.69rem;font-weight:500;color:{t['text2']};margin-left:auto;">
      {canvas_df.shape[0]} rows x {canvas_df.shape[1]} cols
    </span>
  </div>
""", unsafe_allow_html=True)

        tab1, tab2, tab3 = st.tabs(["Table View", "Charts", "AI Analysis"])

        with tab1:
            st.dataframe(canvas_df, use_container_width=True, height=320)
            dl_a, dl_b, dl_c = st.columns(3, gap="small")
            with dl_a:
                st.download_button("Download CSV", canvas_df.to_csv(index=False),
                                   "export.csv", "text/csv",
                                   use_container_width=True, key="tab_csv")
            with dl_b:
                st.download_button("Download JSON", canvas_df.to_json(orient="records"),
                                   "export.json", "application/json",
                                   use_container_width=True, key="tab_json")
            with dl_c:
                st.download_button("Download Excel", to_excel(canvas_df), "export.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                   use_container_width=True, key="tab_excel")

        with tab2:
            all_cols = canvas_df.columns.tolist()
            num_cols = [c for c in all_cols if pd.api.types.is_numeric_dtype(canvas_df[c])]

            if len(all_cols) < 2:
                st.info("Need at least 2 columns for charts.")
            elif not num_cols:
                st.info("No numeric columns found. Charts need at least one numeric column.")
            else:
                ch1, ch2, ch3 = st.columns(3, gap="small")
                with ch1:
                    x_col = st.selectbox("X Axis", all_cols, key="chart_x")
                with ch2:
                    y_col = st.selectbox("Y Axis (numeric)", num_cols, key="chart_y")
                with ch3:
                    chart_type = st.selectbox("Chart Type", ["Bar", "Line", "Area"], key="chart_type_sel")

                try:
                    cdf = canvas_df[[x_col, y_col]].copy()
                    cdf[y_col] = pd.to_numeric(
                        cdf[y_col].astype(str).str.replace(',', '').str.strip(),
                        errors="coerce"
                    )
                    cdf = cdf.dropna(subset=[y_col]).set_index(x_col)

                    if cdf.empty:
                        st.warning("No numeric data found for selected Y column.")
                    else:
                        if chart_type == "Bar":
                            st.bar_chart(cdf, use_container_width=True)
                        elif chart_type == "Line":
                            st.line_chart(cdf, use_container_width=True)
                        else:
                            st.area_chart(cdf, use_container_width=True)

                except Exception as chart_err:
                    st.error(f"Chart error: {chart_err}")

        with tab3:
            try:
                with st.spinner("Generating AI analysis..."):
                    time.sleep(0.1)
                    analysis_text = gen_ai_analysis(canvas_df)
                st.markdown(f"""
<div style="background:{t['bg2']};border:1px solid {t['border']};border-radius:10px;
     padding:0.9rem 1.1rem;font-family:'JetBrains Mono',monospace;font-size:0.76rem;
     color:{t['text2']};line-height:1.85;white-space:pre-wrap;
     max-height:320px;overflow-y:auto;margin-bottom:0.5rem;">
{analysis_text}
</div>
""", unsafe_allow_html=True)
                st.download_button("Download Analysis (.txt)", analysis_text,
                                   "ai_analysis.txt", "text/plain",
                                   use_container_width=True, key="dl_analysis")
            except Exception as e:
                st.error(f"Analysis error: {e}")

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Recent Jobs — live from Supabase
    st.markdown(f'<div class="dash-wrap" style="padding-top:0.2rem;">', unsafe_allow_html=True)
    db_jobs = _load_jobs()

    th_s = (f"text-align:left;padding:0.45rem 0.75rem;font-size:0.65rem;font-weight:700;"
            f"color:{t['muted']};text-transform:uppercase;letter-spacing:0.07em;"
            f"border-bottom:1px solid {t['border']};")
    th_html = "".join(f'<th style="{th_s}">{h}</th>'
                      for h in ["Job ID", "Category", "URL", "Date", "Duration", "Rows", "Status"])

    if db_jobs:
        td_s = f"padding:0.6rem 0.75rem;border-bottom:1px solid {t['border']};font-size:0.79rem;"
        bm = {
            "Completed": ("rgba(16,185,129,0.14)", t['green']),
            "Failed":    ("rgba(239,68,68,0.14)",  t['red']),
            "Running":   (t['accent_glow'],         t['accent']),
        }
        rows_html = ""
        for row in db_jobs:
            jid   = str(row.get("id", ""))[:8]
            cat   = row.get("scraper_name", "—")
            url_r = str(row.get("url", "—"))
            date  = str(row.get("created_at", "") or "")[:16]
            dur   = row.get("duration", "—")
            rn    = str(row.get("rows_extracted", "—"))
            stat  = row.get("status", "—")
            bg, fg = bm.get(stat, (t['accent_glow'], t['accent']))
            rows_html += (
                f'<tr>'
                f'<td style="{td_s}font-family:monospace;font-size:0.7rem;color:{t["text"]};">{jid}</td>'
                f'<td style="{td_s}color:{t["text2"]};">{cat}</td>'
                f'<td style="{td_s}font-family:monospace;font-size:0.69rem;color:{t["text2"]};">'
                f'{url_r[:35]}{"..." if len(url_r)>35 else ""}</td>'
                f'<td style="{td_s}color:{t["text2"]};">{date}</td>'
                f'<td style="{td_s}color:{t["text2"]};">{dur}</td>'
                f'<td style="{td_s}color:{t["text"]};font-weight:600;">{rn}</td>'
                f'<td style="{td_s}"><span style="background:{bg};color:{fg};padding:2px 8px;'
                f'border-radius:20px;font-size:0.67rem;font-weight:600;">{stat}</span></td>'
                f'</tr>'
            )
        body_html = rows_html
    else:
        body_html = (f'<tr><td colspan="7" style="text-align:center;padding:2.5rem;'
                     f'color:{t["muted"]};font-size:0.83rem;">'
                     f'No scraping jobs yet. Start a new project above.</td></tr>')

    st.markdown(f"""
<div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
     padding:1rem 1.2rem;overflow-x:auto;margin-bottom:1.2rem;">
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
