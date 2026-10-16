from pathlib import Path
import os

import mysql.connector
from dotenv import load_dotenv

project_folder = Path(__file__).resolve().parent.parent
load_dotenv(project_folder / ".env")

connection = mysql.connector.connect(
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    connection_timeout=5,
)

try:
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT DATABASE(), CURRENT_USER()")
        database, account = cursor.fetchone()

        print(f"Connected database: {database}")
        print(f"Authenticated account: {account}")

        cursor.execute("SELECT COUNT(*) FROM users")
        print(f"Users currently stored: {cursor.fetchone()[0]}")
    finally:
        cursor.close()
finally:
    connection.close()