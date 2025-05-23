import os
import json
import pyrebase
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Firebase config loaded securely from environment
firebaseConfig = {
    "apiKey": os.getenv("REACT_APP_FIREBASE_API_KEY"),
    "authDomain": os.getenv("REACT_APP_FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("REACT_APP_FIREBASE_DATABASE_URL"),
    "projectId": os.getenv("REACT_APP_FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("REACT_APP_FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("REACT_APP_FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("REACT_APP_FIREBASE_APP_ID"),
    "measurementId": os.getenv("REACT_APP_FIREBASE_MEASUREMENT_ID")
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

def signup(email, password):
    email = email.strip()
    password = password.strip()

    if not email or not password:
        raise ValueError("Email and password cannot be empty")

    try:
        user = auth.create_user_with_email_and_password(email, password)
        firebase_uid = auth.get_account_info(user['idToken'])['users'][0]['localId']
        return {
            "firebase_uid": firebase_uid,
            "email": email
        }
    except Exception as e:
        print("Signup error:", str(e))
        raise Exception("Registration failed. Check your email and password.")

def login_user(email, password):
    email = email.strip()
    password = password.strip()

    if not email or not password:
        raise ValueError("Email and password cannot be empty")

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        firebase_uid = auth.get_account_info(user['idToken'])['users'][0]['localId']
        return {
            "firebase_uid": firebase_uid,
            "email": email
        }
    except Exception as e:
        print("Login error:", str(e))
        raise Exception("Login failed. Invalid email or password.")
