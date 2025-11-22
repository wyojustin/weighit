# app.py
"""
Streamlit GUI for weigh.

Run from this directory:
    streamlit run app.py

Design goals (MVP):
- Full-screen, touch-friendly.
- Top row: pantry logo | HUGE live weight | scale logo.
- Middle: compact donation type buttons (1 row if <=6, else 2 rows).
- Sidebar: source selector + report generation.
- Bottom: today's totals in ONE LINE, smaller font.
- Status area stays at bottom and does NOT shove buttons around.
- No "stable pending" UI; scale seems stable enough in practice.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import streamlit as st
from PIL import Image

# ---- local imports (non-relative to avoid Streamlit "no known parent" issues) ----
try:
    import logger_core
    import report_utils
    import db_backend
    import scale_backend
except Exception:
    # fallback if run from repo root with package on path
    from weigh import logger_core, report_utils, db_backend, scale_backend  # type: ignore

ASSETS_DIR = Path(__file__).parent / "assets"
STYLE_PATH = ASSETS_DIR / "style.css"

PANTRY_LOGO = ASSETS_DIR / "slfp_logo.png"
SCALE_LOGO = ASSETS_DIR / "scale_icon.png"

# ---------------- Streamlit page config ----------------
st.set_page_config(
    page_title="Weigh Food Logger",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------- CSS ----------------
DEFAULT_CSS = """
/* Overall app */
html, body, [class*="css"] {
  font-size: 18px;
}

/* hide Streamlit chrome */
header, footer { visibility: hidden; height: 0px; }

/* reduce padding top */
.block-container {
  padding-top: 0.4rem;
  padding-bottom: 0.2rem;
  padding-left: 0.6rem;
  padding-right: 0.6rem;
}

/* Make buttons compact + touch friendly */
div.stButton > button {
  height: 64px !important;          /* shorter than before */
  padding: 0px 8px !important;      /* thinner L/R */
  margin: 0px !important;
  font-size: 22px !important;
  font-weight: 700 !important;
  border-radius: 10px !important;
}

/* tighten column gaps (Streamlit still adds some) */
[data-testid="column"] {
  padding-left: 2px !important;
  padding-right: 2px !important;
}

/* Huge weight value */
.weight-box {
  text-align: center;
  font-size: 96px;   /* BIG */
  font-weight: 800;
  line-height: 1.0;
  margin-top: 8px;
}

/* Smaller totals line */
.totals-line {
  font-size: 18px;
  font-weight: 600;
  opacity: 0.9;
  padding-top: 4px;
}

