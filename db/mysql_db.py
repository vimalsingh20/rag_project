import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def get_connection():

    conn = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "rag_db"),
        port=int(os.getenv("MYSQL_PORT", "3306"))
    )

    print("MySQL connected successfully")

    return conn