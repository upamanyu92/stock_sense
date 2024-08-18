from flask import Blueprint, jsonify

health_check_bp = Blueprint('health_check', __name__)

@health_check_bp.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'})
