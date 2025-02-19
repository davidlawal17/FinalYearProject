# routes.py
from flask import Blueprint, request, jsonify
import json
from fauth import signup, login_user
from fconfig import verify_token
from models import User
from extensions import db  # Import db if you need to reference it directly

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return "Welcome to Investr API!"

@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    try:
        user_data = signup(email, password)
        firebase_uid = user_data.get("localId")
        existing_user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if not existing_user:
            new_user = User(firebase_uid=firebase_uid, email=email)
            db.session.add(new_user)
            db.session.commit()
        return jsonify({"message": "User registered successfully", "user": user_data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', "").strip()
    password = data.get('password', "").strip()
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    try:
        user_data = login_user(email, password)
        return jsonify({"message": "User logged in successfully", "user": user_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@bp.route('/api/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401
    decoded = verify_token(token)
    if not decoded:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"message": "Access granted", "user": decoded}), 200
