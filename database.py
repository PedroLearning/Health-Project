import sqlite3

conn = sqlite3.connect('FAQHealth.db')
cursor = conn.cursor()

def create_tables():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
        id_group INT PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        grade TEXT);''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
        id_question TINYINT PRIMARY KEY AUTOINCREMENT,
        id_group TINYINT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        pergunta TEXT NOT NULL,
        resposta TEXT NOT NULL,
        votes SMALLINT DEFAULT 0,
        FOREIGN KEY (id_group) REFERENCES groups(id_group));''')
    conn.commit()
    conn.close()