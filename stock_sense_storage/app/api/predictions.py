from flask import Blueprint, request, jsonify
from app.services.prediction_service import PredictionService

predictions_bp = Blueprint('predictions', __name__)

@predictions_bp.route('/', methods=['GET'])
def get_all_predictions():
    return jsonify(PredictionService.get_all_predictions())

@predictions_bp.route('/<int:id>', methods=['GET'])
def get_prediction(id):
    return jsonify(PredictionService.get_prediction(id))

@predictions_bp.route('/', methods=['POST'])
def create_prediction():
    data = request.json
    return jsonify(PredictionService.create_prediction(data))

@predictions_bp.route('/<int:id>', methods=['PUT'])
def update_prediction(id):
    data = request.json
    return jsonify(PredictionService.update_prediction(id, data))

@predictions_bp.route('/<int:id>', methods=['DELETE'])
def delete_prediction(id):
    return jsonify(PredictionService.delete_prediction(id))
