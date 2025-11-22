import sqlite3
from weigh.db import init_db

def test_schema_creates_tables(temp_db):
    init_db()
    conn = sqlite3.connect(temp_db["db_path"])
    cur = conn.cursor()

    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    assert "sources" in tables
    assert "types" in tables
    assert "logs" in tables
