import pyrebase
import json

with open('credential.json') as firebase_credential:
    data = json.load(firebase_credential)

config = data['config']

firebase = pyrebase.initialize_app(config)


def get_storage():
    return firebase.storage()
