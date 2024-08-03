# training_script.py

import yfinance as yf
import numpy as np
from keras import Sequential
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input


def download_stock_data(symbol, start='2010-01-01', end='2024-07-04'):
    """
    Downloads stock data for a given symbol within a specified date range.

    Parameters:
    symbol (str): The stock symbol to download data for.
    start (str): The start date for the data in the format 'YYYY-MM-DD'. Default is '2010-01-01'.
    end (str): The end date for the data in the format 'YYYY-MM-DD'. Default is '2024-07-04'.

    Returns:
    pandas.DataFrame: A DataFrame containing the stock data if available, otherwise None.
    """
    stock = yf.download(symbol, start=start, end=end, progress=False)
    if stock is None or stock.empty:
        return None
    return stock


def preprocess_data(data, time_step=100):
    """
    Generate function comment for preprocess_data function.

    Parameters:
    - data: Input data to be preprocessed.
    - time_step: Number of time steps to look back (default=100).

    Returns:
    - X: Array of input sequences.
    - y: Array of target values.
    - scaler: Scaler object used for preprocessing.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(data)
    X, y = [], []
    for i in range(time_step, len(scaled_data)):
        X.append(scaled_data[i - time_step:i])
        y.append(scaled_data[i, 3])  # 'Close' column is the target
    X, y = np.array(X), np.array(y)
    return X, y, scaler


def build_model(input_shape):
    """
    Builds and compiles a LSTM model based on the given input shape.

    Parameters:
        input_shape (tuple): The shape of the input data.

    Returns:
        tensorflow.keras.Model: Compiled LSTM model.
    """
    model = Sequential()
    model.add(Input(shape=input_shape))
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model


def train_model(symbol):
    """
    Train a model using stock data for the given symbol.

    Parameters:
        symbol (str): The stock symbol to train the model for.

    Returns:
        tuple: A tuple containing the trained model and the scaler used for preprocessing.
    """
    stock_data = download_stock_data(symbol)
    if stock_data is None:
        return None

    stock_data = stock_data[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    stock_data.dropna(inplace=True)

    X, y, scaler = preprocess_data(stock_data)

    model = build_model((X.shape[1], X.shape[2]))

    model.fit(X, y, epochs=50, batch_size=32, verbose=1)

    model.save('optimized_stock_prediction_model.h5')
    return model, scaler


if __name__ == "__main__":
    symbol = 'AAPL'
    train_model(symbol)
