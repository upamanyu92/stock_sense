import logging
from datetime import datetime

from bsedata.bse import BSE

from dataclass_db.dataclass_db_executor import execute_query, insert_stock_quote
from model.keras_model import predict_max_profit


def prediction_executor(data):
    try:
        logging.info(f"prediction_executor: ", data['company_name'])
        stock_symbol = data.get('security_id')
        if stock_symbol:
            stock_symbol_yahoo = stock_symbol + '.BO'  # Assuming it's a BSE stock
            predicted_price = predict_max_profit(stock_symbol_yahoo)
            current_price = float(data['current_value'].replace(',', ''))  # Handle comma in numbers
            execute_query('''
                            INSERT INTO predictions (company_name, security_id, current_price, predicted_price, prediction_date)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (data.get('company_name'), stock_symbol, current_price, predicted_price,
                              datetime.now().strftime('%Y-%m-%d %H:%M:%S')), commit=True)
        else:
            logging.warning(f"Stock symbol not found")
    except Exception as e:
        logging.error(f"Failed to update predictions {e}")

def data_retriever_executor():
    logging.info(f"data_retriever_executor: ")
    b = BSE()
    b.updateScripCodes()
    mutual_funds = b.getScripCodes()
    for code, name in mutual_funds.items():
        try:
            quote = b.getQuote(code)
            insert_stock_quote(quote)
        except Exception as e:
            logging.error(f"Downloading failed {code}: {e}")