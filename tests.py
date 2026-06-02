import sqlite3

DBFILE = 'FAQHealth.db'

def create_connection():
    try:
        conn = sqlite3.connect(DBFILE)
        print(f"Connected to database: {DBFILE}")
        return conn
    except sqlite3.Error as e:
        print(e)
        return None

def insert_user():
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("testuser", "password"))
        conn.commit()
        print("Inserted test user")

def get_user():
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        user = cursor.fetchall()
    return user

insert_user()
user = get_user()
print(user)