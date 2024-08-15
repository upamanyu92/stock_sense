# app.py
import logging

from flask import Flask, render_template
from flask import jsonify

from utils.util import execute_query, check_index_existence

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# API endpoint to get stocks with the biggest profit
@app.route('/get_predictions', methods=['GET'])
def get_top_stocks():
    query = '''
        SELECT company_name, security_id, current_price, predicted_price, (predicted_price - current_price) AS profit
        FROM predictions_linear
        WHERE active = 1
        ORDER BY profit DESC
    '''
    rows = execute_query(query, fetchall=True)

    stocks = []
    for row in rows:
        # Check if any value is None and provide a default value (e.g., 0.0)
        company_name = row.get("company_name", "")
        security_id = row.get("security_id", "")
        current_price = row.get("current_price")
        predicted_price = row.get("predicted_price")
        profit = row.get("profit")

        # Provide default values if any of these are None
        current_price = float(current_price) if current_price is not None else 0.0
        predicted_price = float(predicted_price) if predicted_price is not None else 0.0
        profit = float(profit) if profit is not None else 0.0

        stock = {
            "company_name": company_name,
            "security_id": security_id,
            "current_price": current_price,
            "predicted_price": predicted_price,
            "profit": profit
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
    if not check_index_existence('idx_security_id_linear', 'predictions_linear'):
        logger.error("Index idx_security_id_linear does not exist")
        return
    return render_template('index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

