#firebase configuration
import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
from flask_jwt_extended import decode_token
from flask_jwt_extended.exceptions import JWTDecodeError
BASE_DIR = os.path.dirname("/Users/davidlawal/Desktop/Investr-/backend)") # Get the backend directory path
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "config", "serviceAccountKey.json")

# Load Firebase credentials
cred = credentials.Certificate("/Users/davidlawal/Desktop/Investr-/backend/config/serviceAccountKey.json")
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
