# routes.py
from flask import Blueprint, request, jsonify
import json
from fauth import signup, login_user
from fconfig import verify_token
from models import User, Property
from extensions import db  # Import db if you need to reference it directly
from sqlalchemy import and_

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

@bp.route('/api/properties', methods=['GET'])
def get_properties():
    location = request.args.get('location')
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    property_type = request.args.get('property_type')
    min_bedrooms = request.args.get('min_bedrooms', type=int)

    query = Property.query  # Start query on properties table

    filters = []
    if location:
        filters.append(Property.location.ilike(f"%{location}%"))
    if min_price is not None:
        filters.append(Property.price >= min_price)
    if max_price is not None:
        filters.append(Property.price <= max_price)
    if property_type:
        filters.append(Property.property_type.ilike(property_type))
    if min_bedrooms is not None:
        filters.append(Property.bedrooms >= min_bedrooms)

    if filters:
        query = query.filter(and_(*filters))

    properties = query.all()

    properties_list = []
    for property in properties:
        properties_list.append({
            "id": property.id,
            "title": property.title,
            "price": property.price,
            "location": property.location,
            "bedrooms": property.bedrooms,
            "bathrooms": property.bathrooms,
            "property_type": property.property_type,
            "description": property.description,
            "image_url": property.image_url,
            "created_by": property.created_by,
            "source": property.source,
            "created_at": property.created_at
        })

    return jsonify(properties_list), 200