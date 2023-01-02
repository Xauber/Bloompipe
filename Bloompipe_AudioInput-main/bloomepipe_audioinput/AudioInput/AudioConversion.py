# ===== Inits + Definitions =========================
import os

"""
This module checks if the provided Audiofile is an MP3, otherwise if will convert the File into MP3 using ffmpeg. 
It can only conform wav files into mp3. 
"""

def conformAudiofile(jobPath):
    # Check if directory exists and abort if not
    if not (os.path.exists(jobPath + "/audio")):
        return "directoryNotFound"

    fileAudio = jobPath + "/audio/audio.wav"
    fileMP3 = jobPath + "/audio/audio.mp3"

    print("Check if Audiofile has to be converted")

    if os.path.exists(fileAudio):
        print("Conversion necessary")
        convertAudioToMP3(jobPath)
        return "fileFound"

    elif os.path.exists(fileMP3):
        print("No conversion necessary")
        return "fileFound"

    else:
        return "fileNotFound"


# Converts Audiofile to MP3
def convertAudioToMP3(jobPath):
    fileAudio = jobPath + "/audio/audio.wav"
    fileMP3 = jobPath + "/audio/audio.mp3"

    print("Start Conversion of " + fileAudio + " to " + fileMP3)
    os.system("ffmpeg -i " + fileAudio + " -vn -ar 44100 -ac 2 -b:a 192k " + fileMP3)
