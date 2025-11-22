# test_db_init.py
import sqlite3
from weigh import db


def test_init_creates_tables(temp_db):
    conn = sqlite3.connect(temp_db["db_path"])

    # list expected tables
    tables = {
        r[0]
        for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }

    assert "sources" in tables
    assert "types" in tables
    assert "logs" in tables
