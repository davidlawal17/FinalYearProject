# routes.py
from flask import Blueprint, request, jsonify, current_app
import json
from fauth import signup, login_user
from werkzeug.utils import secure_filename
from fconfig import verify_token
from models import User, Property,Favorite
from extensions import db  # Import db if you need to reference it directly
from sqlalchemy import and_
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, JWTManager
from datetime import timedelta
from utils import allowed_file
import os

UPLOAD_FOLDER = 'investr-frontend/public/images/properties'

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
        user_data = signup(email, password)  # Call Firebase signup
        print("DEBUG: Firebase user_data:", user_data)  # Log Firebase response

        firebase_uid = user_data.get("firebase_uid")
        if not firebase_uid:
            return jsonify({"error": "Firebase registration failed, no UID received"}), 500

        # Check if user already exists in PostgreSQL
        existing_user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if existing_user:
            return jsonify({"error": "User already exists in database"}), 400

        #  Save user to PostgreSQL
        new_user = User(firebase_uid=firebase_uid, email=email)
        db.session.add(new_user)
        db.session.commit()
        print(" User successfully saved to PostgreSQL!")

        return jsonify({
            "message": "User registered successfully",
            "user": {"firebase_uid": firebase_uid, "email": email}
        }), 201

    except Exception as e:
        print(" ERROR in /api/register:", str(e))  # Log the full error
        return jsonify({"error": str(e)}), 500  # Return error message



@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email', "").strip()
    password = data.get('password', "").strip()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    try:
        user_data = login_user(email, password)  # Calls Firebase authentication
        firebase_uid = user_data.get("firebase_uid")

        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if not user:
            return jsonify({"error": "User not found in database"}), 404

        # Generate JWT token for authentication
        access_token = create_access_token(identity=user.firebase_uid, expires_delta=timedelta(hours=1))

        return jsonify({
            "message": "User logged in successfully",
            "user": user_data,
            "access_token": access_token
        }), 200

    except Exception as e:
        print(" ERROR in /api/login:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 400  # Return specific error message

@bp.route('/api/properties', methods=['GET', 'POST'])
def properties_handler():
    if request.method == 'GET':
        return handle_get_properties()
    elif request.method == 'POST':
        return handle_post_property()
def handle_get_properties():
    try:
        locations = request.args.getlist('location')
        min_price = request.args.get('min_price', type=int)
        max_price = request.args.get('max_price', type=int)
        property_type = request.args.get('property_type')
        min_bedrooms = request.args.get('min_bedrooms', type=int)

        print(f"DEBUG: Searching properties with filters - Locations: {locations}, Min Price: {min_price}, Max Price: {max_price}, Type: {property_type}, Min Bedrooms: {min_bedrooms}")

        query = Property.query

        filters = []
        if locations:
            filters.append(Property.location.in_(locations))

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

        if not properties:
            print("DEBUG: No properties found matching filters.")
            return jsonify({"error": "No properties found"}), 404

        properties_list = [{
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
            "source": property.source
        } for property in properties]

        return jsonify(properties_list), 200
    except Exception as e:
        print(f" ERROR in /api/properties: {str(e)}")
        return jsonify({"error": "Failed to fetch properties", "details": str(e)}), 500


def handle_post_property():
    try:
        token = request.headers.get('Authorization', "").replace("Bearer ", "")
        user_data = verify_token(token)
        if not user_data:
            return jsonify({"error": "Unauthorized"}), 401

        user_id = user_data.get("uid")

        title = request.form.get('title')
        price = int(request.form.get('price', 0))
        location = request.form.get('location')
        bedrooms = int(request.form.get('bedrooms', 0))
        bathrooms = int(request.form.get('bathrooms', 0))
        property_type = request.form.get('property_type')
        description = request.form.get('description', '')

        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'properties', filename)
            image.save(image_path)
            image_url = f"/images/properties/{filename}"
        else:
            image_url = "/images/properties/defaultprop.jpg"

        new_property = Property(
            title=title,
            price=price,
            location=location,
            bedrooms=bedrooms,
            bathrooms=bathrooms,
            property_type=property_type,
            description=description,
            image_url=image_url,
            created_by=user_id,
            source='user'
        )

        db.session.add(new_property)
        db.session.commit()

        return jsonify({"message": "Property added successfully"}), 201

    except Exception as e:
        print("Error in add_property:", str(e))
        return jsonify({"error": "Failed to add property"}), 500


