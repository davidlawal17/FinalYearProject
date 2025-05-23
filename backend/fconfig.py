#firebase configuration
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTDecodeError

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "config", "serviceAccountKey.json")

# Load Firebase credentials
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# Firestore reference
db = firestore.client()

def verify_token(token):
    try:
        decoded = decode_token(token)
        return decoded
    except JWTDecodeError as e:
        print("Token verification failed:", e)
        return None

print("Firebase Admin SDK initialized successfully!")
