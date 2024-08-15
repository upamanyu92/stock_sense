import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from flask import Flask, jsonify, render_template

from dataclass_db.dataclass_db_executor import fetch_quotes_batch
from executors.executor import prediction_executor, data_retriever_executor
from utils.util import get_db_connection

app = Flask(__name__)


@app.route('/trigger_prediction', methods=['POST'])
def trigger_prediction():
    offset = 0
    batch_size = 3
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_data_retriever = executor.submit(data_retriever_executor)
        future_data_retriever.result()
        futures = []
        while True:
            batch = fetch_quotes_batch(batch_size, offset)
            if len(batch) == 3:
                logging.info("Batch: ", batch)
                futures.append(executor.submit(prediction_executor, batch[0].__dict__))
                futures.append(executor.submit(prediction_executor, batch[1].__dict__))
                futures.append(executor.submit(prediction_executor, batch[2].__dict__))
            else:
                for quote in batch:
                    logging.info("Quote: ", quote)
                    executor.submit(prediction_executor, quote)
                break
            for future in as_completed(futures):
                try:
                    future.result()  # Block until each future is done
                except Exception as e:
                    logging.error(f"An error occurred during prediction: {e}")

            offset += batch_size
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
