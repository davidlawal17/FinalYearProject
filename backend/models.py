# models py
from datetime import datetime
from extensions import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String, primary_key=True)  #  Keep as String
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Property(db.Model):
    __tablename__ = 'properties'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    property_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(255))
    created_by = db.Column(db.String, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    source = db.Column(db.String(20), default='user')

class Favorite(db.Model):
    __tablename__ = 'favourites'  #  Ensure this matches your actual table name

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.firebase_uid'), nullable=False)  #  Fix FK reference
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    saved_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())




class NewsArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text)
    source_url = db.Column(db.String(255), nullable=False)
    published_date = db.Column(db.DateTime, server_default=db.func.current_timestamp())
