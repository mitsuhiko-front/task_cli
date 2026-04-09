from src.model.model import TaskProperty
from psycopg2.extras import RealDictCursor

class TaskRepository:
    def __init__(self, db):
        self.db = db

    def insert(self, task: TaskProperty):
        cursor = self.db.cursor()

        cursor.execute("""
        INSERT INTO tasks (description, status, user_id, created_at, updated_at)
        VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING id
        """, (task.description, task.status, task.user_id))

        row = cursor.fetchone()
        new_id = row["id"]
        self.db.conn.commit()
        cursor.close()
        return new_id

    def delete(self, task_id: int) -> bool:
        cursor = self.db.cursor()

        cursor.execute("""
        UPDATE tasks
        SET deleted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND deleted_at IS NULL
        RETURNING id
        """, (task_id,))

        deleted = cursor.fetchone()

        self.db.conn.commit()
        cursor.close()
        return deleted is not None

    def restore(self, task_id: int) -> bool:
        cursor = self.db.cursor()
        

        cursor.execute("""
        UPDATE tasks
        SET deleted_at = NULL, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND deleted_at IS NOT NULL
        RETURNING id
        """, (task_id,))

        restored = cursor.fetchone()

        self.db.conn.commit()
        cursor.close()

        return restored is not None

    def update(self, task: TaskProperty):
        cursor = self.db.cursor()

        cursor.execute("""
        UPDATE tasks
        SET description = %s, status = %s, updated_at = CURRENT_TIMESTAMP
        WHERE id = %s AND deleted_at IS NULL
        RETURNING id
        """, (task.description, task.status, task.id))

        updated = cursor.fetchone()

        self.db.conn.commit()
        cursor.close()
        return updated is not None

    def find_by_id(self, task_id: int):
        cursor = self.db.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE id = %s AND deleted_at IS NULL
        """, (task_id,))

        row = cursor.fetchone()
        return self._row_to_task(row)
    
    def find_by_deleted_id(self, task_id: int):
        cursor = self.db.cursor()

        cursor.execute("""
        SELECT * FROM tasks
        WHERE id = %s AND deleted_at IS NOT NULL
        """, (task_id,))

        row = cursor.fetchone()
        return self._row_to_task(row)
    
    def find_all(self, user_id: int):
        cursor = self.db.cursor()
        cursor.execute("""
        SELECT * FROM tasks
        WHERE user_id = %s AND deleted_at IS NULL
        ORDER BY id
        """,(user_id,))

        rows = cursor.fetchall()
        return [self._row_to_task(row) for row in rows]

    def find_by_status(self, status: str):
        cursor = self.db.cursor()

        cursor.execute(
            """
            SELECT id, description, status, user_id, created_at, updated_at, deleted_at
            FROM tasks
            WHERE status = %s AND deleted_at IS NULL
            """,
            (status,)
        )

        rows = cursor.fetchall()
        cursor.close()

        return [self._row_to_task(row) for row in rows]
    
    def exists(self, task_id: int) -> bool:
        cursor = self.db.cursor()
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