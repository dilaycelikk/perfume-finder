import sqlite3

def get_db():
    conn = sqlite3.connect('perfume.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
        
    # Check if database is already seeded to prevent duplicates
    count = conn.execute('SELECT COUNT(*) FROM perfumes').fetchone()[0]
    if count == 0:
        with open('seed.sql', 'r') as f:
            conn.executescript(f.read())
            
    conn.commit()
    conn.close()