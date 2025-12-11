# src/weigh/logger_core.py
from datetime import datetime, UTC
from typing import Optional
from weigh.db import get_conn, fetch_sources, fetch_types

def get_logs_between(start_date: str, end_date: str):
    conn = get_conn()
    try:
        rows = conn.execute("""
            SELECT l.id, l.timestamp, l.weight_lb, l.source_id, l.type_id,
                   s.name AS source, t.name AS type,
                   l.temp_pickup_f, l.temp_dropoff_f
            FROM logs l
            JOIN sources s ON l.source_id = s.id
            JOIN types t   ON l.type_id = t.id
            WHERE DATE(l.timestamp) BETWEEN ? AND ?
              AND l.deleted = 0
            ORDER BY l.timestamp ASC;
        """, (start_date, end_date)).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def get_recent_entries(limit: int = 5, source: Optional[str] = None, date: Optional[str] = None):
    conn = get_conn()
    try:
        if date is None:
            date = datetime.now(UTC).date().isoformat()
        target_date = date

        if source:
            # Filter by source AND target date
            rows = conn.execute("""
                SELECT l.timestamp, l.weight_lb, s.name as source, t.name as type,
                       l.temp_pickup_f, l.temp_dropoff_f
                FROM logs l
                JOIN sources s ON l.source_id = s.id
                JOIN types t   ON l.type_id = t.id
                WHERE l.deleted = 0
                  AND s.name = ?
                  AND DATE(l.timestamp) = ?
                ORDER BY l.id DESC
                LIMIT ?
            """, (source, target_date, limit)).fetchall()
        else:
            # Show all sources for target date
            rows = conn.execute("""
                SELECT l.timestamp, l.weight_lb, s.name as source, t.name as type,
                       l.temp_pickup_f, l.temp_dropoff_f
                FROM logs l
                JOIN sources s ON l.source_id = s.id
                JOIN types t   ON l.type_id = t.id
                WHERE l.deleted = 0
                  AND DATE(l.timestamp) = ?
                ORDER BY l.id DESC
                LIMIT ?
            """, (target_date, limit)).fetchall()

        return [dict(r) for r in rows]
    finally:
        conn.close()

def totals_today_weight_per_type(source: Optional[str] = None, date: Optional[str] = None):
    conn = get_conn()
    try:
        if date is None:
            date = datetime.now(UTC).date().isoformat()
        target_date = date

        if source:
            # Filter by source
            rows = conn.execute("""
                SELECT t.name, SUM(l.weight_lb) as total
                FROM logs l
                JOIN types t ON l.type_id = t.id
                JOIN sources s ON l.source_id = s.id
                WHERE DATE(l.timestamp) = ?
                  AND l.deleted = 0
                  AND s.name = ?
                GROUP BY t.name
                ORDER BY t.sort_order;
            """, (target_date, source)).fetchall()
        else:
            # Show all sources
            rows = conn.execute("""
                SELECT t.name, SUM(l.weight_lb) as total
                FROM logs l
                JOIN types t ON l.type_id = t.id
                WHERE DATE(l.timestamp) = ?
                  AND l.deleted = 0
                GROUP BY t.name
                ORDER BY t.sort_order;
            """, (target_date,)).fetchall()

        return {row["name"]: row["total"] if row["total"] else 0.0 for row in rows}
    finally:
        conn.close()

def get_sources_dict():
    return {row["name"]: row["id"] for row in fetch_sources()}

def get_types_dict():
    """Returns dict with type info including requires_temp flag"""
    types = fetch_types()
    result = {}
    for row in types:
        result[row["name"]] = {
            "id": row["id"],
            "sort_order": row["sort_order"],
            "requires_temp": bool(row["requires_temp"]) if row["requires_temp"] is not None else False
        }
    return result

def type_requires_temp(type_name: str) -> bool:
    """Check if a given type requires temperature logging"""
    types = get_types_dict()
    return types.get(type_name, {}).get("requires_temp", False)

def log_entry(
    weight_lb: float,
    source: str,
    type_: str,
    temp_pickup_f: Optional[float] = None,
    temp_dropoff_f: Optional[float] = None
):
    """
    Log a weight entry with optional temperature data.

    Args:
        weight_lb: Weight in pounds
        source: Source name (e.g., "Trader Joe's")
        type_: Type name (e.g., "Meat", "Produce")
        temp_pickup_f: Temperature at pickup in Fahrenheit (optional)
        temp_dropoff_f: Temperature at dropoff in Fahrenheit (optional)
    """
    conn = get_conn()
    try:
        sources = get_sources_dict()
        types = get_types_dict()
        ts = datetime.now(UTC).isoformat()

        conn.execute("""
            INSERT INTO logs (timestamp, weight_lb, source_id, type_id, deleted,
                             temp_pickup_f, temp_dropoff_f)
            VALUES (?, ?, ?, ?, 0, ?, ?)
        """, (ts, weight_lb, sources[source], types[type_]["id"],
              temp_pickup_f, temp_dropoff_f))
        conn.commit()
    finally:
        conn.close()

def undo_last_entry():
    conn = get_conn()
    try:
        # Find most recent ACTIVE entry
        row = conn.execute(
            "SELECT id FROM logs WHERE deleted=0 ORDER BY id DESC LIMIT 1"
        ).fetchone()

        if not row:
            return None

        conn.execute("UPDATE logs SET deleted=1 WHERE id=?", (row["id"],))
        conn.commit()
        return row["id"]
    finally:
        conn.close()

def redo_last_entry():
    conn = get_conn()
    try:
        # Find most recent DELETED entry (acting as a redo stack)
        row = conn.execute(
            "SELECT id FROM logs WHERE deleted=1 ORDER BY id DESC LIMIT 1"
        ).fetchone()

        if not row:
            return None

        conn.execute("UPDATE logs SET deleted=0 WHERE id=?", (row["id"],))
        conn.commit()
        return row["id"]
    finally:
        conn.close()

def get_last_logs(n=10):
    conn = get_conn()
    try:
        return conn.execute(
            "SELECT * FROM logs ORDER BY id DESC LIMIT ?", (n,)
        ).fetchall()
    finally:
        conn.close()

def totals_today_weight():
    conn = get_conn()
    try:
        today = datetime.now(UTC).date().isoformat()
        row = conn.execute("""
            SELECT SUM(weight_lb)
            FROM logs
            WHERE deleted=0 AND date(timestamp)=?
        """, (today,)).fetchone()
        return row[0] or 0.0
    finally:
        conn.close()
