import sqlite3

with sqlite3.connect("app.db") as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, user_id FROM tasks;")
    rows = cur.fetchall()
    print(rows)
    
import os
print(os.path.abspath("app.db"))    