from flask import Blueprint, request, jsonify
from app.services.stock_quote_service import StockQuoteService

stock_quotes_bp = Blueprint('stock_quotes', __name__)

@stock_quotes_bp.route('/', methods=['GET'])
def get_all_stock_quotes():
    return jsonify(StockQuoteService.get_all_stock_quotes())

@stock_quotes_bp.route('/<int:id>', methods=['GET'])
def get_stock_quote(id):
    return jsonify(StockQuoteService.get_stock_quote(id))

@stock_quotes_bp.route('/', methods=['POST'])
def create_stock_quote():
    data = request.json
    return jsonify(StockQuoteService.create_stock_quote(data))

@stock_quotes_bp.route('/<int:id>', methods=['PUT'])
def update_stock_quote(id):
    data = request.json
    return jsonify(StockQuoteService.update_stock_quote(id, data))

@stock_quotes_bp.route('/<int:id>', methods=['DELETE'])
def delete_stock_quote(id):
    return jsonify(StockQuoteService.delete_stock_quote(id))