@bp.route('/api/favourites', methods=['GET'])
@jwt_required()
def get_favourites():
    try:
        user_id = get_jwt_identity()
        print(f"DEBUG: Fetching favourites for user {user_id}")

        favourites = (
            db.session.query(Property)
            .join(Favorite, Favorite.property_id == Property.id)
            .filter(Favorite.user_id == user_id)
            .all()
        )

        if not favourites:
            print("DEBUG: No saved properties found for user.")
            return jsonify([]), 200

        properties_list = [{
            "id": property.id,
            "title": property.title,
            "price": property.price,
            "location": property.location,
            "bedrooms": property.bedrooms,
            "bathrooms": property.bathrooms,
            "property_type": property.property_type,
            "description": property.description,
            "image_url": property.image_url
        } for property in favourites]

        print(f" DEBUG: Retrieved {len(properties_list)} saved properties")
        return jsonify(properties_list), 200

    except Exception as e:
        print(f" ERROR in /api/favourites: {str(e)}")
        return jsonify({"error": "Failed to fetch saved properties", "details": str(e)}), 500



@bp.route('/api/protected', methods=['GET'])
def protected():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"error": "No token provided"}), 401
    decoded = verify_token(token)
    if not decoded:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"message": "Access granted", "user": decoded}), 200


@bp.route('/api/favourites', methods=['POST'])
@jwt_required()
def save_favourite():
    try:
        token = request.headers.get('Authorization')
        print(f"DEBUG: Received Authorization Header: {token}")  #  Log token

        user_id = get_jwt_identity()
        print(f"DEBUG: Extracted user_id from token: {user_id}")  #  Log extracted user ID

        data = request.get_json()
        print(f"DEBUG: Received request data: {data}")  #  Log request body

        property_id = data.get('property_id')

        if not property_id:
            print(" ERROR: Property ID is missing from request.")
            return jsonify({"error": "Property ID is required"}), 400  #  Return clear error message

        existing_favourite = Favorite.query.filter_by(user_id=user_id, property_id=property_id).first()
        if existing_favourite:
            print("️ Property already saved for this user.")
            return jsonify({"error": "Property already saved"}), 400

        new_favourite = Favorite(user_id=user_id, property_id=property_id)
        db.session.add(new_favourite)
        db.session.commit()

        print(" Property successfully saved!")
        return jsonify({"message": "Property saved successfully!"}), 201

    except Exception as e:
        print(" ERROR in /api/favourites:", str(e))
        return jsonify({"error": "Failed to save property", "details": str(e)}), 500


@bp.route('/api/favourites', methods=['DELETE'])
@jwt_required()
def remove_favourite():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        property_id = data.get('property_id')

        if not property_id:
            print(" ERROR: Property ID is missing from request.")
            return jsonify({"error": "Property ID is required"}), 400

        # Check if the property is saved
        favourite = Favorite.query.filter_by(user_id=user_id, property_id=property_id).first()
        if not favourite:
            print(" ERROR: Property not found in favourites.")
            return jsonify({"error": "Property not found in favourites"}), 404

        # Remove property from favourites
        db.session.delete(favourite)
        db.session.commit()

        print(f" Property {property_id} removed from favourites for user {user_id}")
        return jsonify({"message": "Property removed from favourites"}), 200

    except Exception as e:
        print(" ERROR in /api/favourites (DELETE):", str(e))
        return jsonify({"error": "Failed to remove property", "details": str(e)}), 500



