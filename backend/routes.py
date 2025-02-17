#application routes
from flask import Flask, request, jsonify
import json
import pyrebase
from fauth import signup, login
app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to Investr API!"
#sign up route
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

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
    email = data.get('email')
    password = data.get('password')

    # Basic validation
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        # Attempt to log in the user with Firebase Authentication
        user = login(email, password)
        # Optionally, handle session or token management here
        return jsonify({"message": "User logged in successfully", "user": user}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)