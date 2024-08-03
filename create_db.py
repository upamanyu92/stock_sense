import sqlite3

conn = sqlite3.connect('predicted_prices.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS predictions_linear (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        security_id TEXT UNIQUE,
        current_price REAL,
        predicted_price REAL,
        prediction_date TEXT,
        active INTEGER DEFAULT 1
    )
''')

c.execute('''
    CREATE TABLE IF NOT EXISTS predictions_lstm (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company_name TEXT,
        security_id TEXT UNIQUE,
        current_price REAL,
        predicted_price REAL,
        prediction_date TEXT
    )
''')

c.execute('''
    CREATE UNIQUE INDEX IF NOT EXISTS idx_security_id_linear
    ON predictions_linear (security_id)
''')

c.execute('''
    CREATE UNIQUE INDEX IF NOT EXISTS idx_security_id_lstm
    ON predictions_lstm (security_id)
''')

conn.commit()
conn.close()
