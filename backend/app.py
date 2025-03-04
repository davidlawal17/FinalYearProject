from flask import Flask                         # Import Flask for creating the web application
from flask_cors import CORS                       # Import CORS to enable cross-origin requests
from dotenv import load_dotenv                    # Import load_dotenv to load environment variables from a .env file
from extensions import db                         # Import the centralized SQLAlchemy instance from extensions

load_dotenv()                                     # Load environment variables from the .env file

app = Flask(__name__)                             # Create the Flask application instance

CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})  # Enable CORS for requests from the React app at localhost:3000


# for the database
import os                                       # Import os module to work with environment variables
db_url = os.environ['DATABASE_URL']               # Retrieve the DATABASE_URL from the environment variables
if db_url.startswith("postgres://"):              # Check if the URL starts with "postgres://"
    db_url = db_url.replace("postgres://", "postgresql://", 1)  # Replace with "postgresql://" for SQLAlchemy compatibility
app.config['SQLALCHEMY_DATABASE_URI'] = db_url      # Set the SQLAlchemy Database URI in the app's config
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable modification tracking to save resources
db.init_app(app)                                  # Initialize the SQLAlchemy instance with the Flask app

API_KEY = os.environ.get('PROPERTYDATA_API_KEY')  #retrieves the API key from .env

# defining the URLS base URLs

from routes import bp                           # Import the blueprint that contains API route definitions
app.register_blueprint(bp)                        # Register the blueprint with the Flask application

if __name__ == "__main__":                        # Check if the script is run directly
    app.run(debug=True)                           # Run the Flask app in debug mode
