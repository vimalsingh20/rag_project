from db.mysql_db import get_connection

conn = get_connection()

cursor = conn.cursor()

cursor.execute("SELECT DATABASE()")

print("Current DB:", cursor.fetchone())

cursor.execute("SHOW TABLES")

print("Tables:", cursor.fetchall())

cursor.execute("SELECT * FROM documents")

print("Documents:", cursor.fetchall())

conn.close()
