import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


def get_connection():
    """Create a fresh MySQL connection using values from .env."""
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "livecart"),
        connection_timeout=8,
    )


def read_sql(query, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        connection.close()


def execute_sql(query, params=None):
    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        connection.commit()
        inserted_id = cursor.lastrowid
        cursor.close()
        return inserted_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
