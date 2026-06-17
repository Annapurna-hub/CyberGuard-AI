import sqlite3

conn = sqlite3.connect("users.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fullname TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS assessments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    platform TEXT,
    risk_score INTEGER,
    risk_level TEXT
)
""")

conn.commit()
conn.close()

print("Assessment table created successfully!")
