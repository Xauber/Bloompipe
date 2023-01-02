# ===== Inits + Definitions =========================
from Synthesis import BloomyDreams
from testAudioInput import AudioAnalysis

# ===== Global-Variables =========================
duration = 606
start = 0
fps = 25
pointAmount = 30
sectionAmount = 3
sectionSimilarity = 1.0
gateThreshold = 0.2
sampleRate = fps * 512
bassFactor = 1.0
midFactor = 1.0
trebleFactor = 1.0
interpolationType = "nearest"
truncation = 0.5
motionRandomness = 0.9
pulseReact = 1.0
videoSmoothness = 0.7
pulsePerc = True
visualizeSections = True
showPlotsAudio = True
showPlotsSynthesis = True
loopVideo = True
frameDuration = int(sampleRate / fps - (sampleRate / fps % 64))

STYLE = "3d.pkl"
OUT = "../../Bloompipe_Test/sequence"
SOURCE = "../../Bloompipe_Test/audio/everybody.wav"

# ===== Methods ==================================
A = AudioAnalysis(
    sourcePath=SOURCE,
    duration=duration,
    sampleRate=sampleRate,
    sectionAmount=sectionAmount,
    gateThreshold=gateThreshold,
    bassFactor=bassFactor,
    midFactor=midFactor,
    trebleFactor=trebleFactor,
    start=start,
    frameDuration=frameDuration,
    pulsePerc=pulsePerc,
    showPlots=showPlotsAudio
)

audio_data = A.startAnalysis()

# Create the generator object
bloomyDreams = BloomyDreams(
    style=STYLE,
    pulseAudio=audio_data["pulseData"],
    songSections=audio_data["songSections"],
    showPlots=showPlotsSynthesis,
    fps=fps
)

# Start the synchronization and image generation
bloomyDreams.hallucinate(
    outPath=OUT,
    loopVideo=loopVideo,
    pointAmount=pointAmount,
    interpolationType=interpolationType,
    visualizeSections=visualizeSections,
    sectionSimilarity=sectionSimilarity,
    truncation=truncation,
    pulseReact=pulseReact,
    videoSmoothness=videoSmoothness,
    motionRandomness=motionRandomness
)
