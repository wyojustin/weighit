# app.py
from __future__ import annotations

import time
from datetime import datetime, date, timezone
from pathlib import Path
from typing import List, Optional

import streamlit as st
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
    # Format: "Bread: 4.2 | Dairy: 10.5"
    parts = [f"{k}: {v:.1f}" for k, v in totals.items()]
    return " | ".join(parts)

def load_logo(path: Path, height_px: int = 100) -> Optional[Image.Image]:
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    scale = height_px / float(h)
    return img.resize((int(w * scale), height_px), Image.LANCZOS)

def chunk_types(types: List[str]) -> List[List[str]]:
    """Split types into exactly 1 or 2 rows."""
    if len(types) == 0:
        return []
    if len(types) <= 5:
        return [types]
    # Ceiling division to balance rows
    mid = (len(types) + 1) // 2
    return [types[:mid], types[mid:]]

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()

# ---------------- INIT ----------------
load_css(STYLE_CSS)

# Sidebar
with st.sidebar:
    st.header("Admin")
    sources = get_sources()
    
    # Default selection logic
    if "source" not in st.session_state:
        st.session_state.source = sources[0] if sources else "Unknown"
    
    # Ensure selected source is valid
    current_idx = 0
    if st.session_state.source in sources:
        current_idx = sources.index(st.session_state.source)
        
    st.session_state.source = st.selectbox("Source", sources, index=current_idx)
    
    st.divider()
    
    # Undo Button in Sidebar
    if st.button("Undo Last Entry"):
        logger_core.undo_last_entry()
        st.session_state.status_msg = "↩️ Undid last entry"
        safe_rerun()

    st.divider()
    
    # --- REPORT EXPORT ---
    st.subheader("Export Report")
    
    # Defaults to today
    today = datetime.now(timezone.utc).date()
    
    d_start = st.date_input("Start Date", value=today)
    d_end = st.date_input("End Date", value=today)

    # Generate the CSV bytes immediately based on the date pickers
    csv_bytes = report_utils.generate_report_csv(d_start.isoformat(), d_end.isoformat())
    file_name = f"weigh_report_{d_start}_{d_end}.csv"

    # Direct download button (no nested if st.button check)
    st.download_button(
        label="Download CSV",
        data=csv_bytes,
        file_name=file_name,
        mime="text/csv",
        use_container_width=True
    )

# Session State Defaults
if "status_msg" not in st.session_state:
    st.session_state.status_msg = ""
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
# [1, 5, 1] ratio keeps the text centered and large
c1, c2, c3 = st.columns([1, 5, 1], gap="small", vertical_alignment="center")

with c1:
    img = load_logo(PANTRY_LOGO, height_px=110)
    if img: st.image(img)

with c2:
    st.markdown(f'<div class="weight-box">{weight_str}</div>', unsafe_allow_html=True)

with c3:
    img = load_logo(SCALE_LOGO, height_px=110)
    if img: st.image(img)

# 3. Buttons
types = get_types()
rows = chunk_types(types)

def on_log(tname):
    r = scale.read_stable_weight(timeout_s=0.5) if scale else None
    if r and r.unit == "lb":
        src = st.session_state.source
        logger_core.log_entry(r.value, src, tname)
        st.session_state.status_msg = f"Logged {r.value:.1f} lbs to {src} — {tname}"
    else:
        st.session_state.status_msg = "⚠️ Scale Error"

# Render Rows
for i, row in enumerate(rows):
    cols = st.columns(len(row), gap="small")
    for idx, tname in enumerate(row):
        cols[idx].button(tname, on_click=on_log, args=(tname,), use_container_width=True, key=f"btn_{i}_{idx}")

# 4. Daily Totals
st.markdown(f'<div class="totals-box">{get_daily_totals_line()}</div>', unsafe_allow_html=True)

# 5. Status Bar (Last element)
msg = st.session_state.status_msg
if msg:
    if "Logged" in msg:
        st.success(msg, icon="✅")
    elif "Undid" in msg:
        st.warning(msg, icon="↩️")
    else:
        st.error(msg, icon="⚠️")
else:
    # Invisible placeholder to prevent layout jump
    st.markdown("<div style='height: 52px;'></div>", unsafe_allow_html=True)

# 6. Auto-Refresh Loop
now = time.time()
if (now - st.session_state.last_refresh_t) > 0.2:
    st.session_state.last_refresh_t = now
    time.sleep(0.2)
    safe_rerun()
    