/* Status area at bottom */
.status-area {
  font-size: 20px;
  font-weight: 700;
  color: #0b7d2a; /* green-ish */
  padding-top: 6px;
}
"""

if STYLE_PATH.exists():
    st.markdown(f"<style>{STYLE_PATH.read_text()}</style>", unsafe_allow_html=True)
else:
    st.markdown(f"<style>{DEFAULT_CSS}</style>", unsafe_allow_html=True)

# ---------------- helpers ----------------

@st.cache_resource
def get_scale() -> "scale_backend.DymoHIDScale":
    """One scale reader per Streamlit server."""
    return scale_backend.DymoHIDScale()

@st.cache_data(ttl=2.0)
def get_sources() -> List[str]:
    return sorted(logger_core.get_sources_dict().keys())

@st.cache_data(ttl=2.0)
def get_types() -> List[str]:
    # logger_core provides dict name->id; DB supplies sort_order but not exposed here.
    types = list(logger_core.get_types_dict().keys())
    return types

@st.cache_data(ttl=2.0)
def get_daily_totals_line() -> str:
    """
    Return single-line totals like:
      Bread: 4.0 lb | Dairy: 2.2 lb | Produce: 9.5 lb
    """
    totals = db_backend.get_daily_totals()  # should return dict {type: weight}
    if not totals:
        return "Today's totals: (none yet)"
    parts = [f"{k}: {v:.2f} lb" for k, v in totals.items()]
    return "Today's totals: " + " | ".join(parts)

def load_logo(path: Path, height_px: int = 140) -> Optional[Image.Image]:
    if not path.exists():
        return None
    img = Image.open(path).convert("RGBA")
    w, h = img.size
    scale = height_px / float(h)
    new_w = int(w * scale)
    return img.resize((new_w, height_px), Image.LANCZOS)

def chunk_types(types: List[str]) -> List[List[str]]:
    """1 row if <=6, else 2 rows split roughly in half."""
    if len(types) <= 6:
        return [types]
    mid = (len(types) + 1) // 2
    return [types[:mid], types[mid:]]

def safe_rerun():
    """Compatibility across Streamlit versions."""
    if hasattr(st, "rerun"):
        st.rerun()
    # else: no-op on very old versions

# ---------------- sidebar ----------------

with st.sidebar:
    st.header("Source & Reports")

    sources = get_sources()
    if "source" not in st.session_state:
        st.session_state.source = sources[0] if sources else "Unknown"

    st.session_state.source = st.selectbox(
        "Select source",
        sources,
        index=sources.index(st.session_state.source) if st.session_state.source in sources else 0,
    )

    st.divider()

    st.subheader("Generate report CSV")
    today_str = datetime.utcnow().date().isoformat()
    start_date = st.date_input("Start date", value=date.fromisoformat(today_str))
    end_date = st.date_input("End date", value=date.fromisoformat(today_str))

    if st.button("Generate CSV", width="stretch"):
        csv_bytes = report_utils.generate_report_csv(
            start_date.isoformat(),
            end_date.isoformat()
        )
        st.download_button(
            "Download report.csv",
            data=csv_bytes,
            file_name="report.csv",
            mime="text/csv",
            width="stretch",
        )

    st.divider()
    st.caption("Sidebar can be collapsed when logging.")

# ---------------- session state ----------------
if "status_msg" not in st.session_state:
    st.session_state.status_msg = ""
if "last_logged" not in st.session_state:
    st.session_state.last_logged = None
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = True
if "last_refresh_t" not in st.session_state:
    st.session_state.last_refresh_t = 0.0

# ---------------- build UI ----------------

scale = get_scale()
reading = scale.get_latest()
weight_lb = 0.0
if reading and reading.unit == "lb":
    weight_lb = reading.value

# ---- top row: logos + huge weight ----
colL, colC, colR = st.columns([1.2, 5.0, 1.2], gap="small")

with colL:
    logo = load_logo(PANTRY_LOGO, height_px=140)
    if logo is not None:
        st.image(logo)
    else:
        st.write("Pantry")

with colC:
    st.markdown(
        f"<div class='weight-box'>{weight_lb:0.2f} lb</div>",
        unsafe_allow_html=True,
    )

with colR:
    logo = load_logo(SCALE_LOGO, height_px=140)
    if logo is not None:
        st.image(logo)
    else:
        st.write("Scale")

st.markdown("<hr style='margin:6px 0px 6px 0px;'>", unsafe_allow_html=True)

# ---- type buttons (compact; 1 or 2 rows) ----
types = get_types()

rows = chunk_types(types)

def on_log(type_name: str):
    # read stable-ish weight quickly, but no UI stable check
    r = scale.read_stable_weight(timeout_s=0.5)
    if r is None:
        st.session_state.status_msg = "No scale reading."
        return
    w = r.value if r.unit == "lb" else None
    if w is None:
        st.session_state.status_msg = f"Scale unit {r.unit} not supported."
        return

    src = st.session_state.source
    logger_core.log_entry(w, src, type_name)

    st.session_state.last_logged = (src, type_name, w)
    st.session_state.status_msg = f"Logged {w:.2f} lb to {src} / {type_name}"

for row_types in rows:
    # Add small left/right spacers so row doesn't stretch edge-to-edge
    cols = st.columns([0.4] + [1.0]*len(row_types) + [0.4], gap="small")
    for i, tname in enumerate(row_types, start=1):
        with cols[i]:
            st.button(
                tname,
                width="stretch",
                on_click=on_log,
                args=(tname,),
                key=f"log_{tname}",
            )
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

# ---- bottom area: totals line + status line ----
totals_line = get_daily_totals_line()
st.markdown(f"<div class='totals-line'>{totals_line}</div>", unsafe_allow_html=True)

if st.session_state.status_msg:
    st.markdown(
        f"<div class='status-area'>{st.session_state.status_msg}</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown("<div class='status-area'>&nbsp;</div>", unsafe_allow_html=True)

# ---------------- auto-refresh loop ----------------
# We want the weight display to update even without clicks.
# This makes the script re-run itself ~5 Hz.
now = time.time()
if st.session_state.auto_refresh and (now - st.session_state.last_refresh_t) > 0.2:
    st.session_state.last_refresh_t = now
    time.sleep(0.2)
    safe_rerun()
