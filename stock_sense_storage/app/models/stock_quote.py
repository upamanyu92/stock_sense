from app.utils.database import db

class StockQuote(db.Model):
    __tablename__ = 'stock_quotes'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
