from flask import Flask, render_template, request
import requests

app = Flask(__name__)

esp32_ip = "192.168.206.83"  # Replace with your ESP32's IP address

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/toggle_led', methods=['POST'])
def toggle_led():
    requests.get(f'http://{esp32_ip}/toggle-led')
    return 'OK'

@app.route('/increase_brightness', methods=['POST'])
def increase_brightness():
    requests.get(f'http://{esp32_ip}/increase-brightness')
    return 'OK'

@app.route('/decrease_brightness', methods=['POST'])
def decrease_brightness():
    requests.get(f'http://{esp32_ip}/decrease-brightness')
    return 'OK'

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
