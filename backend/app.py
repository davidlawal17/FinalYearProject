from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Flask-Migrate
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

# Initialize extensions
db.init_app(app)
migrate = Migrate(app, db)  #  Initialize Flask-Migrate
jwt = JWTManager(app)

# Register Blueprints
from routes import bp
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
