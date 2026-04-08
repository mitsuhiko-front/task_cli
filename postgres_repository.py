from model import TaskProperty

class TaskRepository:
    def __init__(self, db):
        self.conn = db.conn

    def insert(self, task: TaskProperty):
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO tasks (description, status, user_id, created_at, updated_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id
        """, (task.description, task.status, task.user_id))

        new_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        return new_id

    def delete(self, task_id: int) -> bool:
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE tasks
        SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND deleted_at IS NULL
        RETURNING id
        """, (task_id,))

        deleted = cursor.fetchone()

        self.conn.commit()
        cursor.close()
        return deleted is not None

    def restore(self, task_id: int) -> bool:
        cursor = self.conn.cursor()
        

        cursor.execute("""
        UPDATE tasks
        SET deleted_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND deleted_at IS NOT NULL
        RETURNING id
        """, (task_id,))

        restored = cursor.fetchone()

        self.conn.commit()
        cursor.close()

        return restored is not None

    def update(self, task: TaskProperty):
        cursor = self.conn.cursor()

        cursor.execute("""
        UPDATE tasks
        SET description = %s, status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND deleted_at IS NULL
        RETURNING id
        """, (task.description, task.status, task.id))

        updated = cursor.fetchone()

        self.conn.commit()
        cursor.close()
        return updated is not None

    def find_by_id(self, task_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE id = %s AND deleted_at IS NULL
        """, (task_id,))

        row = cursor.fetchone()
        return self._row_to_task(row)
    
    def find_by_deleted_id(self, task_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE id = %s AND deleted_at IS NOT NULL
        """, (task_id,))

        row = cursor.fetchone()
        return self._row_to_task(row)
    
    def find_all(self, user_id: int):
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE user_id = %s AND deleted_at IS NULL
        ORDER BY id
        """,(user_id,))

        rows = cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    def exists(self, task_id: int) -> bool:
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT 1 FROM tasks
        WHERE id = %s AND deleted_at IS NULL
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
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            deleted_at=row["deleted_at"]
        )
class UserRepository:
    def __init__(self, db):
        self.conn = db.conn

    def find_by_id(self, user_id: int):
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE id = %s",
            (user_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return {
            "id": int(row["id"]),
            "username": row["username"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    def find_by_username(self, username: str):
        cursor = self.conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = %s", 
            (username,)
        )

        row = cursor.fetchone()

        if row is None:
            return None
        
        return {
            "id":row["id"],
            "username":row["username"],
            "password":row["password"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    def insert(self, username: str, password: str):
        cursor = self.conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, password, created_at, updated_at)" \
            "VALUES (%s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
            , (username, password) 
        )

        self.conn.commit()

        return self.find_by_username(username)

        
