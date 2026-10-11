from api._http import APIHandler
from api._db import connect, init_db, serialize_task, priority_name
from datetime import timezone

class handler(APIHandler):
    def do_GET(self):
        try:
            with connect() as conn:
                init_db(conn)
                rows = conn.execute("SELECT * FROM tasks ORDER BY priority, task_order").fetchall()
                counts = {}
                for r in rows: counts[int(r["priority"])] = counts.get(int(r["priority"]), 0) + 1
                processed = conn.execute("SELECT COUNT(*) AS n FROM activity WHERE action='dequeue'").fetchone()["n"]
                history_rows = conn.execute("SELECT * FROM activity ORDER BY id DESC LIMIT 30").fetchall()
                history = [{"action":r["action"],"task":{"name":r["task_name"],"assigned_to":r["assigned_to"],"priority":int(r["priority"]),"priority_name":priority_name(r["priority"]),"description":r["description"]},"timestamp":r["created_at"].astimezone(timezone.utc).strftime("%H:%M:%S")} for r in history_rows]
                tasks = [serialize_task(r) for r in rows]
                self.send_json(200, {"tasks_priority_order":tasks,"tasks_heap_order":tasks,"history":history,"stats":{"total_waiting":len(tasks),"high_priority":counts.get(1,0),"normal_priority":counts.get(2,0),"low_priority":counts.get(3,0),"processed_count":processed,"next_task":tasks[0] if tasks else None}})
        except Exception as e: self.send_json(500, {"error":str(e)})
