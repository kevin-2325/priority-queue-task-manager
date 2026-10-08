import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- Simple Priority Queue State ---
tasks, order = [], 0
PRIO = {1: "High", 2: "Normal", 3: "Low"}

def enqueue(name, assigned_to, priority=2, desc=""):
    global order; order += 1
    tasks.append({"name": name, "assigned_to": assigned_to, "priority": int(priority), "description": desc, "order": order})

def dequeue():
    if not tasks: return None
    t = min(tasks, key=lambda x: (x["priority"], x["order"]))
    tasks.remove(t); return t

def reset():
    global order; tasks.clear(); order = 0
    enqueue("Complete Project", "Kevin", 1, "DSA project implementation.")
    enqueue("Prepare Notes", "Tony", 2, "Database notes.")
    enqueue("Check Email", "Arun", 3, "Client emails.")
    enqueue("Submit Assignment", "Rahul", 1, "Assignment deadline.")

reset()

# --- Localhost Web Server Handler ---
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        next_task = min(tasks, key=lambda x: (x["priority"], x["order"])) if tasks else None
        peek_txt = f"<b>{next_task['name']}</b> (Assigned: {next_task['assigned_to']} | Priority: {PRIO.get(next_task['priority'])})" if next_task else "Queue is Empty"
        rows = "".join(f"<tr><td>{t['name']}</td><td>{t['assigned_to']}</td><td>{PRIO.get(t['priority'])} ({t['priority']})</td><td>{t['description']}</td></tr>" for t in sorted(tasks, key=lambda x: (x["priority"], x["order"])))
        html = f"""<!DOCTYPE html><html><head><title>Priority Queue Task Manager</title>
        <style>body{{font-family:sans-serif;margin:30px;background:#f4f6f9;color:#333;}} .card{{background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1);margin-bottom:20px;}} table{{width:100%;border-collapse:collapse;}} th,td{{padding:10px;border-bottom:1px solid #ddd;text-align:left;}} th{{background:#0284c7;color:#fff;}} input,select{{padding:8px;margin:5px 0;width:95%;}} button{{padding:10px 16px;background:#0284c7;color:#fff;border:none;border-radius:4px;cursor:pointer;margin-right:10px;}} .danger{{background:#ef4444;}} .success{{background:#10b981;}}</style></head><body>
        <div class="card"><h2>Priority Queue Task Manager (Localhost)</h2><p><b>Next Task to Process (PEEK):</b> {peek_txt}</p>
        <form action="/dequeue" method="POST" style="display:inline;"><button type="submit" class="success">Process Next Task (Dequeue)</button></form>
        <form action="/reset" method="POST" style="display:inline;"><button type="submit" class="danger">Reset Defaults</button></form></div>
        <div class="card"><h3>Enqueue New Task</h3>
        <form action="/enqueue" method="POST">
        <input type="text" name="name" placeholder="Task Name" required><br>
        <input type="text" name="assigned_to" placeholder="Assigned To" required><br>
        <select name="priority"><option value="1">High Priority (1)</option><option value="2" selected>Normal Priority (2)</option><option value="3">Low Priority (3)</option></select><br>
        <input type="text" name="description" placeholder="Description"><br><br>
        <button type="submit">Add Task (Enqueue)</button></form></div>
        <div class="card"><h3>Waiting Tasks ({len(tasks)})</h3>
        <table><tr><th>Task Name</th><th>Assigned To</th><th>Priority</th><th>Description</th></tr>{rows or '<tr><td colspan="4">No waiting tasks</td></tr>'}</table></div>
        </body></html>"""
        self.wfile.write(html.encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = urllib.parse.parse_qs(self.rfile.read(length).decode("utf-8"))
        if self.path == "/enqueue":
            name = body.get("name", [""])[0].strip()
            assigned = body.get("assigned_to", [""])[0].strip()
            priority = body.get("priority", ["2"])[0]
            desc = body.get("description", [""])[0].strip()
            if name and assigned: enqueue(name, assigned, priority, desc)
        elif self.path == "/dequeue": dequeue()
        elif self.path == "/reset": reset()
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, fmt, *args): pass

if __name__ == "__main__":
    print("=" * 60 + "\nPriority Queue Task Manager running at http://localhost:5000\n" + "=" * 60)
    try: HTTPServer(("", 5000), Handler).serve_forever()
    except KeyboardInterrupt: pass
