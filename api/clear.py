from api._http import APIHandler
from api._db import connect, init_db
class handler(APIHandler):
    def do_POST(self):
        try:
            with connect() as conn:
                init_db(conn)
                conn.execute("DELETE FROM tasks")
                conn.commit()
            self.send_json(200,{"ok":True,"message":"Queue cleared"})
        except Exception as e: self.send_json(500,{"error":str(e)})
