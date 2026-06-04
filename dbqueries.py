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

def get_questions_en(per_page=25, current_page=1, category_id=None, sort_by='most_relevant', search_query=None):
    offset = (current_page - 1) * per_page
   
    #SQL sort mapping
    sort_mapping = {
        'most_relevant': 'q.votes DESC',
        'oldest': 'q.id_question ASC',
        'newest': 'q.id_question DESC',
        'alphabetical': 'q.question ASC'
    }
    order_clause = sort_mapping.get(sort_by, 'q.id_question DESC')

    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
       
        sql = '''
            SELECT q.question, q.answer, g.name, c.name, q.votes
            FROM questions q
            JOIN groups g ON g.id_group = q.id_group
            JOIN categories c ON c.id_category = q.id_category
        '''
       
        if category_id and search_query:
            query = f"{sql} WHERE q.id_category = ? AND q.question LIKE ? ORDER BY {order_clause} LIMIT ? OFFSET ?"
            cursor.execute(query, (category_id, f'%{search_query}%', per_page, offset))
        elif category_id:
            query = f"{sql} WHERE q.id_category = ? ORDER BY {order_clause} LIMIT ? OFFSET ?"
            cursor.execute(query, (category_id, per_page, offset))
        elif search_query:
            query = f"{sql} WHERE q.question LIKE ? ORDER BY {order_clause} LIMIT ? OFFSET ?"
            cursor.execute(query, (f'%{search_query}%', per_page, offset))
        else:
            query = f"{sql} ORDER BY {order_clause} LIMIT ? OFFSET ?"
            cursor.execute(query, (per_page, offset))
           
        return cursor.fetchall()

def get_count_questions_en(category_id=None, search_query=None):
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        if category_id and search_query:
            cursor.execute('SELECT COUNT(*) FROM questions WHERE id_category = ? AND question LIKE ?', (category_id, f'%{search_query}%'))
        elif category_id:
            cursor.execute('SELECT COUNT(*) FROM questions WHERE id_category = ?', (category_id,))
        elif search_query:
            cursor.execute('SELECT COUNT(*) FROM questions WHERE question LIKE ?', (f'%{search_query}%',))
        else:
            cursor.execute('SELECT COUNT(*) FROM questions')
        return cursor.fetchone()[0]

# Needed for login_user() in app.py
def get_user_by_username(username):
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_user, username, password_hash FROM users WHERE username = ?', (username,))
        return cursor.fetchone()

# Needed for login_user() in app.py
def get_user_by_email(email):
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_user, email, password_hash FROM users WHERE email = ?', (email,))
        return cursor.fetchone()

# Needed for login_user() in app.py
def get_user_by_id(user_id):
    """Fetches user information based on user ID (needed for Flask-Login sessions)."""
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id_user, username, email FROM users WHERE id_user = ?', (user_id,))
        return cursor.fetchone()

# Needed for register_user() in app.py
def register_user(username, email, password):
    hashed_password = generate_password_hash(password)

    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', (username, email, hashed_password,))
        conn.commit()
