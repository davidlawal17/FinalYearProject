#app.py
from flask import Flask,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os
from dotenv import load_dotenv
from extensions import db
from flask_cors import CORS

# Load environment variables
load_dotenv()
app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')
jwt = JWTManager(app)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Configure the database
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise extensions
db.init_app(app)
migrate = Migrate(app, db)  #  Initialise Flask-Migrate
jwt = JWTManager(app)

# Register Blueprints
from routes import bp
app.register_blueprint(bp)

# backend/app.py

#This block of code allows files to be uploaded to app.py for the property listings
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'investr-frontend', 'public', 'images')
os.makedirs(os.path.join(UPLOAD_FOLDER, 'properties'), exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Max 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('../investr-frontend/public/images/properties', filename)

@app.route('/images/properties/<filename>')
def serve_uploaded_image(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], 'properties'), filename)


if __name__ == "__main__":
    app.run(debug=True)
