#application routes
from flask import Flask, request, jsonify
import json
import pyrebase
from fauth import signup, login_user
from fconfig import verify_token

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to Investr API!"
#sign up route
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', "").strip()
    password = data.get('password', "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = signup(email, password)

        return jsonify({"message": "User registered successfully", "user": user}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', "").strip()
    password = data.get('password', "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user = login_user(email, password)
        return jsonify({"message": "User logged in successfully", "user": user}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/api/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401

    decoded = verify_token(token)
    if not decoded:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"message": "Access granted", "user": decoded}), 200


if __name__ == "__main__":
    app.run(debug=True)