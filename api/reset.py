from api._http import APIHandler
from api._db import connect, init_db, seed_defaults
class handler(APIHandler):
    def do_POST(self):
        try:
            with connect() as conn:
                init_db(conn)
                seed_defaults(conn)
            self.send_json(200,{"ok":True,"message":"Sample tasks restored"})
        except Exception as e: self.send_json(500,{"error":str(e)})
