# routes.py
from flask import Blueprint, request, jsonify, current_app
import json
from fauth import signup, login_user
from werkzeug.utils import secure_filename
from fconfig import verify_token
from models import User, Property,Favorite
from extensions import db  # Import db if you need to reference it directly
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, JWTManager
from datetime import timedelta
from utils import allowed_file
import pandas as pd
import numpy as np
import math

from recomendation import predict_recommendation, FEATURES, model
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

        #  Check if user exists in PostgreSQL; if not, create one
        user = User.query.filter_by(firebase_uid=firebase_uid).first()
        if not user:
            print(f"User not found in DB. Creating new entry for {firebase_uid}")
            user = User(firebase_uid=firebase_uid, email=email)
            db.session.add(user)
            db.session.commit()

        #  Generate JWT token for authentication
        access_token = create_access_token(identity=user.firebase_uid, expires_delta=timedelta(hours=1))

        return jsonify({
            "message": "User logged in successfully",
            "user": user_data,
            "access_token": access_token
        }), 200

    except Exception as e:
        print("ERROR in /api/login:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 400


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


@jwt_required()  # Add this decorator
def handle_post_property():
    try:
        current_user = get_jwt_identity()  # Now this will work
        if not current_user:
            print("ERROR: No user identity in JWT")
            return jsonify({"error": "Unauthorized - invalid token"}), 401

        print(f"DEBUG: Creating property for user: {current_user}")

        # Validate required form data
        required_fields = ['title', 'price', 'location', 'property_type']
        missing_fields = [field for field in required_fields if not request.form.get(field)]

        if missing_fields:
            print(f"ERROR: Missing required fields: {missing_fields}")
            return jsonify({
                "error": "Missing required fields",
                "missing": missing_fields
            }), 400

        # Parse form data
        form_data = {
            'title': request.form.get('title').strip(),
            'price': int(request.form.get('price', 0)),
            'location': request.form.get('location').strip(),
            'bedrooms': int(request.form.get('bedrooms', 0)),
            'bathrooms': int(request.form.get('bathrooms', 0)),
            'property_type': request.form.get('property_type').strip(),
            'description': request.form.get('description', '').strip(),
        }

        # Validate price is positive
        if form_data['price'] <= 0:
            print("ERROR: Invalid price value")
            return jsonify({"error": "Price must be greater than 0"}), 400

        # Handle image upload
        image = request.files.get('image')
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            try:
                image_path = os.path.join(
                    current_app.config['UPLOAD_FOLDER'],
                    'properties',
                    filename
                )
                image.save(image_path)
                image_url = f"/images/properties/{filename}"
                print(f"DEBUG: Image saved at {image_path}")
            except Exception as e:
                print(f"ERROR saving image: {str(e)}")
                image_url = "/images/properties/defaultprop.jpg"
        else:
            image_url = "/images/properties/defaultprop.jpg"
            print("DEBUG: Using default property image")

        # Create new property
        new_property = Property(
            title=form_data['title'],
            price=form_data['price'],
            location=form_data['location'],
            bedrooms=form_data['bedrooms'],
            bathrooms=form_data['bathrooms'],
            property_type=form_data['property_type'],
            description=form_data['description'],
            image_url=image_url,
            created_by=current_user,
            source='user'
        )

        db.session.add(new_property)
        db.session.commit()

        print(f"DEBUG: Property created successfully. ID: {new_property.id}")
        print(f"DEBUG: Property created_by: {new_property.created_by}")

        return jsonify({
            "message": "Property added successfully",
            "property_id": new_property.id,
            "created_by": new_property.created_by
        }), 201

    except ValueError as e:
        print(f"ERROR: Invalid numeric value - {str(e)}")
        return jsonify({
            "error": "Invalid numeric value",
            "details": str(e)
        }), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"DATABASE ERROR: {str(e)}")
        return jsonify({
            "error": "Database operation failed",
            "details": str(e)
        }), 500

    except Exception as e:
        print(f"UNEXPECTED ERROR: {str(e)}")
        return jsonify({
            "error": "Failed to add property",
            "details": str(e)
        }), 500

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

@bp.route('/api/properties/<int:property_id>', methods=['DELETE'])
@jwt_required()
def delete_property(property_id):
    try:
        user_id = get_jwt_identity()  # This gives us the Firebase UID

        property_to_delete = Property.query.get(property_id)

        if not property_to_delete:
            return jsonify({"error": "Property not found"}), 404

        # Check if the current user is the creator
        if property_to_delete.created_by != user_id:
            return jsonify({"error": "You do not have permission to delete this property"}), 403

        db.session.delete(property_to_delete)
        db.session.commit()

        return jsonify({"message": "Property deleted successfully"}), 200

    except Exception as e:
        print("Error in delete_property:", str(e))
        return jsonify({"error": "Failed to delete property"}), 500


