from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route('/send-whatsapp', methods=['POST'])
def send_whatsapp():
    data = request.get_json()
    resp = requests.post(
        f"{data['api_domain']}/send/text",
        headers={"token": data['token'], "Content-Type": "application/json"},
        json={"to": data['to'], "text": data['text']}
    )
    return jsonify(resp.json()), resp.status_code

if __name__ == '__main__':
    app.run()
