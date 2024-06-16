from flask import Flask, render_template, Response, request
import requests

app = Flask(__name__)

# Replace with your ESP32-CAM IP
esp32_cam_url = "http://192.168.206.83/"

@app.route('/')
def index():
    return render_template('index.html')

def gen():
    while True:
        response = requests.get(esp32_cam_url, stream=True)
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + chunk + b'\r\n\r\n')
        else:
            break

@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/led', methods=['POST'])
def led():
    action = request.form.get('action')
    if action == 'on':
        # Replace with your ESP32-CAM LED control URL
        requests.get(f"{esp32_cam_url}/led?state=1")
    elif action == 'off':
        requests.get(f"{esp32_cam_url}/led?state=0")
    elif action == 'brightness_up':
        requests.get(f"{esp32_cam_url}/led?brightness=up")
    elif action == 'brightness_down':
        requests.get(f"{esp32_cam_url}/led?brightness=down")
    return ('', 204)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
