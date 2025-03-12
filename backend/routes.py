# routes.py
from flask import Blueprint, request, jsonify
import json
from fauth import signup, login_user
from fconfig import verify_token
from models import User, Property,Favorite
from extensions import db  # Import db if you need to reference it directly
from sqlalchemy import and_
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, JWTManager
from datetime import timedelta

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

        # Extract firebase_uid from Firebase response
        firebase_uid = user_data.get("localId")  # Firebase assigns a unique ID

        if not firebase_uid:
            return jsonify({"error": "Firebase registration failed, no UID received"}), 500

        # Check if user already exists in PostgreSQL
        existing_user = User.query.filter_by(firebase_uid=firebase_uid).first()

        if not existing_user:
            new_user = User(firebase_uid=firebase_uid, email=email)  # Explicitly set firebase_uid
            db.session.add(new_user)
            db.session.commit()  #  Ensure commit only happens after setting firebase_uid

        return jsonify({
            "message": "User registered successfully",
            "user": {"firebase_uid": firebase_uid, "email": email}
        }), 201

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
        print("DEBUG: user_data retrieved from Firebase:", user_data)  # Debugging

        if 'firebase_uid' not in user_data:
            return jsonify({"error": "firebase_uid missing from user data"}), 400

        user = User.query.filter_by(firebase_uid=user_data['firebase_uid']).first()
        if not user:
            return jsonify({"error": "User not found in database"}), 404

        access_token = create_access_token(identity=user.firebase_uid, expires_delta=timedelta(hours=1))
        return jsonify({
            "message": "User logged in successfully",
            "user": user_data,
            "access_token": access_token
        }), 200
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
    # Fetch multiple locations from query params - supports multi-select
    locations = request.args.getlist('location')  # Now supports multiple areas
    min_price = request.args.get('min_price', type=int)
    max_price = request.args.get('max_price', type=int)
    property_type = request.args.get('property_type')
    min_bedrooms = request.args.get('min_bedrooms', type=int)

    query = Property.query  # Start query on properties table

    filters = []
    if locations:
        filters.append(Property.location.in_(locations))  # Check if in selected areas

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

@bp.route('/api/favourites', methods=['POST'])
@jwt_required()  # Ensure user is logged in
def save_favourite():
    user_id = get_jwt_identity()  # Get the logged-in user's ID
    data = request.get_json()
    property_id = data.get('property_id')

    # Check if already saved
    existing_favourite = Favorite.query.filter_by(user_id=user_id, property_id=property_id).first()
    if existing_favourite:
        return jsonify({"message": "Property already saved"}), 400

    # Save new favourite
    new_favourite = Favorite(user_id=user_id, property_id=property_id)
    db.session.add(new_favourite)
    db.session.commit()

    return jsonify({"message": "Property saved!"}), 201

@bp.route('/api/favourites', methods=['GET'])
@jwt_required()
def get_favourites():
    user_id = get_jwt_identity()

    # Query all properties saved by the user
    saved_properties = db.session.query(Property).join(Favorite).filter(Favorite.user_id == user_id).all()

    properties_list = []
    for property in saved_properties:
        properties_list.append({
            "id": property.id,
            "title": property.title,
            "price": property.price,
            "location": property.location,
            "bedrooms": property.bedrooms,
            "bathrooms": property.bathrooms,
            "property_type": property.property_type,
            "description": property.description,
            "image_url": property.image_url
        })

    return jsonify(properties_list), 200
