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
def signup():
  while True:
    email = input("Enter your email: ").strip()                 #Checks whether the user typed their email
    if not email:
      print("Error: Email cannot be empty. Please try again.")
      continue

    password = input("Enter your password: ").strip()         #Check whether user has typed their password
    if not password:
      print("Error: Password cannot be empty. Please try again.")
      continue

    try:                #Tries to create an account
      user = auth.create_user_with_email_and_password(email, password)
      print("User created successfully!")
      return user
    except Exception as e:             #error handling
      error_json = e.args[1]           #Pyrebase includes error details in the second element of the string tuple, the line extracts that error
      error = json.loads(error_json)['error']['message']   #parse the JSOn string and retrieve/ assign the error message
      if error == "EMAIL_EXISTS":
        print("Error: The email address is already in use. Please use a different email.")
      elif error == "WEAK_PASSWORD":
        print("Error: The password is too weak. Please choose a stronger password.")
      elif error == "INVALID_EMAIL":
        print("Error: The email address is not valid. Please enter a valid email.")
      else:
        print(f"An unexpected error occurred: {error}")

    retry = input("Do you want to try again? (y/n): ").lower()
    if retry != 'y':
      print("Signup process cancelled.")
      break

def login():
  while True:
    email = input("Enter your email: ").strip()
    if not email:
      print("Please enter your email")
      continue

    password = input("Enter your password: ").strip()
    if not password:
      print("Please enter your password")
      continue

    try:
      user = auth.sign_in_with_email_and_password(email, password)
      print("User logged in successfully!")
      return user

    except Exception as e:
        try:
            error_json = e.args[1]
            error = json.loads(error_json)['error']['message']

            if error == "INVALID_EMAIL":
                print("Error: Invalid email address.")
            elif error == "INVALID_PASSWORD":
                print("Error: Incorrect password.")
            elif error == "EMAIL_NOT_FOUND":
                print("Error: No user found with that email.")
            else:
                print(f"Login unsuccessful. Please try again. (Error: {error})")
        except:
            print("Login unsuccessful. Please try again. (Unexpected error parsing response)")  #Fallback

    retry = input("Do you want to try again? (y/n): ").lower()
    if retry != 'y':
        print("Login process cancelled.")
        return None #Or some appropriate value



login()