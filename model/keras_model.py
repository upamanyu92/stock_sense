import logging

import numpy as np
import yfinance as yf
from keras.src.callbacks import EarlyStopping
from keras.src.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import Dense, LSTM, Dropout, Bidirectional

from features.FeatureFactory import create_features


def predict_max_profit(symbol):
    try:
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
    except Exception as e:
        logging.error(f"Error predicting for {symbol}: {e.__str__()}")
        raise e