# ===== Inits + Definitions =========================
import json
import requests
import Synthesis
from threading import Thread
from flask import Flask, request, jsonify
import torch
import os
import time
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

# JWT-Key for Access 
SECRET_KEY = ""
with open("/app/meta/auth_key.txt", "r") as file:
    contents = file.read()
    SECRET_KEY = contents.split('\n', 1)[0]

# Open IP-Config file
with open("/app/meta/env", "r") as file:
    contents = file.read()
    ENV_MODE = contents.split('\n', 1)[0]

if(ENV_MODE == "dev"):
    apiUrl = "https://dev.bloompipe.de"
elif (ENV_MODE == "prod"):
    apiUrl = "https://bloompipe.de"

# Check if GPU is available
isGpu = torch.cuda.is_available()
print("GPU available: " + str(isGpu))




# ===== Methods =========================
# Method for checking if a token is valid
# Method based on: https://www.geeksforgeeks.org/using-jwt-for-user-authentication-in-flask/
def token_required(f):  
    @wraps(f)  
    def decorator(*args, **kwargs):
    
        token = None 

        if "access-token" in request.headers:  
            token = request.headers["access-token"]

        if not token:  
            return jsonify({"message": "A valid token is missing"}), 401   

        try:
            jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            return f(*args,  **kwargs)
        except:  
            return jsonify({"message": "Token is invalid"}), 401  

    return decorator 



def startThread(jobId):

    # Start Synthesis Process in Background
        thread = Thread(
            target=Synthesis.start, args=(
                jobId,
                apiUrl,
                SECRET_KEY,
            )
        )
        thread.daemon = True
        thread.start()



def getGpuServer():
    gpu_server_request = requests.post(
        apiUrl + "/api/serviceagent/getActiveGpu",
        headers = {"access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")},
        )
    gpu_server_request = gpu_server_request.json()

    gpu_found = gpu_server_request["gpuFound"]

    if gpu_found == "True":
        return gpu_server_request["gpuIp"]
    else:
        return "0"



# ===== Routes =========================
@app.route("/api/synthesis/createImageSequence", methods=["POST"])
@token_required
def C():
    with app.app_context():

        # Fetching jobId
        jobId = request.json["jobId"]

        # Determine if current system has GPU
        if isGpu:
            print("GPU found - Starting Synthesis with GPU...")
            startThread(jobId)

        else:
            print("No GPU available on this Server - Searching for one...")
            gpuIp = getGpuServer()

            if gpuIp != "0":
                print("GPU found - Starting Synthesis there...")

                requests.post(
                    "http://" + gpuIp + ":64/api/synthesis/createImageSequence",
                    headers = {"access-token" : jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")},
                    json = {
                        "jobId": jobId
                    }
                )

            else:
                print("No GPU found - Starting Synthesis with CPU...")
                startThread(jobId)
        
        # Return Stage
        requests.post(
            apiUrl + "/api/database/setJobAttr",
            headers = {"access-token" : jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")},
            json = {
                "jobId": jobId,
                "values": {"status": "synthesisRunning"}
            }
        )
        return {
            "status": "synthesisRunning"
        }



# ===== App Footer Statements =========================
if __name__ == "__main__":
    app.run(debug=True)
