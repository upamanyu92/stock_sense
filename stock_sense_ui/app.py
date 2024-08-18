from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Replace these with actual microservice endpoints
STOCK_DATA_SERVICE_URL = "http://stock-data-service:5001/api/stock-data"
PREDICTION_SERVICE_URL = "http://prediction-service:5002/api/predict"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    symbol = request.form.get('symbol')
    response = requests.get(f"{STOCK_DATA_SERVICE_URL}?symbol={symbol}")
    return jsonify(response.json())

@app.route('/get_prediction', methods=['POST'])
def get_prediction():
    symbol = request.form.get('symbol')
    response = requests.get(f"{PREDICTION_SERVICE_URL}?symbol={symbol}")
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0')
