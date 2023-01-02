# ===== Inits + Definitions =========================
import librosa
import numpy as np
import librosa.display
import matplotlib.pyplot as plt
import matplotlib.transforms as mpt


class AudioAnalysis:
    """
    AudioAnalysis is the main module in oder to process the uploaded audio. It
    splits the track into the harmonic and percussive components, analyzes each component for its fourier data,
    different sections, scales its frequency bands, gates its loudness, and normalizes the loudness.

    On the basis of the open source LucidSonicDreams Code: https://github.com/mikaelalafriz/lucid-sonic-dreams
    we pulled out the audio-analysis into a separate module in order to add functionality. Therefore,
    we refactored the unclear & unstructured audio analysis of the LSD into different methods
    and expanded it by adding in the user dependent parameters:
    bassFactor, midFactor, trebleFactor, gateThreshold, sectionAmount.
    These parameters influence the audio analysis and in a later step have an impact onto the image generation.
    Therefore, we added the functionality of defining a particular amount of sections that
    divide the source audio into parts defined by characteristic spectral differences.
    Still for the FFT Analysis and the splitting of the audio into percussive and harmonic content
    we used librosa which is a python package for music and audio analysis.

    https://librosa.org/doc/latest/index.html
    """
    def __init__(
            self,
            sourcePath: str,
            duration: int,
            sampleRate: int,
            start: int,
            frameDuration: int,
            sectionAmount: int,
            gateThreshold: float = 0.0,
            bassFactor: float = 1.0,
            midFactor: float = 1.0,
            trebleFactor: float = 1.0,
            pulsePerc: bool = True,
            showPlots: bool = False,
    ):
        """
        The constructor of the AudioAnalysis class initializes all the class attributes
        and also sets some default values.
        Args:
            sourcePath: Path to the audio file
            duration: Length of the audio that should be analyzed
            sampleRate: How many samples per second should be analyzed
            start: At what second to start the analysis
            frameDuration: How long a frame of the corresponding video will last
            sectionAmount: How many song sections should be analyzed
            gateThreshold: How much of the audio should be let through
            bassFactor: How much the bass frequencies should be scaled
            midFactor: How much the middle frequencies should be scaled
            trebleFactor: How much the upper frequencies should be scaled
            pulsePerc: If the returned loudness should contain the harmonic or percussive component of the audio
            showPlots: If the plots of the different metadata should be displayed
        """
        # Defining class attributes
        self.percData = None
        self.harmData = None
        self.sr = None
        self.fullData = None
        self.sourcePath = sourcePath
        self.duration = duration
        self.sampleRate = sampleRate
        self.start = start
        self.frameDuration = frameDuration
        self.sectionAmount = sectionAmount
        self.gateThreshold = gateThreshold
        self.bassFactor = bassFactor
        self.midFactor = midFactor
        self.trebleFactor = trebleFactor
        self.pulsePerc = pulsePerc
        self.showPlots = showPlots
        self.songSections = None
        self.pulseData = None

    def startAnalysis(self):
        """
        Load the audio file, split it into harm and perc components and then start the analysis for each component.
        Returns: The loudness curve as an array and the section beginnings as an array

        """
        self.fullData, self.sr = self.loadAudioFile()
        self.harmData, self.percData = self.splitAudioComponents()

        print("Analyzing harmonic content")
        harmMetadata = self.analyzeTrack(self.harmData)
        print("Analyzing percussive content")
        percMetadata = self.analyzeTrack(self.percData)

        if self.pulsePerc:
            self.pulseData = percMetadata["pulseData"]
            self.songSections = percMetadata["songSections"]
        else:
            self.pulseData = harmMetadata["pulseData"]
            self.songSections = harmMetadata["songSections"]

        audioMetadata = {
            "pulseData": self.pulseData,
            "songSections": self.songSections
        }

        return audioMetadata

    def loadAudioFile(self):
        """
        Retrieve audio data and sample rate
        Returns: The audio data as a float array

        """
        print("Loading audio file...")

        # Load audio file
        data, sr = librosa.load(path=self.sourcePath, duration=self.duration, sr=self.sampleRate, offset=self.start)

        return data, sr

    def analyzeTrack(self, audioData):
        """
        Main analysis function where all analyzing functions are called
        Args:
            audioData: Floating point data to analyze

        Returns: Sample loudness and sections of provided data

        """
        # Get fourier spectrum
        fourierData = self.getFourierData(audioData=audioData)

        # Scale frequency bands
        scaledFrequencies = self.scaleFrequencyAreas(fourierData=fourierData)

        # Calculate loudness per sample
        sampleLoudness = self.getSampleLoudness(fourierData=scaledFrequencies)

        # Normalizing loudness
        normalizedLoudness = self.getNormalizedLoudness(audioData=sampleLoudness)

        # Gating normalized loudness
        gatedLoudness = self.gateLoudness(audioData=normalizedLoudness)

        # Calculate start of song sections
        songSections = self.analyzeSections(fourierData=fourierData)

        audio_metadata = {
            "pulseData": gatedLoudness,
            "songSections": songSections
        }

        return audio_metadata

    def splitAudioComponents(self):
        """
        Splits the audio into harmonic and percussive components
        Returns: The harmonic and the percussive component

        """
        print("Splitting audio...")
        harmonic, percussive = librosa.effects.hpss(self.fullData)

        return harmonic, percussive

    def getFourierData(self, audioData):
        """
        Short time fourier transform and mapping of the stft to the mel scale
        Args:
            audioData: The audio data to analyze

        Returns: The scaled stft data

        """
        print("Retrieving FFT data...")

        # Retrieving FFT data
        fourierData = np.abs(librosa.stft(y=audioData, hop_length=self.frameDuration))

        # Mapping FFT data onto the human hearing mel scale
        fourierData = librosa.feature.melspectrogram(S=fourierData)

        if self.showPlots:
            fig, ax = plt.subplots()
            img = librosa.display.specshow(librosa.amplitude_to_db(fourierData, ref=np.max), y_axis="mel", x_axis="time",
                                           ax=ax)
            ax.set_title("Power spectrogram")
            fig.colorbar(img, ax=ax, format="%+2.0f dB")

            plt.show()

        return fourierData

    def scaleFrequencyAreas(self, fourierData):
        """
        Scaling each frequency area by the provided factor
        Args:
            fourierData: The data in which to scale the areas

        Returns: The data with scaled areas

        """
        print("Scaling frequency bands...")

        # Calculate size of frequency bands
        amountFrequencyBands = len(fourierData)
        amountBassBands = int(amountFrequencyBands * 0.01)
        amountMidBands = int(amountFrequencyBands * 0.26)

        # Set bass band loudness
        fourierData[:amountBassBands] = fourierData[:amountBassBands] * self.bassFactor

        # Set mid band loudness
        fourierData[amountBassBands:amountMidBands] = fourierData[amountBassBands:amountMidBands] * self.midFactor

        # Set treble band loudness
        fourierData[amountMidBands:] = fourierData[amountMidBands:] * self.trebleFactor

        return fourierData

    def getSampleLoudness(self, fourierData):
        """
        Returns loudness for each sample as a float value
        Args:
            fourierData: The data from which to infer the sample loudness

        Returns: Array of sample loudness values

        """
        print("Calculating sample loudness...")

        sampleLoudness = np.ndarray(len(fourierData[0]))

        # Calculate loudness for each sample
        for i in range(len(sampleLoudness)):
            sampleLoudness[i] = np.average(fourierData[:, i])

        if self.showPlots:
            plt.plot(sampleLoudness)
            plt.show()

        return sampleLoudness

    def getNormalizedLoudness(self, audioData):
        """
        Normalizes the float audio between 0 and 1
        Args:
            audioData: The audio data to normalize

        Returns: The normalized audio data array

        """
        print("Normalizing sample loudness...")

        # Retrieving minimum and maximum of the wav data
        maxVolume = np.amax(audioData)
        minVolume = np.amin(audioData)

        # Normalizing the wav float data
        normalizedData = (audioData - minVolume) / (maxVolume - minVolume)

        if self.showPlots:
            plt.plot(normalizedData)
            plt.show()

        return normalizedData

    def gateLoudness(self, audioData):
        """
        Gating loudness: Only letting through the louder parts according to the threshold
        Args:
            audioData: The audio data to gate

        Returns: The gated audio data array

        """
        print("Gating loudness samples...")

        audioData[audioData < self.gateThreshold] = 0
        audioGated = audioData

        if self.showPlots:
            plt.plot(audioGated)
            plt.show()

        return audioGated

    def analyzeSections(self, fourierData):
        """
        Divide audio into sections defined by characteristic spectral differences
        Args:
            fourierData: The data from which to analyze the sections

        Returns: Array with starting points for each section in seconds

        """
        print("Calculating song sections...")

        # Calculate start of sections in seconds
        sectionBoundaries = librosa.segment.agglomerative(data=fourierData, k=self.sectionAmount, axis=-1)
        boundaryTimes = librosa.frames_to_time(sectionBoundaries, sr=self.sampleRate)
        print("Section beginnings: {}".format(boundaryTimes))

        if self.showPlots:
            # Plot spectrogram and sections
            fig, ax = plt.subplots()
            trans = mpt.blended_transform_factory(ax.transData, ax.transAxes)
            img = librosa.display.specshow(librosa.amplitude_to_db(fourierData, ref=np.max), sr=self.frameDuration, y_axis='fft',
                                           x_axis='time', ax=ax)
            ax.vlines(sectionBoundaries, 0, 1, color="linen", linestyle="--", linewidth=2, alpha=0.9, label="Segment boundaries",
                      transform=trans)
            ax.legend()
            ax.set(title="Power spectrogram")
            fig.colorbar(img, ax=ax, format="%+2.0f dB")

            plt.show()

        return boundaryTimes
