from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Setup logging
logging.basicConfig(level=logging.DEBUG)

sensor_data = []

@app.route('/', methods=['POST'])
def receive_data():
    data = request.get_json()
    app.logger.debug(f"Received data: {data}")
    if data:
        data['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')  # Add timestamp to data
        sensor_data.append(data)
        return jsonify({"status": "success", "data": data}), 201
    return jsonify({"status": "error"}), 400

@app.route('/', methods=['GET'])
def get_data():
    app.logger.debug(f"Sending data: {sensor_data}")
    return jsonify(sensor_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
