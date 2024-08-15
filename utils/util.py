import logging
import os

import tensorflow as tf

from model.training_script import preprocess_data, train_model
from utils.connection_pool import SQLiteConnectionPool

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """
    Function to establish a connection to the database and set the row factory.
    Returns a database connection object.
    """
    # conn = sqlite3.connect('utils/stock_predictions.db')
    # conn.row_factory = sqlite3.Row
    db_path = 'utils/stock_predictions.db'
    pool = SQLiteConnectionPool(db_path, pool_size=10)
    conn = pool.get_connection()

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


def predict_algo(stock, symbol):
    model_file = 'model/optimized_stock_prediction_model.h5'
    if not os.path.exists(model_file):
        logger.info(f"{model_file} not found. Training model...")
        train_model('AAPL')

    model = tf.keras.models.load_model('optimized_stock_prediction_model.h5')
    try:
        X, y = preprocess_data(stock)
        # Predict the next day's closing price
        prediction = model.predict(X[-1].reshape(1, 1, X.shape[2]))
        return float(prediction[0][0])
    except Exception as e:
        logger.error(f"Error predicting for {symbol}: {e}")
        return None

def check_index_existence(index_name, table_name):
    """
    Check if a specific index exists in the database.

    :param table_name: The name of the table to check.
    :param index_name: The name of the index to check.
    :return: Boolean indicating if the index exists or not.
    """
    try:
        query = f'PRAGMA index_list({table_name})'
        indices = execute_query(query, fetchall=True)
        return any(index['name'] == index_name for index in indices)
    except Exception as e:
        logger.error(f"Error checking index existence: {e}")
        return False
