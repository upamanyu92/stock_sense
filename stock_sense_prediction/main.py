from flask import Flask, request, jsonify
from prediction_service.service import PredictionService

app = Flask(__name__)
prediction_service = PredictionService()


@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON data from the request
        data = request.json

        # Ensure data is not empty
        if not data or 'data' not in data:
            return jsonify({"error": "Invalid input data"}), 400

        # Make predictions
        predictions = prediction_service.predict(data['data'])

        # Return the predictions as a JSON response
        return jsonify({"predictions": predictions.tolist()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5011)
