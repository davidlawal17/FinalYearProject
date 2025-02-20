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
        print("User registered successfully!")
        return user
    except Exception as e:
        # Log full error response from Firebase
        print("Firebase Registration Error:", e)
        try:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            print("Specific Firebase Error:", error)  # e.g., EMAIL_EXISTS, WEAK_PASSWORD
            raise Exception(f"Registration unsuccessful: {error}")
        except:
            print(" Error parsing Firebase response")
            raise Exception("Registration failed due to an unexpected error")




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
        return user
    except Exception as e:
        # Log full error response from Firebase
        print("Firebase Login Error:", e)
        try:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']
            print("Specific Firebase Error:", error)  # This will print detailed error like EMAIL_NOT_FOUND or INVALID_PASSWORD
            raise Exception(f"Login unsuccessful: {error}")
        except:
            print("Error parsing Firebase response")
            raise Exception("Login failed due to an unexpected error")
