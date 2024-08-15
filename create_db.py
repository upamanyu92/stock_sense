import sqlite3




def create_db():
    print("Creating database...")
    conn = sqlite3.connect('utils/stock_predictions.db')
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
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            security_id TEXT UNIQUE,
            current_price REAL,
            predicted_price REAL,
            prediction_date TEXT
        )''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS stock_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                current_value REAL,
                change REAL,
                p_change REAL,
                updated_on TEXT,
                security_id TEXT UNIQUE,
                scrip_code TEXT,
                group_type TEXT,
                face_value REAL,
                industry TEXT,
                previous_close REAL,
                previous_open REAL,
                day_high REAL,
                day_low REAL,
                week_52_high REAL,
                week_52_low REAL,
                weighted_avg_price REAL,
                total_traded_value TEXT,
                total_traded_quantity TEXT,
                two_week_avg_quantity TEXT,
                market_cap_full TEXT,
                market_cap_free_float TEXT,
                buy_1_quantity TEXT,
                buy_1_price REAL,
                buy_2_quantity TEXT,
                buy_2_price REAL,
                buy_3_quantity TEXT,
                buy_3_price REAL,
                buy_4_quantity TEXT,
                buy_4_price REAL,
                buy_5_quantity TEXT,
                buy_5_price REAL,
                sell_1_quantity TEXT,
                sell_1_price REAL,
                sell_2_quantity TEXT,
                sell_2_price REAL,
                sell_3_quantity TEXT,
                sell_3_price REAL,
                sell_4_quantity TEXT,
                sell_4_price REAL,
                sell_5_quantity TEXT,
                sell_5_price REAL
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

    c.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_security_id
        ON predictions (security_id)
        ''')

    conn.commit()
    conn.close()

if  __name__ == '__main__':
    create_db()