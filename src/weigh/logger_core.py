# logger_core.py
from datetime import datetime
from weigh.db import get_conn, fetch_sources, fetch_types
from datetime import datetime, UTC

def get_logs_between(start_date: str, end_date: str):
    """
    Return all logs between start_date and end_date inclusive.
    Dates should be strings 'YYYY-MM-DD'.
    """
    conn = get_conn()

    rows = conn.execute("""
        SELECT l.id, l.timestamp, l.weight_lb, l.source_id, l.type_id,
               s.name AS source, t.name AS type
        FROM logs l
        JOIN sources s ON l.source_id = s.id
        JOIN types t   ON l.type_id = t.id
        WHERE DATE(l.timestamp) BETWEEN ? AND ?
          AND l.deleted = 0
        ORDER BY l.timestamp ASC;
    """, (start_date, end_date)).fetchall()

    return [dict(row) for row in rows]

def totals_today_weight_per_type():
    """
    Returns dict: {type_name: total_weight_for_today}
    """
    conn = get_conn()

    today = datetime.utcnow().date().isoformat()

    rows = conn.execute("""
        SELECT t.name, SUM(l.weight_lb) as total
        FROM logs l
        JOIN types t ON l.type_id = t.id
        WHERE DATE(l.timestamp) = ?
          AND l.deleted = 0
        GROUP BY t.name
        ORDER BY t.sort_order;
    """, (today,)).fetchall()

    return {row["name"]: row["total"] if row["total"] else 0.0 for row in rows}

def get_sources_dict():
    return {row["name"]: row["id"] for row in fetch_sources()}

def get_types_dict():
    return {row["name"]: row["id"] for row in fetch_types()}

def log_entry(weight_lb: float, source: str, type_: str):
    conn = get_conn()
    sources = get_sources_dict()
    types = get_types_dict()

    ts = datetime.now(UTC).isoformat()

    conn.execute("""
        INSERT INTO logs (timestamp, weight_lb, source_id, type_id, deleted)
        VALUES (?, ?, ?, ?, 0)
    """, (ts, weight_lb, sources[source], types[type_]))
    conn.commit()

def undo_last_entry():
    conn = get_conn()
    row = conn.execute(
        "SELECT id FROM logs WHERE deleted=0 ORDER BY id DESC LIMIT 1"
    ).fetchone()

    if not row:
        return None

    conn.execute("UPDATE logs SET deleted=1 WHERE id=?", (row["id"],))
    conn.commit()
    return row["id"]

def get_last_logs(n=10):
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM logs ORDER BY id DESC LIMIT ?", (n,)
    ).fetchall()

def totals_today_weight():
    conn = get_conn()
    today = datetime.now(UTC).date().isoformat()

    row = conn.execute("""
        SELECT SUM(weight_lb)
        FROM logs
        WHERE deleted=0 AND date(timestamp)=?
    """, (today,)).fetchone()

    return row[0] or 0.0
