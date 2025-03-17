#firebase authorisation
import json
from idlelib.autocomplete import TRY_A
from os import WCONTINUED

import pyrebase  #importing the required library

firebaseConfig = {"apiKey": "AIzaSyAD90JGwcbElvpmLnvLS6fXZFtNLc3WzG0",
  "authDomain": "investr-7839f.firebaseapp.com",
  "databaseURL": "https://investr-7839f-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "investr-7839f",
  "storageBucket": "investr-7839f.firebasestorage.app",
  "messagingSenderId": "923518426976",
  "appId": "1:923518426976:web:b8c7ec1ccc5e4f89068805",
  "measurementId": "G-MCCXQ2F2JY"}      #configuring firebase, these credentials were taken from the firebase project

#setting up firebase
firebase = pyrebase.initialize_app(firebaseConfig)

#This firebase config and the line above allows us to connect to our firebase project

#using the authentication part of firebase
auth=firebase.auth()

#Defining a create account function
def signup(email, password):
    email = email.strip()
    password = password.strip()

    if not email:
        raise ValueError("Email cannot be empty")
    if not password:
        raise ValueError("Password cannot be empty")

    try:
        user = auth.create_user_with_email_and_password(email, password)
        print(" DEBUG: Firebase Response:", user)  # Print full Firebase response

        #  Check the exact structure of Firebase response
        if 'localId' in user:
            firebase_uid = user['localId']  # Direct extraction if present at top-level
        elif 'user' in user and 'localId' in user['user']:
            firebase_uid = user['user']['localId']  # Extraction from nested structure
        else:
            print(" ERROR: Firebase response does not contain localId!")
            raise Exception("Firebase registration failed: No UID received")

        return {
            "firebase_uid": firebase_uid,
            "email": email
        }

    except Exception as e:
        print(" ERROR in signup():", str(e))  # Log the full error for debugging
        try:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            print(" Specific Firebase Error:", error)
            raise Exception(f"Registration unsuccessful: {error}")
        except Exception as parse_error:
            print(" Error parsing Firebase response:", str(parse_error))
            raise Exception("Registration failed due to an unexpected error, please ensure your email is valid and your password is at least 6 characters long")


def login_user(email, password):
    email = email.strip()
    password = password.strip()

    if not email:
        raise ValueError("Email cannot be empty")
    if not password:
        raise ValueError("Password cannot be empty")

    try:
        user = auth.sign_in_with_email_and_password(email, password)
        print("User logged in successfully!")

        # Extract firebase_uid from the Firebase response
        firebase_uid = auth.get_account_info(user['idToken'])['users'][0]['localId']

        return {
            "firebase_uid": firebase_uid,
            "email": email
        }

    except Exception as e:
        print(" Firebase Login Error:", str(e))  # Debugging full error

        try:
            error_json = e.args[1]
            error_response = json.loads(error_json)
            error_message = error_response['error']['message']

            #  Handle Specific Firebase Authentication Errors
            if error_message == "EMAIL_NOT_FOUND":
                raise Exception("No account found with this email.")
            elif error_message == "INVALID_PASSWORD":
                raise Exception("Incorrect password. Please try again.")
            elif error_message == "INVALID_LOGIN_CREDENTIALS":
                raise Exception("Invalid email or password. Please check your details.")
            elif error_message == "USER_DISABLED":
                raise Exception("This account has been disabled. Contact support.")
            elif error_message == "TOO_MANY_ATTEMPTS_TRY_LATER":
                raise Exception("Too many failed attempts. Try again later.")
            else:
                raise Exception(f"Login failed: {error_message}")

        except Exception as parse_error:
            print(" Error parsing Firebase response:", str(parse_error))
            raise Exception("Login failed, ensure your credentials are correct.")