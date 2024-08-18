import pandas as pd
from prediction_service.model import PredictionModel

class PredictionService:
    def __init__(self):
        self.model = PredictionModel()

    def preprocess(self, data):
        # Convert the input data to a DataFrame
        df = pd.DataFrame(data)

        # Convert 'date' column to datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Set the 'date' column as the DataFrame index
        df.set_index('date', inplace=True)

        # Fill missing values using forward-fill method
        df.fillna(method='ffill', inplace=True)

        # Drop any remaining rows with NaN values
        df.dropna(inplace=True)

        # Feature engineering (e.g., calculating moving averages)
        df['SMA_10'] = df['close'].rolling(window=10).mean()
        df['SMA_50'] = df['close'].rolling(window=50).mean()

        # Drop rows with NaN values after calculating moving averages
        df.dropna(inplace=True)

        # Normalize or scale the data
        scaled_features = self.scaler.fit_transform(df[['close', 'SMA_10', 'SMA_50']])
        df[['close', 'SMA_10', 'SMA_50']] = scaled_features

        return df

    def make_prediction(self, data):
        preprocessed_data = self.preprocess(data)
        predictions = self.model.predict(preprocessed_data)
        return predictions.tolist()
