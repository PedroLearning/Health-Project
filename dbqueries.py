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

def get_questions_en():
    with sqlite3.connect(DBFILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT q.question, q.answer, g.name, c.name, q.votes 
            FROM questions q
            JOIN groups g ON g.id_group = q.id_group
            JOIN categories c ON c.id_category = q.id_category
        ''')
        rows = cursor.fetchall()
    return rows

#try:
    rows = get_questions_en()
    for question, answer, group, category, votes in rows:
        print(question)
        print(answer)
        print(group)
        print(category)
        print(votes)
#except Exception as e:
    print(f"An error occurred: {e}")

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

#input("Press Enter to exit...")
