from api._http import APIHandler
from api._db import connect, init_db, serialize_task, log_activity

class handler(APIHandler):
    def do_POST(self):
        try:
            with connect() as conn:
                init_db(conn)
                row = conn.execute("SELECT * FROM tasks ORDER BY priority, task_order LIMIT 1 FOR UPDATE").fetchone()
                if not row:
                    return self.send_json(200,{"ok":True,"task":None,"message":"Queue is empty"})
                task = serialize_task(row)
                conn.execute("DELETE FROM tasks WHERE id=%s",(row["id"],))
                log_activity(conn,"dequeue",task)
                conn.commit()
            self.send_json(200,{"ok":True,"task":task})
        except Exception as e: self.send_json(500,{"error":str(e)})
