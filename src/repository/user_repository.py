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

        
