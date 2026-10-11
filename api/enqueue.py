import json
from api._http import APIHandler
from api._db import connect, init_db, log_activity

class handler(APIHandler):
    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")
            name = str(data.get("name","")).strip()
            assigned = str(data.get("assigned_to","")).strip()
            desc = str(data.get("description","")).strip()
            priority = int(data.get("priority",2))
            if not name or not assigned: return self.send_json(400, {"error":"Task name and assignee are required"})
            if priority not in (1,2,3): return self.send_json(400, {"error":"Priority must be 1, 2, or 3"})
            with connect() as conn:
                init_db(conn)
                order = conn.execute("SELECT nextval('task_order_seq') AS n").fetchone()["n"]
                conn.execute("INSERT INTO tasks(name,assigned_to,priority,description,task_order) VALUES (%s,%s,%s,%s,%s)",(name,assigned,priority,desc,order))
                log_activity(conn,"enqueue",{"name":name,"assigned_to":assigned,"priority":priority,"description":desc})
                conn.commit()
            self.send_json(201,{"ok":True,"message":"Task added"})
        except Exception as e: self.send_json(500,{"error":str(e)})
