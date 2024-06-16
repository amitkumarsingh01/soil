# app.py (Python code for the Flask server)

from flask import Flask, render_template_string, request
import requests

# Initialize the Flask app
app = Flask(__name__)

# Define the IP address of the Raspberry Pi Pico
pico_ip = 'http://192.168.156.82'

# Define the template for the web page
template = """
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>LED Control</title>
  </head>
  <body>
    <h1>LED Control</h1>
    <form method="post">
      <button name="action" value="on">Turn LED On</button>
      <button name="action" value="off">Turn LED Off</button>
    </form>
  </body>
</html>
"""

# Define a route for the web page
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']
        if action == 'on':
            requests.get(f'{pico_ip}/on')
        elif action == 'off':
            requests.get(f'{pico_ip}/off')
    return render_template_string(template)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
