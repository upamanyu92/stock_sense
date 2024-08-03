import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from keras.src.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional
from keras.src.callbacks import EarlyStopping
from bsedata.bse import BSE
import sqlite3
from datetime import datetime
from flask import Flask, jsonify, render_template

app = Flask(__name__)


# Database connection
def get_db_connection():
    conn = sqlite3.connect('predicted_prices.db')
    conn.row_factory = sqlite3.Row
    return conn


def create_features(data):
    data['SMA_20'] = data['Close'].rolling(window=20).mean()
    data['SMA_50'] = data['Close'].rolling(window=50).mean()
    data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
    data['EMA_50'] = data['Close'].ewm(span=50, adjust=False).mean()
    data['Volume_Mean'] = data['Volume'].rolling(window=20).mean()
    data.dropna(inplace=True)
    return data

def predict_max_profit(symbol):
    stock = yf.download(symbol, start='2010-01-01', end='2023-07-16')
    stock = create_features(stock)
    data = stock[['Close', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'Volume_Mean']].values

    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)

    x_train, y_train = [], []
    for i in range(60, len(scaled_data)):
        x_train.append(scaled_data[i-60:i])
        y_train.append(scaled_data[i, 0])

    x_train, y_train = np.array(x_train), np.array(y_train)

    model = Sequential()
    model.add(Bidirectional(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], x_train.shape[2]))))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    model.add(Dense(1))

    model.compile(optimizer='adam', loss='mean_squared_error')
    early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
    model.fit(x_train, y_train, epochs=100, batch_size=32, verbose=2, callbacks=[early_stopping])

    last_60_days = stock[['Close', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'Volume_Mean']][-60:].values
    last_60_days_scaled = scaler.transform(last_60_days)
    x_test = [last_60_days_scaled]
    x_test = np.array(x_test)

    predicted_price = model.predict(x_test)
    predicted_price = scaler.inverse_transform(np.concatenate((predicted_price, np.zeros((1, data.shape[1] - 1))), axis=1))[:,0]

    return predicted_price[0]


@app.route('/trigger_prediction', methods=['POST'])
def trigger_prediction():
    b = BSE()
    b.updateScripCodes()
    mutual_funds = b.getScripCodes()
    conn = get_db_connection()
    c = conn.cursor()

    for code, name in mutual_funds.items():
        try:
            quote = b.getQuote(code)
            stock_symbol = quote.get('securityID')
            stock_symbol_yahoo = stock_symbol + '.BO'  # Assuming it's a BSE stock
            predicted_price = predict_max_profit(stock_symbol_yahoo)
            current_price = float(quote['currentValue'].replace(',', ''))  # Handle comma in numbers

            c.execute('''
                INSERT INTO predictions (company_name, security_id, current_price, predicted_price, prediction_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (quote.get('companyName'), stock_symbol, current_price, predicted_price,
                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()

        except Exception as e:
            print(f"An error occurred while fetching data for {stock_symbol}: {e}")

    conn.close()
    return jsonify({"message": "Prediction triggered and data stored in database"}), 200


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
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, port=5005)
