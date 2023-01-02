# ===== Inits + Definitions =========================
from AudioInput import AudioConversion
from AudioInput import AudioAnalysis
import requests
import json
import jwt
import datetime

"""
This module is the middlelayer between the database and the AudioAnalysis. It requests the audio parameters from each job 
passed in by the user though the webapp. It converts the parameters into the appropriate type, checks the audio and
convert it to mp3 if needed and starts the Audio-Analysis. Finally it passes the analysed audio metadata on to the database.
 """

# Start the Main Logic
def start(jobId, apiUrl, SECRET_KEY):
    # Request Parameters for Audio-Input from Database
    jobParametersRequest = requests.post(apiUrl + "/api/database/getJobAttr",
                                         json={
                                             "jobId": jobId,
                                             "attributes": [
                                                 "videoStart",
                                                 "videoEnd",
                                                 "fps",
                                                 "gateThreshold",
                                                 "freqLow",
                                                 "freqMid",
                                                 "freqHigh",
                                                 "pulsePerc",
                                                 "sectionAmount"
                                             ]
                                         }
                                         )
    jobParameters = jobParametersRequest.json()["values"]

    # Get parameters from jobParameters and convert them to right type
    videoStart = int(jobParameters["videoStart"])
    videoEnd = int(jobParameters["videoEnd"])
    fps = int(jobParameters["fps"])
    gateThreshold = float(jobParameters["gateThreshold"])
    freqLow = float(jobParameters["freqLow"])
    freqMid = float(jobParameters["freqMid"])
    freqHigh = float(jobParameters["freqHigh"])
    pulsePerc = json.loads(jobParameters["pulsePerc"])
    sourcePath = "/app/meta/jobs/" + jobId + "/audio/audio.mp3"
    sampleRate = int(fps * 512)
    frameDuration = int(sampleRate / fps - (sampleRate / fps % 64))
    sectionAmount = int(jobParameters["sectionAmount"])
    duration = int(videoEnd - videoStart)
    showPlots = eval("False")

    # Check Audio and convert to mp3 if needed
    fileStatus = AudioConversion.conformAudiofile("/app/meta/jobs/" + jobId)

    if fileStatus == "fileFound":
        print("Audiofile found")

        # Starting Audio-Analysis
        A = AudioAnalysis.AudioAnalysis(
            sourcePath=sourcePath,
            duration=duration,
            sampleRate=sampleRate,
            start=videoStart,
            frameDuration=frameDuration,
            sectionAmount=sectionAmount,
            gateThreshold=gateThreshold,
            bassFactor=freqLow,
            midFactor=freqMid,
            trebleFactor=freqHigh,
            pulsePerc=pulsePerc,
            showPlots=showPlots
        )

        audioData = A.startAnalysis()

        if audioData:
            print("Audio analysis successful")

            requests.post(
                apiUrl + "/api/database/setJobAttr",
                headers={
                    "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
                },
                json={
                    "jobId": jobId,
                    "values": {
                        "pulseData": ", ".join(map(str, audioData["pulseData"])),
                        "songSections": ", ".join(map(str, audioData["songSections"]))
                    }
                }
            )
            requests.post(
                apiUrl + "/api/database/setJobAttr",
                headers={
                    "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
                },
                json={
                    "jobId": jobId,
                    "values": {"status": "audioInputFinished"}
                }
            )
            requests.post(
                apiUrl + "/api/synthesis/createImageSequence",
                headers={
                    "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
                },
                json={
                    "jobId": jobId
                }
            )
            return
        else:
            print("Audio analysis failed")

            requests.post(
                apiUrl + "/api/database/setJobAttr",
                headers={
                    "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
                },
                json={
                    "jobId": jobId,
                    "values": {"status": "audioInputFailed"}
                }
            )
            return
    else:
        print("No Audiofile found")

        requests.post(
            apiUrl + "/api/database/setJobAttr",
            headers={
                "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
            },
            json={
                "jobId": jobId,
                "values": {"status": "audioInputFailed"}
            }
        )
        return
