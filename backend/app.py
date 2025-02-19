import os
from flask import Flask
from dotenv import load_dotenv
from extensions import db  # Import the centralized db instance

load_dotenv()

app = Flask(__name__)

db_url = os.environ['DATABASE_URL']
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the centralized SQLAlchemy instance with your app
db.init_app(app)
print("Using database URL:", os.environ.get('DATABASE_URL'))

# Import and register blueprints after the app and db are set up
from routes import bp
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
