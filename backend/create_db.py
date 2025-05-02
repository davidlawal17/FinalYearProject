# run this file to create database

from app import app, db

with app.app_context():
    db.create_all()
    print("Database tables created!")
