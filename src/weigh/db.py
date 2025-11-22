# db.py — Streamlit-safe SQLite access layer

import sqlite3
import os
from threading import Lock

# -------------------------------------------------------------------
# Global configuration (overridden by tests and Streamlit at startup)
# -------------------------------------------------------------------

DB_PATH = None
SCHEMA_PATH = None

# IMPORTANT:
# We no longer keep a long-lived connection in memory.
# Each call to get_conn() returns a NEW connection.
# This avoids Streamlit's "SQLite objects created in a thread…"
# errors entirely.
#
# However, schema initialization must be thread-safe:
_init_lock = Lock()
_schema_initialized = False


# -------------------------------------------------------------------
# Utility
# -------------------------------------------------------------------

def set_defaults_if_needed():
    """Assign default paths unless tests or app override them."""
    global DB_PATH, SCHEMA_PATH

    if DB_PATH is None:
        DB_PATH = os.path.expanduser("~/weighit/weigh.db")

    if SCHEMA_PATH is None:
        here = os.path.dirname(__file__)
        SCHEMA_PATH = os.path.join(here, "schema.sql")


# -------------------------------------------------------------------
# Schema initialization
# -------------------------------------------------------------------

def initialize_schema_if_needed():
    """
    Ensure tables exist. Thread-safe. Called inside get_conn().
    Only runs once per process.
    """
    global _schema_initialized
    if _schema_initialized:
        return

    with _init_lock:
        if _schema_initialized:
            return

        set_defaults_if_needed()
        
        conn = sqlite3.connect(DB_PATH)
        try:
            # Check if a key table (e.g., 'logs') already exists.
            # If it does, assume the DB is initialized and DO NOT run schema.sql.
            cur = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='logs'"
            )
            if cur.fetchone() is None:
                # Table missing? Run the schema to create everything.
                if os.path.exists(SCHEMA_PATH):
                    with open(SCHEMA_PATH, "r") as f:
                        conn.executescript(f.read())
                    conn.commit()
        finally:
            conn.close()

        _schema_initialized = True


def init_db():
    """Force regenerate schema (only used manually or by tests)."""
    set_defaults_if_needed()
    conn = sqlite3.connect(DB_PATH)
    try:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())
        conn.commit()
    finally:
        conn.close()


def init_for_test(db_path, schema_path):
    """
    Test harness uses this to override the DB file.
    Always forces schema rebuild.
    """
    global DB_PATH, SCHEMA_PATH, _schema_initialized
    DB_PATH = db_path
    SCHEMA_PATH = schema_path
    
    # Reset flag so next connection knows to respect new paths
    _schema_initialized = False
    
    # Force creation immediately
    init_db()


# -------------------------------------------------------------------
# Connection Management (STREAMLIT SAFE)
# -------------------------------------------------------------------

def get_conn():
    """
    Return a fresh SQLite connection every time.
    Streamlit runs code in multiple threads, so keeping a global
    connection is unsafe. Each call gets a new connection with:

        conn.row_factory = sqlite3.Row

    Caller is responsible for closing the connection OR relying on
    context managers.
    """
    initialize_schema_if_needed()
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# -------------------------------------------------------------------
# Query helpers
# -------------------------------------------------------------------

def fetch_sources():
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT id, name FROM sources ORDER BY id"
        ).fetchall()
    finally:
        conn.close()


def fetch_types():
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT id, name, sort_order, requires_temp FROM types ORDER BY sort_order"
        ).fetchall()
    finally:
        conn.close()
