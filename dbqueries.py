import sqlite3

DBFILE = 'FAQHealth.db'
category = 'Mental Health and Socio-Emotional Skills'

def create_connection():

    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()

    try:
        conn = sqlite3.connect(DBFILE)
        print(f"Connected to database: {DBFILE}")
    except sqlite3.Error as e:
        print(e)
    return conn

def get_questions_by_category(category):

    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()

    conn = sqlite3.connect(DBFILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT question, answer 
        FROM questions
        JOIN groups ON groups.id = questions.id_group
        WHERE category = ?
    ''', (category,))
    rows = cursor.fetchall()
    conn.close()
    return rows


create_connection()
questions = get_questions_by_category(category)
print(f'Questions for category "{category}":')
for question, answer in questions:
    print(f'Q: {question}')
    print(f'A: {answer}')
    print()