@bp.route('/api/properties/<int:property_id>/check-ownership', methods=['GET'])
@jwt_required()
def check_ownership(property_id):
    user_id = get_jwt_identity()
    property = Property.query.get(property_id)

    if not property:
        return jsonify({"error": "Property not found"}), 404

    return jsonify({
        "property_created_by": property.created_by,
        "current_user": user_id,
        "is_owner": property.created_by == user_id
    }), 200

@bp.route('/api/properties/<int:property_id>', methods=['DELETE'])
@jwt_required()
def delete_property_by_id(property_id):
    try:
        user_id = get_jwt_identity()
        property = Property.query.get(property_id)

        if not property:
            return jsonify({"error": "Property not found"}), 404

        if property.created_by != user_id:
            return jsonify({"error": "Unauthorized – You do not own this property"}), 403

        db.session.delete(property)
        db.session.commit()

        return jsonify({"message": "Property deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"ERROR deleting property: {str(e)}")
        return jsonify({
            "error": "Failed to delete property",
            "details": str(e)
        }), 500


REGION_MAP = {
    'N': 'North', 'NW': 'North',
    'E': 'East',
    'SE': 'South', 'SW': 'South', 'S': 'South',
    'W': 'West',
    'WC': 'Central', 'EC': 'Central'
}

def extract_region_from_title(title):
    import re
    match = re.search(r'([A-Z]{1,2})\d{1,2}[A-Z]?', title.strip().split(',')[-1].strip())
    prefix = match.group(1) if match else 'UNK'
    return REGION_MAP.get(prefix, 'Other')

@bp.route('/api/recommend', methods=['POST'])
def recommend():
    try:
        data = request.get_json()

        # Extract raw inputs
        price = float(data.get("price"))
        bedrooms = int(data.get("bedrooms", 1))
        bathrooms = int(data.get("bathrooms", 1))
        sqft = float(data.get("sizeSqFeetMax", 600))
        property_type = data.get("property_type", "Other")
        region = data.get("region", "Other")

        # Derived features
        price_per_bedroom = price / bedrooms
        price_per_sqft = price / sqft
        estimated_rent = price * np.random.uniform(0.0035, 0.0065)
        rent_to_price_ratio = (estimated_rent * 12) / price * 100
        bedrooms_per_100k = bedrooms / (price / 100_000)

        # Region score
        region_score_map = {
            "Central": 0.90,
            "East": 0.85,
            "South": 0.75,
            "West": 0.65,
            "North": 0.60,
            "Other": 0.50
        }
        region_score = region_score_map.get(region, 0.50)

        # Simulated growth and ROI
        growth_rate = np.random.uniform(0.02, 0.06)
        roi = rent_to_price_ratio + (growth_rate * 100)

        # 5-year projections
        price_projection = [round(price * ((1 + growth_rate) ** i)) for i in range(6)]
        benchmark_growth_map = {
            "Central": 0.035, "North": 0.030, "South": 0.035,
            "East": 0.040, "West": 0.030, "Other": 0.035
        }
        benchmark_growth = benchmark_growth_map.get(region, 0.035)
        benchmark_projection = [round(price * ((1 + benchmark_growth) ** i)) for i in range(6)]

        # Build feature dict (match model exactly)
        features = {
            "price": price,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sizeSqFeetMax": sqft,
            "price_per_bedroom": price_per_bedroom,
            "price_per_sqft": price_per_sqft,
            "estimated_rent": estimated_rent,
            "rent_to_price_ratio": rent_to_price_ratio,
            "bedrooms_per_100k": bedrooms_per_100k,
            "region_score": region_score
        }

        # One-hot encoding for region
        for r in ["Central", "East", "North", "Other", "South", "West"]:
            features[f"region_{r}"] = 1 if region == r else 0

        # One-hot encoding for property type
        for pt in ["Detached", "Flat", "House", "Other", "Semi_Detached", "Terraced"]:
            features[f"propertyType_{pt}"] = 1 if property_type == pt else 0

        # Ensure missing features are included as 0

        for f in FEATURES:
            features.setdefault(f, 0)

        # Predict
        result = predict_recommendation(features)

        return jsonify({
            **result,
            "roi": round(roi, 2),
            "growth_rate": round(growth_rate * 100, 2),
            "estimated_rent": round(estimated_rent, 2),
            "price_projection": price_projection,
            "benchmark_projection": benchmark_projection,
            "benchmark_growth": round(benchmark_growth * 100, 2)
        })

    except Exception as e:
        print("Error in recommendation route:", e)
        return jsonify({"error": str(e)}), 500
