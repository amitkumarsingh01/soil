from flask import Flask, render_template, request
import requests

app = Flask(__name__)

ESP32_IP = 'http://192.168.145.248/'  # Replace with the actual IP address of your ESP32

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    direction = request.form.get('direction')
    requests.get(f"{ESP32_IP}/{direction}")
    return '', 204

@app.route('/speed', methods=['POST'])
def speed():
    action = request.form.get('action')
    requests.get(f"{ESP32_IP}/{action}")
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)