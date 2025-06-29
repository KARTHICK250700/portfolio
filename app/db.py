import sqlite3

def init_db():
    with sqlite3.connect('portfolio.db') as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, phone TEXT, company TEXT, message TEXT)''')
        conn.commit()
