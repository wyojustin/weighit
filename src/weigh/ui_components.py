# ui_components.py
import streamlit as st

def big_weight_display(value, unit, is_stable):
    color = "green" if is_stable else "orange"
    st.markdown(
        f"""
        <div class="weight-display" style="color:{color}">
            {value:.2f} {unit}
        </div>
        """,
        unsafe_allow_html=True,
    )

def pending_indicator(reading):
    if reading and not reading.is_stable:
        st.markdown(
            "<div class='pending'>Pending stable weight...</div>",
            unsafe_allow_html=True,
        )

def type_buttons_row(types, source, reading):
    cols = st.columns(len(types))

    for col, t in zip(cols, types):
        with col:
            if st.button(t["name"], use_container_width=True):
                if reading and reading.is_stable:
                    st.success(f"Logged {reading.value:.2f} lb as {t['name']} from {source}")
                    import logger_core
                    logger_core.log_entry(reading.value, source, t["name"])
                else:
                    st.warning("Waiting for stable weight… try again.")
