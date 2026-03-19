import sqlite3
conn = sqlite3.connect("memory/memory.db")
cursor = conn.cursor()

def init_db():
    # ALWAYS ensure schema exists
    print("-"*60)
    print("Initializing db for long term memory ")
    print("-"*60)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        language TEXT
    )
    """)

    conn.commit()
    
def get_user():
    cursor.execute("SELECT name, age, language FROM users LIMIT 1")
    row = cursor.fetchone()
    if row:
        return {"name": row[0], "age": row[1], "language": row[2]}
    return None

def save_user(name, age=None, language=None):
    cursor.execute(
        "INSERT INTO users (name, age, language) VALUES (?, ?, ?)",
        (name, age, language)
    )
    conn.commit()

def update_age(name , age ):
    cursor.execute(
            "UPDATE users SET age = ? where name = ? "
            (age, name)
            )
    conn.commit()

