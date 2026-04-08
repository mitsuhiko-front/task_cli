
class TaskQueryService:
    def __init__(self, db):
        self.conn = db.conn

    def find_task_with_user_by_id(self, task_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT tasks.id, tasks.description, tasks.status, users.username
        FROM tasks
        JOIN users ON users.id = tasks.user_id
        WHERE tasks.id = %s AND tasks.deleted_at IS NULL
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

    def find_all_with_user(self, user_id):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT tasks.id, tasks.description, tasks.status, users.username
        FROM tasks
        JOIN users ON users.id = tasks.user_id
        WHERE tasks.user_id = %s AND tasks.deleted_at IS NULL
        """, (user_id,))

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