from app.models.prediction import Prediction
from app.utils.database import db

class PredictionService:
    @staticmethod
    def get_all_predictions():
        return [prediction.to_dict() for prediction in Prediction.query.all()]

    @staticmethod
    def get_prediction(id):
        prediction = Prediction.query.get(id)
        return prediction.to_dict() if prediction else {}

    @staticmethod
    def create_prediction(data):
        prediction = Prediction(**data)
        db.session.add(prediction)
        db.session.commit()
        return prediction.to_dict()

    @staticmethod
    def update_prediction(id, data):
        prediction = Prediction.query.get(id)
        if not prediction:
            return {}
        for key, value in data.items():
            setattr(prediction, key, value)
        db.session.commit()
        return prediction.to_dict()

    @staticmethod
    def delete_prediction(id):
        prediction = Prediction.query.get(id)
        if prediction:
            db.session.delete(prediction)
            db.session.commit()
        return {}
