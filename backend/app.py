import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from extensions import db

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Load Database URL
db_url = os.getenv('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# 🔹 Load JWT secret key & algorithm
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Ensure secret key is set
app.config['JWT_ALGORITHM'] = 'HS256'  # Explicitly setting the algorithm
app.config['JWT_DECODE_ALGORITHMS'] = ['HS256']  # Ensures only HS256 is used

jwt = JWTManager(app)  # Initialize JWT

# Register Blueprints
from routes import bp
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
