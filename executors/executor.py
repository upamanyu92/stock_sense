from datetime import datetime

from dataclass_db.dataclass_db_executor import execute_query
from model.keras_model import predict_max_profit


def prediction_executor(quote):
    try:
        print("prediction_executor: ", quote)
        stock_symbol = quote.get('securityID')
        stock_symbol_yahoo = stock_symbol + '.BO'  # Assuming it's a BSE stock
        predicted_price = predict_max_profit(stock_symbol_yahoo)
        current_price = float(quote['currentValue'].replace(',', ''))  # Handle comma in numbers
        execute_query('''
                        INSERT INTO predictions (company_name, security_id, current_price, predicted_price, prediction_date)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (quote.get('companyName'), stock_symbol, current_price, predicted_price,
                          datetime.now().strftime('%Y-%m-%d %H:%M:%S')), commit=True)
    except Exception as e:
        print(f"An error occurred while fetching data for {quote}: {e}")