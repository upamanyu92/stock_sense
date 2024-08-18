from app.utils.database import db

class Prediction(db.Model):
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, nullable=False)
