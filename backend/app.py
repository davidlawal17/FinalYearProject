from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from extensions import db  # Assuming you're using SQLAlchemy

load_dotenv()

app = Flask(__name__)

# CORS Configuration to allow requests from React app running on localhost:3000
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Database Configuration
import os
db_url = os.environ['DATABASE_URL']
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Import and register blueprints
from routes import bp
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
