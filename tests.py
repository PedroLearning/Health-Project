import sqlite3
from werkzeug.security import generate_password_hash

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
    # 2. Scramble "password" using Python
    hashed_password = generate_password_hash("password")
    
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        # 3. Save the securely hashed string instead of raw text
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("testuser", hashed_password))
        conn.commit()
        print("Inserted test user with a secure hash!")

def get_user():
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        user = cursor.fetchall()
    return user

insert_user()
user = get_user()
print(user)