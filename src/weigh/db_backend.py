# db_backend.py
# Thin wrapper around logger_core + db for Streamlit UI

from weigh import logger_core
from weigh import db

# ---------------------
# SOURCE / TYPE LISTING
# ---------------------

def list_sources():
    """Return list of source names."""
    rows = logger_core.get_sources_dict()
    return list(rows.keys())


def list_types():
    """Return list of type names sorted by sort_order."""
    rows = logger_core.get_types_dict()
    return list(rows.keys())


# ---------------------
# DAILY TOTALS
# ---------------------

def get_daily_totals():
    """
    Returns dict: {type_name: total_weight_lbs}
    """
    return logger_core.totals_today_weight_per_type()
