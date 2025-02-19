# run this file to create your database

from app import app, db

with app.app_context():
    db.create_all()
    print("Database tables created!")
