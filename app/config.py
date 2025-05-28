import firebase_admin
from firebase_admin import credentials

def init_firebase():
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)