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

def get_questions_by_category():
    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT q.question, q.answer 
        FROM questions q
        JOIN groups g ON g.id_group = q.id_group
        JOIN categories c ON c.id_category = q.id_category
    ''',)
    rows = cursor.fetchall()
    conn.close()
    return rows


create_connection()
questions = get_questions_by_category()
print(f'Questions:}')
for question, answer in questions:
    print(f'Q: {question}')
    print(f'A: {answer}')
    print()

    