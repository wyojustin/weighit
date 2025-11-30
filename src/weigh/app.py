# src/weigh/app.py
from __future__ import annotations

import os
import signal
import time
import textwrap
from datetime import datetime, date, timezone
from pathlib import Path
from typing import List, Optional

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

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
def get_types() -> List[dict]:
    """Returns list of type info dicts with name and requires_temp flag"""
    types_dict = logger_core.get_types_dict()
    types_list = []
    for name, info in types_dict.items():
        types_list.append({
            "name": name,
            "sort_order": info["sort_order"],
            "requires_temp": info["requires_temp"]
        })
    return sorted(types_list, key=lambda x: x["sort_order"])

def get_daily_totals_line() -> str:
    current_source = st.session_state.get("source", None)
    totals = db_backend.get_daily_totals(source=current_source)
    
    # Get all types to show them all (even if 0.0)
    all_types = get_types()
    
    # Build parts list with all types in order
    parts = []
    for type_info in all_types:
        type_name = type_info["name"]
        weight = totals.get(type_name, 0.0)
        parts.append(f"{type_name}: {weight:.1f}")
    
    return " | ".join(parts)

def get_history_html() -> str:
    """Generates a fixed-height table with exactly 15 rows filtered by current source."""
    limit = 15
    current_source = st.session_state.get("source", None)
    entries = logger_core.get_recent_entries(limit, source=current_source)
    
    rows_html = ""
    
    # 1. Render actual data rows
    for row in entries:
        try:
            dt = datetime.fromisoformat(row["timestamp"]).astimezone()
            ts_str = dt.strftime("%H:%M")
        except Exception:
            ts_str = row["timestamp"]

        # Add temperature info if present
        temp_info = ""
        if row.get("temp_pickup_f") is not None or row.get("temp_dropoff_f") is not None:
            temps = []
            if row.get("temp_pickup_f") is not None:
                temps.append(f"Pick:{row['temp_pickup_f']:.1f}°F")
            if row.get("temp_dropoff_f") is not None:
                temps.append(f"Drop:{row['temp_dropoff_f']:.1f}°F")
            temp_info = f" ({', '.join(temps)})"

        rows_html += (
            f"<tr>"
            f"<td>{ts_str}</td>"
            f"<td>{row['source']}</td>"
            f"<td>{row['type']}{temp_info}</td>"
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

def chunk_types(types: List[dict]) -> List[List[dict]]:
    if len(types) == 0: return []
    if len(types) <= 8: return [types]
    mid = (len(types) + 1) // 2
    return [types[:mid], types[mid:]]

@st.fragment(run_every="1s")
def display_weight():
    """Auto-updating weight display that refreshes every second independently"""
    try:
        scale = get_scale()
        reading = scale.get_latest()

        # Retry a few times if no reading yet
        if reading is None:
            for _ in range(3):
                time.sleep(0.1)
                reading = scale.get_latest()
                if reading:
                    break

        weight_str = f"{reading.value:.1f} lbs" if reading and reading.unit == "lb" else "—"
    except Exception as e:
        weight_str = "Err"
        logging.error(f"Scale error in fragment: {type(e).__name__}: {e}")

    # This markdown will update every second without redrawing the whole app
    st.markdown(f'<div class="weight-box">{weight_str}</div>', unsafe_allow_html=True)

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()

@st.dialog("Volunteer Cheat Sheet", width="large")
def cheatsheet_dialog():
    """Modal dialog for displaying the volunteer cheat sheet"""
    cheatsheet_path = Path(__file__).parent.parent.parent / "docs" / "volunteer_cheatsheet.md"
    
    if cheatsheet_path.exists():
        with open(cheatsheet_path, "r") as f:
            markdown_content = f.read()
            
            # Split content into sections by major headers (##)
            sections = markdown_content.split('\n## ')
            
            # First section includes the title
            left_sections = [sections[0]]
            right_sections = []
            
            # Distribute remaining sections into two columns
            # Put first half in left, second half in right
            remaining = ['## ' + s for s in sections[1:]]
            mid_point = len(remaining) // 2
            
            left_sections.extend(remaining[:mid_point])
            right_sections.extend(remaining[mid_point:])
            
            # Display in two columns
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('\n'.join(left_sections))
            
            with col2:
                st.markdown('\n'.join(right_sections))
    else:
        st.error("Cheat sheet not found!")
    
    # Scroll to top of dialog
    components.html("""
    <script>
    const doc = window.parent.document;
    // Find the dialog and scroll to top
    function scrollToTop() {
        const dialogs = doc.querySelectorAll('[role="dialog"]');
        if (dialogs.length > 0) {
            const dialog = dialogs[dialogs.length - 1];
            dialog.scrollTop = 0;
            
            // Also scroll any scrollable children
            const scrollableContent = dialog.querySelector('[data-testid="stVerticalBlock"]');
            if (scrollableContent) {
                scrollableContent.scrollTop = 0;
            }
            
            // Scroll the dialog's first child (the content container)
            if (dialog.firstElementChild) {
                dialog.firstElementChild.scrollTop = 0;
            }
        }
    }
    
    // Try multiple times to ensure it works
    setTimeout(scrollToTop, 50);
    setTimeout(scrollToTop, 200);
    setTimeout(scrollToTop, 500);
    </script>
    """, height=0, width=0)
    
    if st.button("Close", type="primary", use_container_width=True):
        st.rerun()


@st.dialog("Temperature Recording")
def temperature_dialog():
    """Modal dialog for recording temperatures"""
    entry = st.session_state.pending_entry
    if not entry or st.session_state.get("dialog_processed", False):
        st.session_state.show_temp_dialog = False
        st.session_state.dialog_processed = False
        st.rerun()
        return
    
    type_name = entry["type"]
    weight = entry["weight"]
    source = entry["source"]
    
    st.write(f"Recording temperatures for **{type_name}**")
    st.write(f"Weight: **{weight:.2f} lb** from **{source}**")
    
    st.divider()
    
    # Temperature inputs with number_input for better mobile experience
    temp_pickup = st.number_input(
        "Pickup Temperature (°F)",
        min_value=-40.0,
        max_value=200.0,
        value=40.0,
        step=1.0,
        format="%.1f",
        help="Temperature at pickup location",
        key="temp_pickup_input"
    )
    
    temp_dropoff = st.number_input(
        "Dropoff Temperature (°F)",
        min_value=-40.0,
        max_value=200.0,
        value=38.0,
        step=1.0,
        format="%.1f",
        help="Temperature at dropoff/storage location",
        key="temp_dropoff_input"
    )
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Cancel", use_container_width=True, key="cancel_temp"):
            st.session_state.show_temp_dialog = False
            st.session_state.pending_entry = None
            st.session_state.dialog_processed = True
            st.rerun()
    
    with col2:
        if st.button("Save Entry", type="primary", use_container_width=True, key="save_temp"):
            # Log the entry with temperatures
            logger_core.log_entry(
                weight, 
                source, 
                type_name,
                temp_pickup_f=temp_pickup,
                temp_dropoff_f=temp_dropoff
            )
            
            # Mark as processed and clear
            st.session_state.dialog_processed = True
            st.session_state.show_temp_dialog = False
            st.session_state.pending_entry = None
            
            # Force dialog to close
            st.rerun()

    # Inject JS for input behavior (Select All on Focus + Input Validation)
    # We use a MutationObserver to attach listeners to the number inputs in the dialog
    components.html("""
    <script>
    const doc = window.parent.document;
    
    function attachListeners() {
        // Target the specific number inputs by their aria-labels or just all number inputs in the dialog
        // Streamlit number inputs are usually <input type="number"> or <input type="text" inputmode="decimal">
        const inputs = Array.from(doc.querySelectorAll('input[type="number"], input[inputmode="decimal"]'));
        
        inputs.forEach(input => {
            if (input.dataset.listenersAttached) return;
            
            // Helper to select text
            const selectText = () => {
                input.select();
            };
            
            // 1. Select All on Focus
            input.addEventListener('focus', function(e) {
                // Small timeout to ensure browser default behavior doesn't override us
                setTimeout(selectText, 50);
            });
            
            // Handle click/touch specifically (fixes selection clearing on mobile)
            input.addEventListener('mouseup', function(e) {
                // Prevent default to stop browser from clearing selection
                e.preventDefault();
                setTimeout(selectText, 50);
            });
            
            // 2. Strict Input Validation (Digits, one dot, one minus at start)
            input.addEventListener('input', function(e) {
                let val = this.value;
                
                // Allow: digits, dot, minus
                const clean = val.replace(/[^0-9.-]/g, '');
                
                // Handle multiple dots: keep only the first
                const parts = clean.split('.');
                let final = parts[0];
                if (parts.length > 1) {
                    final += '.' + parts.slice(1).join('');
                }
                
                // Handle minus: only allowed at start
                if (final.indexOf('-') > 0) {
                    final = final.replace(/-/g, '');
                }
                
                if (val !== final) {
                    this.value = final;
                }
            });
            
            input.dataset.listenersAttached = 'true';
        });
    }

    // Observe changes to detect when dialog opens
    const observer = new MutationObserver(() => {
        attachListeners();
    });
    
    observer.observe(doc.body, { childList: true, subtree: true });
    
    // Initial run
    setTimeout(attachListeners, 500);
    </script>
    """, height=0, width=0)

# ---------------- INIT ----------------
load_css(STYLE_CSS)

# Inject Keyboard Listener (Ctrl-Z / Ctrl-Y / Alt-F4)
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
    // F4 = Close Application
    if (e.altKey && e.key === 'F4') {
        e.preventDefault();  // Prevent default browser behavior
        const buttons = Array.from(doc.querySelectorAll('button'));
        const closeBtn = buttons.find(el => el.innerText.includes("Close Application"));
        if (closeBtn) {
            closeBtn.click();
        }
    }
});
</script>
""", height=0, width=0)


# Sidebar
with st.sidebar:
    st.header("Admin")
    sources = get_sources()
    
    # Initialize source if not set (will be displayed on main screen)
    if "source" not in st.session_state:
        st.session_state.source = sources[0] if sources else "Unknown"
    
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
    
    # --- VOLUNTEER CHEAT SHEET ---
    if st.button("📋 View Volunteer Cheat Sheet", use_container_width=True):
        st.session_state.show_cheatsheet = True
        st.rerun()
    
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

    st.divider()

    # --- CLOSE APPLICATION ---
    if st.button("Close Application", type="secondary", use_container_width=True):
        st.warning("Shutting down...")
        # Kill all browsers and streamlit
        os.system("pkill -f chromium")
        os.system("pkill -f firefox")
        os.system("pkill -f epiphany")
        os.kill(os.getpid(), signal.SIGTERM)

# Session State Defaults
if "last_refresh_t" not in st.session_state:
    st.session_state.last_refresh_t = 0.0
if "show_temp_dialog" not in st.session_state:
    st.session_state.show_temp_dialog = False
if "pending_entry" not in st.session_state:
    st.session_state.pending_entry = None
if "dialog_processed" not in st.session_state:
    st.session_state.dialog_processed = False
if "show_cheatsheet" not in st.session_state:
    st.session_state.show_cheatsheet = False

# ---------------- MAIN UI ----------------

# 1. Get Weight
try:
    scale = get_scale()
    # Retry a few times if we just started up and haven't got a reading yet
    reading = scale.get_latest()
    if reading is None:
        for _ in range(10):
            time.sleep(0.1)
            reading = scale.get_latest()
            if reading:
                break
                
    weight_str = f"{reading.value:.1f} lbs" if reading and reading.unit == "lb" else "—"
except Exception as e:
    scale = None
    weight_str = "Err"
    # Log the error for debugging
    logging.error(f"Scale error: {type(e).__name__}: {e}")
    # Show error in sidebar for debugging
    with st.sidebar:
        st.error(f"Scale Error: {type(e).__name__}: {str(e)}")

# 2. Top Row: Logo | Weight | Logo
c1, c2, c3 = st.columns([1, 5, 1], gap="small", vertical_alignment="center")

with c1:
    img = load_logo(PANTRY_LOGO, height_px=138)
    if img: st.image(img)

with c2:
    # Compact donor dropdown above weight
    sources = get_sources()
    current_idx = 0
    if st.session_state.source in sources:
        current_idx = sources.index(st.session_state.source)
    
    st.session_state.source = st.selectbox(
        "Current Donor",
        sources,
        index=current_idx,
        key="donor_select_main",
        label_visibility="collapsed"
    )
    
    #weight_ph = st.empty()
    
    #weight_ph.markdown(f'<div class="weight-box">{weight_str}</div>', unsafe_allow_html=True)
    display_weight()

with c3:
    img = load_logo(SCALE_LOGO, height_px=138)
    if img:
        # Hidden button for refresh
        if st.button("refresh_hidden", key="refresh_scale", help="Click scale to refresh"):
            safe_rerun()
        # Show image with click handler
        st.image(img, use_container_width=False)

# Inject JavaScript to make scale image clickable
components.html("""
<script>
const doc = window.parent.document;

