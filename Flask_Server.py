from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from threading import Thread

app = Flask(__name__, static_folder="../website")
CORS(app)

latest_risk = {"risk": 0}

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/risk')
def get_risk():
    return jsonify(latest_risk)

def update_risk(risk):
    latest_risk["risk"] = risk

def run_flask():
    app.run(host="0.0.0.0", port=5000)

flask_thread = Thread(target=run_flask)
flask_thread.daemon = True
flask_thread.start()
