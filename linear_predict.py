# app.py
import os

from flask import Flask, jsonify, render_template
import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import sqlite3
from datetime import datetime
import logging
from bsedata.bse import BSE
from yfinance.exceptions import YFInvalidPeriodError
import schedule
import time
import threading
from model.training_script import train_model

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
def get_db_connection():
    """
    Function to establish a connection to the database and set the row factory.
    Returns a database connection object.
    """
    conn = sqlite3.connect('predicted_prices.db')
    conn.row_factory = sqlite3.Row
    return conn



def execute_query(query, args=(), fetchone=False, fetchall=False, commit=False):
    """
    Execute a SQL query on the database.

    Parameters:
        query (str): The SQL query to be executed.
        args (tuple, optional): The arguments to be passed with the query. Defaults to ().
        fetchone (bool, optional): Flag to fetch only one result. Defaults to False.
        fetchall (bool, optional): Flag to fetch all results. Defaults to False.
        commit (bool, optional): Flag to commit the transaction. Defaults to False.

    Returns:
        tuple or None: The result of the query execution.
    """
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
        logger.error(f"SQL error: {e}")
        result = None
    finally:
        conn.close()
    return result

# Function to preprocess data for the model
def preprocess_data(stock):
    """
    Generate X and y arrays from stock data for machine learning model training.

    Parameters:
    - stock (DataFrame): Input stock data containing Open, High, Low, Close, Volume.

    Returns:
    - X (numpy array): Reshaped input array with dimensions [samples, time steps, features].
    - y (numpy array): Target array for the next day's Close prices.
    """
    stock['NextDayClose'] = stock['Close'].shift(-1)
    stock.dropna(inplace=True)

    X = stock[['Open', 'High', 'Low', 'Close', 'Volume']].values
    y = stock['NextDayClose'].values

    # Reshape input to be [samples, time steps, features]
    X = X.reshape((X.shape[0], 1, X.shape[1]))

    return X, y

# Function to download stock data
def download_stock_data(symbol):
    """
    Downloads stock data for a given symbol.

    Parameters:
        symbol (str): The stock symbol to download data for.

    Returns:
        pandas.DataFrame: Stock data for the given symbol, or None if download fails.
    """
    try:
        stock = yf.download(symbol, start='2010-01-01', end='2024-07-04', progress=False)
        if (stock is None) or stock.empty:
            logger.error(f"Failed to download data for {symbol}")
            return None
    except YFInvalidPeriodError as e:
        logger.error(f"Invalid period error for {symbol}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error downloading data for {symbol}: {e}")
        return None
    return stock

# Load the trained model

model_file = 'optimized_stock_prediction_model.h5'
if not os.path.exists(model_file):
    logger.info(f"{model_file} not found. Training model...")
    train_model('AAPL')

model = tf.keras.models.load_model('optimized_stock_prediction_model.h5')

# Function to predict using the optimized model
def predict_algo(stock, symbol):
    try:
        X, y = preprocess_data(stock)
        # Predict the next day's closing price
        prediction = model.predict(X[-1].reshape(1, 1, X.shape[2]))
        return float(prediction[0][0])
    except Exception as e:
        logger.error(f"Error predicting for {symbol}: {e}")
        return None

def check_index_existence(index_name):
    """
    Check if a specific index exists in the database.

    :param index_name: The name of the index to check.
    :return: Boolean indicating if the index exists or not.
    """
    try:
        query = 'PRAGMA index_list(predictions_linear)'
        indices = execute_query(query, fetchall=True)
        return any(index['name'] == index_name for index in indices)
    except Exception as e:
        logger.error(f"Error checking index existence: {e}")
        return False