// Find the scale refresh button and the scale image
function makeScaleClickable() {
    const buttons = Array.from(doc.querySelectorAll('button'));
    const refreshBtn = buttons.find(el => el.innerText.includes("refresh_hidden"));
    
    if (refreshBtn) {
        // Hide the button
        refreshBtn.style.display = 'none';
        
        // Find scale image (it's in the last column)
        const images = Array.from(doc.querySelectorAll('img'));
        const scaleImg = images[images.length - 1]; // Last image should be scale
        
        if (scaleImg) {
            scaleImg.style.cursor = 'pointer';
            scaleImg.onclick = function() {
                refreshBtn.click();
            };
        }
    }
}

// Run after page loads
setTimeout(makeScaleClickable, 100);
</script>
""", height=0, width=0)

# 3. Buttons
types = get_types()
rows = chunk_types(types)

def on_log(type_info):
    """Handle button click - check if temperature is required"""
    scale = get_scale()
    r = scale.read_stable_weight(timeout_s=0.5) if scale else None
    if r and r.unit == "lb":
        if r.value > 0.0:
            src = st.session_state.source
            
            # Check if this type requires temperature
            if type_info["requires_temp"]:
                # Store pending entry and show dialog
                st.session_state.pending_entry = {
                    "weight": r.value,
                    "source": src,
                    "type": type_info["name"]
                }
                st.session_state.show_temp_dialog = True
                st.session_state.dialog_processed = False  # Reset the flag
            else:
                # Log directly without temperature
                logger_core.log_entry(r.value, src, type_info["name"])

for i, row in enumerate(rows):
    cols = st.columns(len(row), gap="small")
    for idx, type_info in enumerate(row):
        cols[idx].button(
            type_info["name"], 
            on_click=on_log, 
            args=(type_info,), 
            use_container_width=True, 
            key=f"btn_{i}_{idx}"
        )

# Show temperature dialog if needed
if st.session_state.get("show_temp_dialog", False):
    temperature_dialog()

# Show cheat sheet dialog if requested
if st.session_state.get("show_cheatsheet", False):
    st.session_state.show_cheatsheet = False
    cheatsheet_dialog()

# 4. Daily Totals
totals_ph = st.empty()
totals_ph.markdown(f'<div class="totals-box">{get_daily_totals_line()}</div>', unsafe_allow_html=True)

# 5. History Table
history_ph = st.empty()
history_ph.markdown(get_history_html(), unsafe_allow_html=True)

# 6. Auto-Refresh - DISABLED when dialog exists
# The dialog and auto-refresh conflict, so we disable auto-refresh
# Users can manually click buttons to refresh
# Uncomment below if you want auto-refresh back (but dialog won't work properly)
junk = """
now = time.time()
if (now - st.session_state.last_refresh_t) > 0.5:
    st.session_state.last_refresh_t = now
    time.sleep(0.5)
    safe_rerun()
"""
