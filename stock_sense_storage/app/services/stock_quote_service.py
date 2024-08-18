from app.models.stock_quote import StockQuote
from app.utils.database import db

class StockQuoteService:
    @staticmethod
    def get_all_stock_quotes():
        return [quote.to_dict() for quote in StockQuote.query.all()]

    @staticmethod
    def get_stock_quote(id):
        quote = StockQuote.query.get(id)
        return quote.to_dict() if quote else {}

    @staticmethod
    def create_stock_quote(data):
        quote = StockQuote(**data)
        db.session.add(quote)
        db.session.commit()
        return quote.to_dict()

    @staticmethod
    def update_stock_quote(id, data):
        quote = StockQuote.query.get(id)
        if not quote:
            return {}
        for key, value in data.items():
            setattr(quote, key, value)
        db.session.commit()
        return quote.to_dict()

    @staticmethod
    def delete_stock_quote(id):
        quote = StockQuote.query.get(id)
        if quote:
            db.session.delete(quote)
            db.session.commit()
        return {}
