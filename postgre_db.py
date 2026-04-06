import os
import psycopg2
from sqlite_db import SQLiteDatabase

def get_db():
    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return PostgreSQLDatabase(database_url)
    else:
        return SQLiteDatabase()

class PostgreSQLDatabase:
    def __init__(self, database_url: str):
        self.conn = psycopg2.connect(database_url, sslmode="require")

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id SERIAL PRIMARY KEY,
                description TEXT NOT NULL,
                status TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                createdAt TEXT NOT NULL,
                updatedAt TEXT NOT NULL,
                deletedAt TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        self.conn.commit()
