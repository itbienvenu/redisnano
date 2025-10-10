import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT
        )
    """)
    conn.commit()
    return conn

def mock_data():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users(id, username, email) VALUES ('1','bienvenu','bienvenu@gmail.com')")
    conn.commit()
# mock_data()    