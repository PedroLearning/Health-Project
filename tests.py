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

