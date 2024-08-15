from concurrent.futures import ThreadPoolExecutor

from bsedata.bse import BSE
from flask import Flask, jsonify, render_template

from dataclass_db.dataclass_db_executor import insert_stock_quote, fetch_quotes_batch
from executors.executor import prediction_executor
from utils.util import get_db_connection

app = Flask(__name__)


@app.route('/trigger_prediction', methods=['POST'])
def trigger_prediction():
    b = BSE()
    b.updateScripCodes()
    mutual_funds = b.getScripCodes()

    # Collect quotes first
    for code, name in mutual_funds.items():
        try:
            quote = b.getQuote(code)
            insert_stock_quote(quote)
        except Exception as e:
            print(f"An error occurred in getting quote for {code}: {e}")

    # Run prediction_executor simultaneously for 3 different quotes at a time
    with ThreadPoolExecutor(max_workers=3) as executor:
        batch = fetch_quotes_batch(3)
        if len(batch) == 3:
            executor.submit(prediction_executor, batch[0])
            executor.submit(prediction_executor, batch[1])
            executor.submit(prediction_executor, batch[2])
        else:
            for quote in batch:
                executor.submit(prediction_executor, quote)
    return jsonify({'message': 'Predictions triggered and data stored to DB'}), 200


# API endpoint to get stocks with the biggest profit
@app.route('/get_predictions', methods=['GET'])
def get_top_stocks():
    conn = get_db_connection()
    c = conn.cursor()

    c.execute('''
        SELECT company_name, security_id, current_price, predicted_price, (predicted_price - current_price) AS profit
        FROM predictions
        ORDER BY profit DESC
    ''')
    rows = c.fetchall()

    conn.close()

    stocks = [dict(row) for row in rows]

    return jsonify(stocks), 200


# Root endpoint with options
@app.route('/')
def index():
    return render_template('index_main.html')


if __name__ == '__main__':
    app.run(debug=True, port=5005)
