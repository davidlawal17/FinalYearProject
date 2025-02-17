import firebase_admin
from firebase_admin import credentials, firestore, auth
import os

BASE_DIR = os.path.dirname("/Users/davidlawal/Desktop/Investr-/backend)") # Get the backend directory path
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, "config", "serviceAccountKey.json")

# Load Firebase credentials
cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
firebase_admin.initialize_app(cred)

# Firestore reference
db = firestore.client()

print("✅ Firebase Admin SDK initialized successfully!")
