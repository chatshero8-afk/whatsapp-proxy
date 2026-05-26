from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/send-whatsapp', methods=['POST', 'OPTIONS'])
def send_whatsapp():
    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return resp
    data = request.get_json()
    resp = requests.post(
        f"{data['api_domain']}/send/text",
        headers={"token": data['token'], "Content-Type": "application/json"},
        json={"to": data['to'], "text": data['text']}
    )
    response = jsonify(resp.json())
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response, resp.status_code

if __name__ == '__main__':
    app.run()
