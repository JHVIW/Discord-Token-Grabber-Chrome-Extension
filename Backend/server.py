from flask import Flask, request, jsonify
from flask_cors import CORS
from src.discord_functions import process_user_data

app = Flask(__name__)
CORS(app)

@app.route('/token', methods=['POST'])
def receive_token():
    data = request.json
    token = data.get('token')
    if token:
        print(f"Received token: {token}")
        
        user_data, status_code = process_user_data(token)
        if user_data is not None:
            print(user_data)
            return jsonify(user_data), status_code
        else:
            return jsonify({"message": "Invalid token"}), status_code
    else:
        return jsonify({"message": "No token provided"}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
