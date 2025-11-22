# dao.py
from weigh.db import get_conn

def add_source(name: str):
    """Add a new source if not already present."""
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO sources (name) VALUES (?)", (name,))
    conn.commit()

def get_sources():
    """Return all sources (id, name)."""
    conn = get_conn()
    return conn.execute("SELECT id, name FROM sources ORDER BY id").fetchall()