@app.route('/trigger_prediction', methods=['POST'])
def trigger_prediction():
    """
    Trigger prediction for each stock in the BSE and store the predicted prices in the database.
    If necessary indexes do not exist, return an error response. Handle exceptions
    such as inactive stocks and log appropriate messages. Return a success response.
    """
    b = BSE()
    b.updateScripCodes()
    funds = b.getScripCodes()
    stock_symbol = None

    if not check_index_existence('idx_security_id_linear'):
        return jsonify({"error": "Index idx_security_id_linear does not exist"}), 500

    for code, name in funds.items():
        try:
            quote = b.getQuote(code)
            stock_symbol = quote.get('securityID')
            stock_symbol_yahoo = stock_symbol + '.BO'  # Assuming it's a BSE stock
            query = 'SELECT active FROM predictions_linear WHERE security_id = ?'
            row = execute_query(query, (stock_symbol,), fetchone=True)
            if row is None or row['active'] == 1:
                stock_data = download_stock_data(stock_symbol_yahoo)
                predicted_price = predict_algo(stock_data, stock_symbol)
                current_price = float(quote['currentValue'].replace(',', ''))  # Handle comma in numbers
                logger.debug(f"Predicted price: {predicted_price}, Current price: {current_price} for {quote.get('companyName')}")

                query = '''
                    INSERT INTO predictions_linear (company_name, security_id, current_price, predicted_price, prediction_date, active)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(security_id) DO UPDATE SET
                        company_name=excluded.company_name,
                        current_price=excluded.current_price,
                        predicted_price=excluded.predicted_price,
                        prediction_date=excluded.prediction_date,
                        active=excluded.active
                '''
                execute_query(query, (quote.get('companyName'), stock_symbol, current_price, predicted_price,
                                      datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 1), commit=True)
            else:
                logger.info(f"Stock {stock_symbol} is marked as inactive for {quote.get('companyName')}")

        except Exception as e:
            if e is not None or e == "Inactive stock":
                logger.warning(f"Stock {stock_symbol} is marked to inactive")
                query = 'UPDATE predictions_linear SET active = 0 WHERE security_id = ?'
                execute_query(query, (stock_symbol,), commit=True)

    return jsonify({"message": "Prediction triggered and data stored in database"}), 200

# API endpoint to get stocks with the biggest profit
@app.route('/get_predictions', methods=['GET'])
def get_top_stocks():
    """
    Function to retrieve and return the top stocks based on predicted price versus current price.
    Returns a JSON response containing the top stocks and a status code of 200.
    """
    query = '''
        SELECT company_name, security_id, current_price, predicted_price, (predicted_price - current_price) AS profit
        FROM predictions_linear
        WHERE active = 1
        ORDER BY profit DESC
    '''
    rows = execute_query(query, fetchall=True)

    # Handle None values in rows
    stocks = []
    for row in rows:
        company_name = row.get("company_name")
        security_id = row.get("security_id")
        current_price = row.get("current_price")
        predicted_price = row.get("predicted_price")
        profit = row.get("profit")

        # Convert to float only if the value is not None
        stock = {
            "company_name": company_name,
            "security_id": security_id,
            "current_price": float(current_price) if current_price is not None else None,
            "predicted_price": float(predicted_price) if predicted_price is not None else None,
            "profit": float(profit) if profit is not None else None
        }
        stocks.append(stock)

    return jsonify(stocks), 200


@app.route('/search/<security_id>', methods=['GET'])
def search_by_security_id(security_id):
    """
    Search for a stock by security ID and return its details if found.

    Parameters:
    - security_id: str, the unique identifier of the stock to search for

    Returns:
    - JSON response with stock details if found, HTTP status code 200
    - JSON response with error message if stock not found, HTTP status code 404
    """
    query = '''
        SELECT company_name, security_id, current_price, predicted_price, (predicted_price - current_price) AS profit
        FROM predictions_linear
        WHERE security_id = ?
    '''
    row = execute_query(query, (security_id,), fetchone=True)

    if row:
        stock = dict(row)
        return jsonify(stock), 200
    else:
        return jsonify({"message": "Security ID not found"}), 404

# Root endpoint with options
@app.route('/')
def index():
    """
    Route decorator for the index page.
    Renders the 'index.html' template.
    """
    return render_template('index.html')

def retrain_model():
    """
    Retrains the model using the stock symbol 'AAPL' and saves the updated model.
    """
    symbol = 'AAPL'
    train_model(symbol)
    global model
    model = tf.keras.models.load_model('optimized_stock_prediction_model.h5')

# Schedule the retraining task
def job():
    logger.info("Starting the scheduled job...")
    trigger_prediction()
    logger.info("Scheduled job completed.")
    schedule_next_run()

def schedule_next_run():
    schedule.clear()
    schedule.every(1).hours.do(job)

def run_scheduler():
    schedule_next_run()
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduler in a separate thread
scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
scheduler_thread.start()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
