from datetime import datetime
from model import TaskProperty

class TaskRepository:
    def __init__(self, db):
        self.conn = db.conn

    def insert(self, task: TaskProperty):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO tasks (description, status, user_id, created_at, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (task.description, task.status, task.user_id))

        self.conn.commit()
        return cursor.lastrowid

    def delete(self, task_id: int) -> bool:
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE tasks
        SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND deleted_at IS NULL
        """, (task_id,))

        self.conn.commit()
        return cursor.rowcount > 0

    def restore(self, task_id: int) -> bool:
        cursor = self.conn.cursor()
        

        cursor.execute("""
        UPDATE tasks
        SET deleted_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND deleted_at IS NOT NULL
        """, (task_id,))

        self.conn.commit()
        return cursor.rowcount > 0

    def update(self, task: TaskProperty):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE tasks
        SET description = ?, status = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ? AND deleted_at IS NULL
        """, (task.description, task.status, task.id))

        self.conn.commit()
        return cursor.rowcount > 0

    def find_by_id(self, task_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE id = ? AND deleted_at IS NULL
        """, (task_id,))

        row = cursor.fetchone()
        return self._row_to_task(row)
    
    def find_by_deleted_id(self, task_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE id = ? AND deleted_at IS NOT NULL
        """, (task_id,))

        row = cursor.fetchone()
        return self._row_to_task(row)
    
    def find_all(self, user_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE user_id = ? AND deleted_at IS NULL
        ORDER BY id
        """,(user_id,))

        rows = cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    def exists(self, task_id: int) -> bool:
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT 1 FROM tasks
        WHERE id = ? AND deleted_at IS NULL
        """, (task_id,))

        return cursor.fetchone() is not None

    def _row_to_task(self, row):
        if row is None:
            return None

        return TaskProperty(
            id=row["id"],
            description=row["description"],
            status=row["status"],
            user_id=row["user_id"], 
            created_at=row["createdat"],
            updated_at=row["updatedat"],
            deleted_at=row["deletedat"]
        )
class UserRepository:
    def __init__(self, db):
        self.conn = db.conn

    def find_by_id(self, user_id: int):
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": int(row["id"]),
            "username": row["username"],
            "created_at": row["createdat"],
            "updated_at": row["updatedat"]
        }
    def find_by_username(self, username: str):
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?", 
            (username,)
        )

        row = cursor.fetchone()

        if row is None:
            return None
        
        return {
            "id":row["id"],
            "username":row["username"],
            "password":row["password"],
            "created_at": row["createdat"],
            "updated_at": row["updatedat"]
        }
    def insert(self, username: str, password: str):
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, created_at, updated_at)" \
            "VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            , (username, password) 
        )

        self.conn.commit()

        return self.find_by_username(username)

        
