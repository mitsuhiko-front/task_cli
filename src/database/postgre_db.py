import os
import psycopg2
from psycopg2.extras import RealDictCursor

def create_db():
    return PostgreSQLDatabase(os.getenv("DATABASE_URL"))

def get_db():
    db = create_db()
    try:
        yield db
    finally:
        db.close()

    return 

class PostgreSQLDatabase:
    def __init__(self, database_url: str):
        self.conn = psycopg2.connect(database_url)
        self.conn.autocommit = True


    def cursor(self):
        return self.conn.cursor(cursor_factory=RealDictCursor)
    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deleted_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self.conn.commit()
