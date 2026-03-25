import sqlite3

with sqlite3.connect("app.db") as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = conn.commit()
    task = cur.lastrowid
    print(task)
    
import os
print(os.path.abspath("app.db"))    