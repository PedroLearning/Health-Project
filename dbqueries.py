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

def get_questions_en(per_page=25, current_page=1):

    offset = (current_page - 1) * per_page

    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT q.question, q.answer, g.name, c.name, q.votes 
            FROM questions q
            JOIN groups g ON g.id_group = q.id_group
            JOIN categories c ON c.id_category = q.id_category
            LIMIT ? OFFSET ?
        ''', (per_page ,offset,))
        rows = cursor.fetchall()
    return rows

def get_count_questions_en():
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM questions')
        count = cursor.fetchone()[0]
    return count

def get_questions_category_en(category_id):
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT q.question, q.answer, g.name, c.name, q.votes 
            FROM questions q
            JOIN groups g ON g.id_group = q.id_group
            JOIN categories c ON c.id_category = q.id_category
            WHERE c.id_category = ?
        ''', (category_id,))
        rows = cursor.fetchall()
    return rows

def get_user_by_username(username):
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_user, username, password_hash FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

def get_user_by_email(email):
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_user, email, password_hash FROM users WHERE email = ?', (email,))
        return cursor.fetchone()


def get_user_by_id(user_id):
    """Fetches user information based on user ID (needed for Flask-Login sessions)."""
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_user, username, email FROM users WHERE id_user = ?', (user_id,))
        return cursor.fetchone()

def register_user(username, email, hashed_password):
    hashed_password = generate_password_hash("password")

    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', (username, email, hashed_password,))
        conn.commit()
