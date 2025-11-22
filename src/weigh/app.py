# src/weigh/app.py
from __future__ import annotations

import time
import textwrap
from datetime import datetime, date, timezone
from pathlib import Path
from typing import List, Optional

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image

# ---- local imports ----
try:
    import logger_core
    import report_utils
    import db_backend
    import scale_backend
except Exception:
    from weigh import logger_core, report_utils, db_backend, scale_backend

ASSETS_DIR = Path(__file__).parent / "assets"
STYLE_CSS = ASSETS_DIR / "style.css"
PANTRY_LOGO = ASSETS_DIR / "slfp_logo.png"
SCALE_LOGO = ASSETS_DIR / "scale_icon.png"

# ---------------- Streamlit page config ----------------
st.set_page_config(
    page_title="Weigh Kiosk",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- helpers ----------------

def load_css(css_path: Path):
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_resource
def get_scale() -> "scale_backend.DymoHIDScale":
    return scale_backend.DymoHIDScale()

@st.cache_data(ttl=60.0)
def get_sources() -> List[str]:
    return sorted(logger_core.get_sources_dict().keys())

@st.cache_data(ttl=60.0)
def get_types() -> List[str]:
    return list(logger_core.get_types_dict().keys())

def get_daily_totals_line() -> str:
    totals = db_backend.get_daily_totals()
    if not totals:
        return "Today: 0.0 lbs"
    parts = [f"{k}: {v:.1f}" for k, v in totals.items()]
    return " | ".join(parts)

def get_history_html() -> str:
    """Generates a fixed-height table with exactly 15 rows."""
    limit = 15
    entries = logger_core.get_recent_entries(limit)
    
    rows_html = ""
    
    # 1. Render actual data rows
    for row in entries:
        try:
            dt = datetime.fromisoformat(row["timestamp"]).astimezone()
            ts_str = dt.strftime("%H:%M")
        except Exception:
            ts_str = row["timestamp"]

        rows_html += (
            f"<tr>"
            f"<td>{ts_str}</td>"
            f"<td>{row['source']}</td>"
            f"<td>{row['type']}</td>"
            f"<td>{row['weight_lb']:.2f} lb</td>"
            f"<td>Logged</td>"
            f"</tr>"
        )
    
    # 2. Render blank filler rows to maintain constant height
    slots_needed = limit - len(entries)
    if slots_needed > 0:
        blank_row = "<tr><td>&nbsp;</td><td></td><td></td><td></td><td></td></tr>"
        rows_html += blank_row * slots_needed

    return (
        f'<table class="history-table">'
        f'<thead><tr><th>Time</th><th>Source</th><th>Type</th><th>Weight</th><th>Action</th></tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table>'
    )

def load_logo(path: Path, height_px: int = 100) -> Optional[Image.Image]:
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    scale = height_px / float(h)
    return img.resize((int(w * scale), height_px), Image.LANCZOS)

def chunk_types(types: List[str]) -> List[List[str]]:
    if len(types) == 0: return []
    if len(types) <= 8: return [types]
    mid = (len(types) + 1) // 2
    return [types[:mid], types[mid:]]

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()

# ---------------- INIT ----------------
load_css(STYLE_CSS)

# Inject Keyboard Listener (Ctrl-Z / Ctrl-Y)
# This JS finds the buttons by their text content and clicks them.
components.html("""
<script>
const doc = window.parent.document;
doc.addEventListener('keydown', function(e) {
    // Ctrl+Z = Undo
    if (e.ctrlKey && e.key.toLowerCase() === 'z') {
        const buttons = Array.from(doc.querySelectorAll('button'));
        const undoBtn = buttons.find(el => el.innerText.includes("Undo Last Entry"));
        if (undoBtn) {
            undoBtn.click();
        }
    }
    // Ctrl+Y = Redo
    if (e.ctrlKey && e.key.toLowerCase() === 'y') {
        const buttons = Array.from(doc.querySelectorAll('button'));
        const redoBtn = buttons.find(el => el.innerText.includes("Redo Last Undo"));
        if (redoBtn) {
            redoBtn.click();
        }
    }
});
</script>
""", height=0, width=0)


# Sidebar
with st.sidebar:
    st.header("Admin")
    sources = get_sources()
    
    if "source" not in st.session_state:
        st.session_state.source = sources[0] if sources else "Unknown"
    
    current_idx = 0
    if st.session_state.source in sources:
        current_idx = sources.index(st.session_state.source)
        
    st.session_state.source = st.selectbox("Source", sources, index=current_idx)
    
    st.divider()
    
    # --- Undo / Redo ---
    c_undo, c_redo = st.columns(2)
    with c_undo:
        if st.button("Undo Last Entry"):
            logger_core.undo_last_entry()
            safe_rerun()
    with c_redo:
        if st.button("Redo Last Undo"):
            logger_core.redo_last_entry()
            safe_rerun()

    st.divider()
    
    # --- REPORTING SECTION ---
    st.subheader("Send Report")
    
    today = datetime.now(timezone.utc).date()
    d_start = st.date_input("Start Date", value=today)
    d_end = st.date_input("End Date", value=today)
    
    default_email = ""
    try:
        default_email = st.secrets["email"]["default_recipient"]
    except Exception:
        pass

    recipient = st.text_input("Recipient Email", value=default_email)

    # EMAIL BUTTON
    if st.button("Email CSV", type="primary"):
        if not recipient:
            st.error("Enter an email address.")
        else:
            with st.spinner("Sending email..."):
                try:
                    csv_bytes = report_utils.generate_report_csv(
                        d_start.isoformat(), d_end.isoformat()
                    )
                    fname = f"report_{d_start}_{d_end}.csv"
                    
                    report_utils.send_email_with_attachment(
                        to_email=recipient,
                        subject=f"Donation Report: {d_start} - {d_end}",
                        body=f"Attached is the donation log for {d_start} to {d_end}.",
                        attachment_bytes=csv_bytes,
                        filename=fname
                    )
                    st.success("Email Sent!")
                    time.sleep(2) 
                except Exception as e:
                    st.error(f"Error: {e}")

    st.caption("Or download directly:")
    csv_bytes_dl = report_utils.generate_report_csv(d_start.isoformat(), d_end.isoformat())
    st.download_button(
        "Download CSV",
        csv_bytes_dl,
        f"report_{d_start}_{d_end}.csv",
        "text/csv",
        use_container_width=True
    )

# Session State Defaults
if "last_refresh_t" not in st.session_state:
    st.session_state.last_refresh_t = 0.0

# ---------------- MAIN UI ----------------

# 1. Get Weight
try:
    scale = get_scale()
    reading = scale.get_latest()
    weight_str = f"{reading.value:.1f}" if reading and reading.unit == "lb" else "—"
except Exception:
    scale = None
    weight_str = "Err"

# 2. Top Row: Logo | Weight | Logo
c1, c2, c3 = st.columns([1, 5, 1], gap="small", vertical_alignment="center")

with c1:
    img = load_logo(PANTRY_LOGO, height_px=110)
    if img: st.image(img)

with c2:
    weight_ph = st.empty()
    weight_ph.markdown(f'<div class="weight-box">{weight_str}</div>', unsafe_allow_html=True)

with c3:
    img = load_logo(SCALE_LOGO, height_px=110)
    if img: st.image(img)

# 3. Buttons
types = get_types()
rows = chunk_types(types)

def on_log(tname):
    r = scale.read_stable_weight(timeout_s=0.5) if scale else None
    if r and r.unit == "lb":
        if r.value > 0.0:
            src = st.session_state.source
            logger_core.log_entry(r.value, src, tname)

for i, row in enumerate(rows):
    cols = st.columns(len(row), gap="small")
    for idx, tname in enumerate(row):
        cols[idx].button(tname, on_click=on_log, args=(tname,), use_container_width=True, key=f"btn_{i}_{idx}")

# 4. Daily Totals
totals_ph = st.empty()
totals_ph.markdown(f'<div class="totals-box">{get_daily_totals_line()}</div>', unsafe_allow_html=True)

# 5. History Table
history_ph = st.empty()
history_ph.markdown(get_history_html(), unsafe_allow_html=True)

# 6. Auto-Refresh
now = time.time()
if (now - st.session_state.last_refresh_t) > 0.5:
    st.session_state.last_refresh_t = now
    time.sleep(0.5)
    safe_rerun()

