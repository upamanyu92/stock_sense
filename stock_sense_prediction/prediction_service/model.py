import joblib

class PredictionModel:
    def __init__(self, model_path='prediction_service/model.pkl'):
        self.model = joblib.load(model_path)

    def predict(self, features):
        return self.model.predict(features)
