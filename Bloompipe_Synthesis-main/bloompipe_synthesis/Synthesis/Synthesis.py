# ===== Inits + Definitions =========================
import requests
from Synthesis import PklCopier, BloomyDreams
import json
import jwt
import datetime
import os
import shutil
from distutils.dir_util import copy_tree

# ===== Methods =========================


# Start the Main Logic
def start(jobId, apiUrl, SECRET_KEY):
    appPath = "/app/"
    jobPath = "/app/meta/jobs/" + jobId

    jobTempFoldername = "temp_" + jobId
    jobTempPath = appPath + jobTempFoldername

    tempExist = os.path.exists(jobTempPath)
    if not tempExist:
        os.makedirs(jobTempPath)
        print("Job temp directory is created!")

    # Request Parameters for Synthesis from Database
    jobParametersRequest = requests.post(
        apiUrl + "/api/database/getJobAttr",
        json={
            "jobId": jobId,
            "attributes": [
                "style",
                "videoStart",
                "videoEnd",
                "pulseData",
                "songSections",
                "fps",
                "loopVideo",
                "visualizeSections",
                "sectionSimilarity",
                "pointAmount",
                "interpolationType",
                "pulseReact",
                "videoSmoothness",
                "motionRandomness",
                "truncation"
            ]
        }
    )

    jobParameters = jobParametersRequest.json()["values"]

    # Get Parameters from jobParameters and convert them to right type
    style = str(jobParameters["style"])
    pulseData = list(map(float, jobParameters["pulseData"].split(",")))
    songSections = list(map(float, jobParameters["songSections"].split(",")))
    fps = int(jobParameters["fps"])
    loopVideo = eval(jobParameters["loopVideo"].capitalize())
    visualizeSections = eval(jobParameters["visualizeSections"].capitalize())
    showPlots = eval("False")
    sectionSimilarity = float(jobParameters["sectionSimilarity"])
    pointAmount = int(jobParameters["pointAmount"])
    interpolationType = str(jobParameters["interpolationType"])
    pulseReact = float(jobParameters["pulseReact"])
    videoSmoothness = float(jobParameters["videoSmoothness"])
    motionRandomness = float(jobParameters["motionRandomness"])
    truncation = float(jobParameters["truncation"])

    # Downloading PKL file
    PklCopier.getStyle(style)

    # Create the generator object
    bloomyDreams = BloomyDreams(
        style=style,
        pulseAudio=pulseData,
        songSections=songSections,
        showPlots=showPlots,
        fps=fps
    )

    # Start the image generation
    synthesisStatus = bloomyDreams.hallucinate(
        outPath=jobTempPath,
        loopVideo=loopVideo,
        visualizeSections=visualizeSections,
        sectionSimilarity=sectionSimilarity,
        pointAmount=pointAmount,
        interpolationType=interpolationType,
        pulseReact=pulseReact,
        videoSmoothness=videoSmoothness,
        motionRandomness=motionRandomness,
        truncation=truncation,
    )

    # Copy cached files from job temp directory to the server
    print("Copying cached images to storage.bloompipe.de ...")
    jobTempTar = jobTempFoldername + ".tar"

    os.system("tar -cf " + jobTempTar + " -C " + appPath + " " + jobTempFoldername)
    os.system("cp " + jobTempTar + " " + jobPath)
    os.system("rm -f " + jobTempTar)

    # Starting video file creation
    if synthesisStatus == "synthesisSuccessful":
        print("Synthesis Successful")

        requests.post(
            apiUrl + "/api/database/setJobAttr",
            headers={
                "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
                },
            json={
                "jobId": jobId,
                "values": {"status": "synthesisFinished"}
            }
        )

        requests.post(
            apiUrl + "/api/postpro/createVideoFile",
            headers={
                "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
            },
            json={
                "jobId": jobId
            }
        )

        return
    # Stopping pipeline
    else:
        print("Synthesis Failed")

        requests.post(
            apiUrl + "/api/database/setJobAttr",
            headers={
                "access-token": jwt.encode({"user": "bloompipe"}, SECRET_KEY, algorithm="HS256")
            },
            json={
                "jobId": jobId,
                "values": {"status": "synthesisFailed"}
            }
        )

        return
