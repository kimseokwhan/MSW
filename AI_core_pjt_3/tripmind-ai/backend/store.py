import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from backend.config import setting
from backend.schemas.service import PlanInput, PlanPatch


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY, memory_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT REFERENCES sessions(id) ON DELETE SET NULL,
    title TEXT NOT NULL, region TEXT NOT NULL, visit_date TEXT NOT NULL,
    start_time TEXT NOT NULL, end_time TEXT NOT NULL, notes TEXT,
    created_at TEXT NOT NULL, updated_at TEXT NOT NULL, CHECK(start_time < end_time)
);
CREATE INDEX IF NOT EXISTS plan_window ON plans(visit_date, start_time, end_time);
CREATE TABLE IF NOT EXISTS plan_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT, plan_id INTEGER NOT NULL REFERENCES plans(id) ON DELETE CASCADE,
    position INTEGER NOT NULL, content_id TEXT, title TEXT NOT NULL, address TEXT,
    latitude REAL, longitude REAL, start_time TEXT, end_time TEXT,
    evidence_json TEXT NOT NULL, UNIQUE(plan_id, position)
);
CREATE TABLE IF NOT EXISTS execution_logs (
    event_id TEXT PRIMARY KEY, session_id TEXT NOT NULL REFERENCES sessions(id),
    run_id TEXT NOT NULL, seq INTEGER NOT NULL, event_type TEXT NOT NULL,
    node TEXT NOT NULL, occurred_at TEXT NOT NULL, payload_json TEXT NOT NULL,
    UNIQUE(run_id, seq)
);
CREATE INDEX IF NOT EXISTS log_session ON execution_logs(session_id, occurred_at);
"""

SUMMARY = """SELECT p.*, (SELECT COUNT(*) FROM plan_items i WHERE i.plan_id=p.id)
             AS item_count FROM plans p"""


class NotFound(Exception):
    pass


def utc_now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def connection(write=False):
    path = setting("TRIPMIND_DB_PATH") or Path(__file__).resolve().with_name("tripmind.sqlite3")
    db = sqlite3.connect(path, timeout=5)
    db.row_factory = sqlite3.Row
    try:
        db.execute("PRAGMA foreign_keys=ON")
        if write:
            db.execute("BEGIN IMMEDIATE")
        with db:
            yield db
    finally:
        db.close()


def initialize():
    with connection() as db:
        db.executescript(SCHEMA)
        db.execute("PRAGMA journal_mode=WAL")


def insert_session(db, session_id):
    now = utc_now()
    db.execute("INSERT OR IGNORE INTO sessions(id, created_at, updated_at) VALUES (?, ?, ?)",
               (session_id, now, now))


def read_memory(session_id):
    with connection() as db:
        row = db.execute("SELECT memory_json FROM sessions WHERE id=?", (session_id,)).fetchone()
        return json.loads(row["memory_json"]) if row else {}


def write_memory(session_id, memory):
    with connection(write=True) as db:
        insert_session(db, session_id)
        db.execute("UPDATE sessions SET memory_json=?, updated_at=? WHERE id=?",
                   (json.dumps(memory, ensure_ascii=False), utc_now(), session_id))


def detail(db, plan_id):
    row = db.execute("SELECT * FROM plans WHERE id=?", (plan_id,)).fetchone()
    if row is None:
        raise NotFound
    plan = dict(row)
    plan["items"] = []
    for item in db.execute("SELECT * FROM plan_items WHERE plan_id=? ORDER BY position", (plan_id,)):
        values = dict(item)
        values["evidence"] = json.loads(values.pop("evidence_json"))
        plan["items"].append(values)
    return plan


def get_plan(plan_id):
    with connection() as db:
        db.execute("BEGIN")
        return detail(db, plan_id)


def list_plans(visit_date, limit, offset):
    where = " WHERE p.visit_date=?" if visit_date else ""
    params = (visit_date,) if visit_date else ()
    with connection() as db:
        db.execute("BEGIN")
        total = db.execute("SELECT COUNT(*) FROM plans p" + where, params).fetchone()[0]
        rows = db.execute(SUMMARY + where + " ORDER BY visit_date,start_time,id LIMIT ? OFFSET ?",
                          (*params, limit, offset)).fetchall()
    return {"items": [dict(row) for row in rows], "total": total}


def save_plan(changes: PlanInput | PlanPatch, plan_id=None):
    with connection(write=True) as db:
        if plan_id is not None:
            plan = PlanInput.model_validate({**detail(db, plan_id), **changes.model_dump(exclude_unset=True)})
        else:
            plan = changes
        data = plan.model_dump(mode="json")
        now = utc_now()
        if data["session_id"]:
            insert_session(db, data["session_id"])
        if plan_id is None:
            cursor = db.execute("""INSERT INTO plans(session_id,title,region,visit_date,start_time,end_time,
                 notes,created_at,updated_at) VALUES (:session_id,:title,:region,:visit_date,:start_time,
                 :end_time,:notes,:now,:now)""", {**data, "now": now})
            plan_id = cursor.lastrowid
        else:
            db.execute("""UPDATE plans SET title=:title,region=:region,visit_date=:visit_date,
                start_time=:start_time,end_time=:end_time,notes=:notes,updated_at=:now WHERE id=:id""",
                       {**data, "id": plan_id, "now": now})
        if isinstance(changes, PlanInput) or "items" in changes.model_fields_set:
            db.execute("DELETE FROM plan_items WHERE plan_id=?", (plan_id,))
            db.executemany("""INSERT INTO plan_items(plan_id,position,content_id,title,address,
                latitude,longitude,start_time,end_time,evidence_json) VALUES (:plan_id,:position,
                :content_id,:title,:address,:latitude,:longitude,:start_time,:end_time,:evidence_json)""",
                [{**item, "plan_id": plan_id, "position": index,
                  "evidence_json": json.dumps(item["evidence"], ensure_ascii=False)}
                 for index, item in enumerate(data["items"], start=1)])
        conflicts = db.execute(SUMMARY + """ WHERE p.visit_date=? AND p.id<>?
            AND p.start_time<? AND ?<p.end_time ORDER BY p.start_time,p.id""",
            (data["visit_date"], plan_id, data["end_time"], data["start_time"])).fetchall()
        return {"plan": detail(db, plan_id), "conflicts": [dict(row) for row in conflicts]}


def delete_plan(plan_id):
    with connection(write=True) as db:
        if not db.execute("DELETE FROM plans WHERE id=?", (plan_id,)).rowcount:
            raise NotFound


def append_event(event):
    with connection(write=True) as db:
        insert_session(db, event["session_id"])
        db.execute("""INSERT INTO execution_logs(event_id,session_id,run_id,seq,event_type,node,
                   occurred_at,payload_json) VALUES (?,?,?,?,?,?,?,?)""",
                   (event["event_id"], event["session_id"], event["run_id"], event["seq"],
                    event["type"], event["node"], event["occurred_at"],
                    json.dumps(event["payload"], ensure_ascii=False)))


def list_logs(limit, offset):
    with connection() as db:
        db.execute("BEGIN")
        total = db.execute("SELECT COUNT(DISTINCT session_id) FROM execution_logs").fetchone()[0]
        rows = db.execute("""SELECT session_id, COUNT(*) AS event_count,
            COUNT(DISTINCT run_id) AS run_count, MAX(occurred_at) AS last_event_at
            FROM execution_logs GROUP BY session_id ORDER BY last_event_at DESC,session_id
            LIMIT ? OFFSET ?""", (limit, offset)).fetchall()
    return {"items": [dict(row) for row in rows], "total": total}


def get_logs(session_id):
    with connection() as db:
        rows = db.execute("""SELECT e.* FROM execution_logs e
            JOIN (SELECT run_id, MIN(occurred_at) AS started FROM execution_logs
                  WHERE session_id=? GROUP BY run_id) r ON r.run_id=e.run_id
            WHERE e.session_id=? ORDER BY r.started,e.run_id,e.seq""", (session_id, session_id)).fetchall()
    if not rows:
        raise NotFound
    events = []
    for row in rows:
        event = dict(row)
        event["type"] = event.pop("event_type")
        event["payload"] = json.loads(event.pop("payload_json"))
        events.append(event)
    return {"session_id": session_id, "events": events}


def delete_logs(session_id):
    with connection(write=True) as db:
        if not db.execute("DELETE FROM execution_logs WHERE session_id=?", (session_id,)).rowcount:
            raise NotFound
