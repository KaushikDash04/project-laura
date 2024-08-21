import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
import google.cloud.speech as speech
from google.cloud import speech_v1p1beta1 as speech
import io

# Set up the Google Speech-to-Text API client
client = speech.SpeechClient()

# Recording configuration
freq = 44100  # Sample rate
duration = 5  # Duration of the recording in seconds

# Record audio
print("Recording...")
recording = sd.rec(int(duration * freq), samplerate=freq, channels=2)
sd.wait()  # Wait for the recording to finish
print("Recording complete.")

# Save the recording as a WAV file
wav_filename = "recording.wav"
wv.write(wav_filename, recording, freq, sampwidth=2)

# Read the WAV file
with io.open(wav_filename, "rb") as audio_file:
    content = audio_file.read()

