import os
import psycopg
from psycopg.rows import dict_row
from datetime import datetime, timezone

def connect():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not configured. Add a Neon PostgreSQL connection string in Vercel Project Settings.")
    return psycopg.connect(url, row_factory=dict_row)

def init_db(conn):
    conn.execute("""
      CREATE TABLE IF NOT EXISTS tasks (
        id BIGSERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        priority INTEGER NOT NULL CHECK (priority BETWEEN 1 AND 3),
        description TEXT NOT NULL DEFAULT '',
        task_order BIGINT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    """)
    conn.execute("""
      CREATE TABLE IF NOT EXISTS activity (
        id BIGSERIAL PRIMARY KEY,
        action TEXT NOT NULL,
        task_name TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        priority INTEGER NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
      )
    """)
    conn.execute("CREATE SEQUENCE IF NOT EXISTS task_order_seq START 1")
    conn.commit()

def priority_name(priority):
    return {1: "High", 2: "Normal", 3: "Low"}.get(int(priority), "Normal")

def serialize_task(row):
    if not row: return None
    created = row.get("created_at")
    return {
      "id": row["id"], "name": row["name"], "assigned_to": row["assigned_to"],
      "priority": int(row["priority"]), "priority_name": priority_name(row["priority"]),
      "description": row.get("description") or "", "order": row.get("task_order", row.get("order", 0)),
      "created_at": created.strftime("%Y-%m-%d %H:%M") if created else ""
    }

def log_activity(conn, action, task):
    conn.execute("INSERT INTO activity(action, task_name, assigned_to, priority, description) VALUES (%s,%s,%s,%s,%s)",
      (action, task["name"], task["assigned_to"], task["priority"], task.get("description","")))

def seed_defaults(conn):
    conn.execute("DELETE FROM tasks")
    conn.execute("DELETE FROM activity")
    samples = [
      ("Complete Project", "Kevin", 1, "DSA project implementation."),
      ("Prepare Notes", "Tony", 2, "Database notes."),
      ("Check Email", "Arun", 3, "Client emails."),
      ("Submit Assignment", "Rahul", 1, "Assignment deadline.")
    ]
    for name, assigned, priority, desc in samples:
      order = conn.execute("SELECT nextval('task_order_seq') AS n").fetchone()["n"]
      conn.execute("INSERT INTO tasks(name,assigned_to,priority,description,task_order) VALUES (%s,%s,%s,%s,%s)",
        (name, assigned, priority, desc, order))
      log_activity(conn, "enqueue", {"name":name,"assigned_to":assigned,"priority":priority,"description":desc})
    conn.commit()
