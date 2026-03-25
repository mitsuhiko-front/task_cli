
class TaskQueryService:
    def __init__(self, db):
        self.conn = db.conn

    def find_task_with_user_by_id(self, task_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT tasks.id, tasks.description, tasks.status, users.username
        FROM tasks
        JOIN users ON users.id = tasks.user_id
        WHERE tasks.id = ? AND tasks.deletedAt IS NULL
        """, (task_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": row["id"],
            "description": row["description"],
            "status": row["status"],
            "username": row["username"]
        }

    def find_all_with_user(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT tasks.id, tasks.description, tasks.status, users.username
        FROM tasks
        JOIN users ON users.id = tasks.user_id
        WHERE tasks.deletedAt IS NULL
        """)

        rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "description": row["description"],
                "status": row["status"],
                "username": row["username"]
            }
            for row in rows
        ]