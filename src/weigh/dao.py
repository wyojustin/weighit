# dao.py
from weigh.db import get_conn

def add_source(name: str):
    """Add a new source if not already present."""
    conn = get_conn()
    try:
        conn.execute("INSERT OR IGNORE INTO sources (name) VALUES (?)", (name,))
        conn.commit()
    finally:
        conn.close()

def get_sources():
    """Return all sources (id, name)."""
    conn = get_conn()
    try:
        return conn.execute("SELECT id, name FROM sources ORDER BY id").fetchall()
    finally:
        conn.close()
