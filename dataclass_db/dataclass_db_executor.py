import sqlite3

from dataclass_db.stock_predictions import StockQuote
from utils.util import get_db_connection


def execute_query(query, args=(), fetchone=False, fetchall=False, commit=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(query, args)
        if commit:
            conn.commit()
        if fetchone:
            result = cursor.fetchone()
        elif fetchall:
            result = cursor.fetchall()
        else:
            result = None
    except Exception as e:
        print(f"An error occurred while executing query: {query}: {e}")
        result = None
    finally:
        conn.close()
    return result

def insert_stock_quote(quote):
    conn = get_db_connection()
    c = conn.cursor()

    # Insert data into the table
    data = {
        'company_name': quote.get('companyName', None),
        'current_value': float(quote.get('currentValue', 0.0)),
        'change': float(quote.get('change', 0.0)),
        'p_change': float(quote.get('pChange', 0.0)),
        'updated_on': quote.get('updatedOn', None),
        'security_id': quote.get('securityID', None),
        'scrip_code': quote.get('scripCode', None),
        'group_type': quote.get('group', None),
        'face_value': float(quote.get('faceValue', 0.0)),
        'industry': quote.get('industry', None),
        'previous_close': float(quote.get('previousClose', 0.0)),
        'previous_open': float(quote.get('previousOpen', 0.0)),
        'day_high': float(quote.get('dayHigh', 0.0)),
        'day_low': float(quote.get('dayLow', 0.0)),
        'week_52_high': float(quote.get('52weekHigh', 0.0)),
        'week_52_low': float(quote.get('52weekLow', 0.0)),
        'weighted_avg_price': float(quote.get('weightedAvgPrice', 0.0)),
        'total_traded_value': quote.get('totalTradedValue', None),
        'total_traded_quantity': quote.get('totalTradedQuantity', None),
        'two_week_avg_quantity': quote.get('2WeekAvgQuantity', None),
        'market_cap_full': quote.get('marketCapFull', None),
        'market_cap_free_float': quote.get('marketCapFreeFloat', None),
        'buy_1_quantity': quote.get('buy', {}).get('1', {}).get('quantity', None),
        'buy_1_price': float(quote.get('buy', {}).get('1', {}).get('price', 0.0)),
        'buy_2_quantity': quote.get('buy', {}).get('2', {}).get('quantity', None),
        'buy_2_price': float(quote.get('buy', {}).get('2', {}).get('price', 0.0)),
        'buy_3_quantity': quote.get('buy', {}).get('3', {}).get('quantity', None),
        'buy_3_price': float(quote.get('buy', {}).get('3', {}).get('price', 0.0)),
        'buy_4_quantity': quote.get('buy', {}).get('4', {}).get('quantity', None),
        'buy_4_price': float(quote.get('buy', {}).get('4', {}).get('price', 0.0)),
        'buy_5_quantity': quote.get('buy', {}).get('5', {}).get('quantity', None),
        'buy_5_price': float(quote.get('buy', {}).get('5', {}).get('price', 0.0)),
        'sell_1_quantity': quote.get('sell', {}).get('1', {}).get('quantity', None),
        'sell_1_price': float(quote.get('sell', {}).get('1', {}).get('price', 0.0)),
        'sell_2_quantity': quote.get('sell', {}).get('2', {}).get('quantity', None),
        'sell_2_price': float(quote.get('sell', {}).get('2', {}).get('price', 0.0)),
        'sell_3_quantity': quote.get('sell', {}).get('3', {}).get('quantity', None),
        'sell_3_price': float(quote.get('sell', {}).get('3', {}).get('price', 0.0)),
        'sell_4_quantity': quote.get('sell', {}).get('4', {}).get('quantity', None),
        'sell_4_price': float(quote.get('sell', {}).get('4', {}).get('price', 0.0)),
        'sell_5_quantity': quote.get('sell', {}).get('5', {}).get('quantity', None),
        'sell_5_price': float(quote.get('sell', {}).get('5', {}).get('price', 0.0))
    }

    try:
        c.execute('''
            INSERT INTO stock_quotes (
                company_name, current_value, change, p_change, updated_on,
                security_id, scrip_code, group_type, face_value, industry,
                previous_close, previous_open, day_high, day_low, week_52_high, 
                week_52_low, weighted_avg_price, total_traded_value, total_traded_quantity, 
                two_week_avg_quantity, market_cap_full, market_cap_free_float,
                buy_1_quantity, buy_1_price, buy_2_quantity, buy_2_price, 
                buy_3_quantity, buy_3_price, buy_4_quantity, buy_4_price, 
                buy_5_quantity, buy_5_price, sell_1_quantity, sell_1_price, 
                sell_2_quantity, sell_2_price, sell_3_quantity, sell_3_price, 
                sell_4_quantity, sell_4_price, sell_5_quantity, sell_5_price
            ) VALUES (
                :company_name, :current_value, :change, :p_change, :updated_on,
                :security_id, :scrip_code, :group_type, :face_value, :industry,
                :previous_close, :previous_open, :day_high, :day_low, :week_52_high, 
                :week_52_low, :weighted_avg_price, :total_traded_value, :total_traded_quantity, 
                :two_week_avg_quantity, :market_cap_full, :market_cap_free_float,
                :buy_1_quantity, :buy_1_price, :buy_2_quantity, :buy_2_price, 
                :buy_3_quantity, :buy_3_price, :buy_4_quantity, :buy_4_price, 
                :buy_5_quantity, :buy_5_price, :sell_1_quantity, :sell_1_price, 
                :sell_2_quantity, :sell_2_price, :sell_3_quantity, :sell_3_price, 
                :sell_4_quantity, :sell_4_price, :sell_5_quantity, :sell_5_price
            )
            ON CONFLICT(security_id) DO UPDATE SET
                company_name=excluded.company_name,
                current_value=excluded.current_value,
                change=excluded.change,
                p_change=excluded.p_change,
                updated_on=excluded.updated_on,
                scrip_code=excluded.scrip_code,
                group_type=excluded.group_type,
                face_value=excluded.face_value,
                industry=excluded.industry,
                previous_close=excluded.previous_close,
                previous_open=excluded.previous_open,
                day_high=excluded.day_high,
                day_low=excluded.day_low,
                week_52_high=excluded.week_52_high,
                week_52_low=excluded.week_52_low,
                weighted_avg_price=excluded.weighted_avg_price,
                total_traded_value=excluded.total_traded_value,
                total_traded_quantity=excluded.total_traded_quantity,
                two_week_avg_quantity=excluded.two_week_avg_quantity,
                market_cap_full=excluded.market_cap_full,
                market_cap_free_float=excluded.market_cap_free_float,
                buy_1_quantity=excluded.buy_1_quantity,
                buy_1_price=excluded.buy_1_price,
                buy_2_quantity=excluded.buy_2_quantity,
                buy_2_price=excluded.buy_2_price,
                buy_3_quantity=excluded.buy_3_quantity,
                buy_3_price=excluded.buy_3_price,
                buy_4_quantity=excluded.buy_4_quantity,
                buy_4_price=excluded.buy_4_price,
                buy_5_quantity=excluded.buy_5_quantity,
                buy_5_price=excluded.buy_5_price,
                sell_1_quantity=excluded.sell_1_quantity,
                sell_1_price=excluded.sell_1_price,
                sell_2_quantity=excluded.sell_2_quantity,
                sell_2_price=excluded.sell_2_price,
                sell_3_quantity=excluded.sell_3_quantity,
                sell_3_price=excluded.sell_3_price,
                sell_4_quantity=excluded.sell_4_quantity,
                sell_4_price=excluded.sell_4_price,
                sell_5_quantity=excluded.sell_5_quantity,
                sell_5_price=excluded.sell_5_price
        ''', data)

        conn.commit()
    except sqlite3.IntegrityError as e:
        print(f"Error occurred: {e}")
    finally:
        conn.close()


def fetch_quotes_batch(batch_size, offset=0):
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        SELECT * FROM stock_quotes LIMIT ? OFFSET ?
    ''', (batch_size, offset))

    rows = c.fetchall()
    conn.close()

    stock_quotes = [
        StockQuote(
            id=row[0],
            company_name=row[1],
            current_value=row[2],
            change=row[3],
            p_change=row[4],
            updated_on=row[5],
            security_id=row[6],
            scrip_code=row[7],
            group_type=row[8],
            face_value=row[9],
            industry=row[10],
            previous_close=row[11],
            previous_open=row[12],
            day_high=row[13],
            day_low=row[14],
            week_52_high=row[15],
            week_52_low=row[16],
            weighted_avg_price=row[17],
            total_traded_value=row[18],
            total_traded_quantity=row[19],
            two_week_avg_quantity=row[20],
            market_cap_full=row[21],
            market_cap_free_float=row[22],
            buy_1_quantity=row[23],
            buy_1_price=row[24],
            buy_2_quantity=row[25],
            buy_2_price=row[26],
            buy_3_quantity=row[27],
            buy_3_price=row[28],
            buy_4_quantity=row[29],
            buy_4_price=row[30],
            buy_5_quantity=row[31],
            buy_5_price=row[32],
            sell_1_quantity=row[33],
            sell_1_price=row[34],
            sell_2_quantity=row[35],
            sell_2_price=row[36],
            sell_3_quantity=row[37],
            sell_3_price=row[38],
            sell_4_quantity=row[39],
            sell_4_price=row[40],
            sell_5_quantity=row[41],
            sell_5_price=row[42]
        ) for row in rows
    ]

    return stock_quotes