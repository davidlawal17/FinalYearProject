import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

BASE_DIR = os.path.dirname("/Users/davidlawal/Desktop/Investr-/backend)") # Get the backend directory path
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "config", "serviceAccountKey.json")

# Load Firebase credentials
cred = credentials.Certificate("/Users/davidlawal/Desktop/Investr-/backend/config/serviceAccountKey.json")
firebase_admin.initialize_app(cred)

# Firestore reference
db = firestore.client()

def verify_token(token):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token  # Contains user data such as uid, email, etc.
    except Exception as e:
        print("Token verification failed:", e)
        return None

print("✅ Firebase Admin SDK initialized successfully!")
