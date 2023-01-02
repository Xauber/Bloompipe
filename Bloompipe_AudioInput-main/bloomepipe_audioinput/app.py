# ===== Inits + Definitions =========================
import json
import requests
from AudioInput import AudioInput
from threading import Thread
from flask import Flask, request, jsonify
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# JWT-Key for Access 
SECRET_KEY = ""
with open("/app/meta/auth_key.txt", "r") as file:
    contents = file.read()
    SECRET_KEY = contents.split('\n', 1)[0]

with open("/app/meta/env", "r") as file:
    contents = file.read()
    ENV_MODE = contents.split('\n', 1)[0]

if(ENV_MODE == "dev"):
    apiUrl = "https://dev.bloompipe.de"
elif (ENV_MODE == "prod"):
    apiUrl = "https://bloompipe.de"



# ===== Methods =========================
# Method for checking if a token is valid
# Method based on: https://www.geeksforgeeks.org/using-jwt-for-user-authentication-in-flask/
def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):

        token = None

        if 'access-token' in request.headers:
            token = request.headers['access-token']

        if not token:
            return jsonify({'message': 'a valid token is missing'}), 401

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return f(*args, **kwargs)
        except:
            return jsonify({'message': 'token is invalid'}), 401

    return decorator


# ===== Routes =========================
@app.route("/api/audioinput/createAudioFile", methods=["POST"])
# @token_required  #Disbabled until new WebApp
def createAudioFile():
    with app.app_context():
        # Fetching jobId
        jobId = request.json["jobId"]

        # Start AudioInput Process in Background
        thread = Thread(
            target=AudioInput.start, args=(
                jobId,
                apiUrl,
                SECRET_KEY,
            )
        )
        thread.daemon = True
        thread.start()

        # Return Stage
        requests.post(
            apiUrl + "/api/database/setJobAttr",
            json={
                "jobId": jobId,
                "values": {"status": "audioInputRunning"}
            }
        )
        return {
            "status": "audioInputRunning"
        }


# ===== App Footer Statements =========================
if __name__ == "__main__":
    app.run(debug=True)
