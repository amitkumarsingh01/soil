from flask import Flask, request, render_template, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'audio.db'

# Initialize database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS recordings (id INTEGER PRIMARY KEY, audio BLOB)''')
    conn.commit()
    conn.close()

# Save audio to database
def save_audio(audio_data):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO recordings (audio) VALUES (?)', (sqlite3.Binary(audio_data),))
    conn.commit()
    conn.close()

# Retrieve last audio recording
def get_last_audio():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT audio FROM recordings ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_recording():
    return jsonify(success=True)

@app.route('/stop', methods=['POST'])
def stop_recording():
    audio_data = request.files['audio'].read()
    save_audio(audio_data)
    return jsonify(success=True)

@app.route('/play', methods=['POST'])
def play_audio():
    audio_data = get_last_audio()
    return audio_data if audio_data else '', 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
