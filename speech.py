import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
from pydub import AudioSegment
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

# Convert stereo to mono using pydub
print("Converting to mono...")
audio = AudioSegment.from_wav(wav_filename)
audio = audio.set_channels(1)
mono_filename = "recording_mono.wav"
audio.export(mono_filename, format="wav")

# Read the mono WAV file for Google Speech-to-Text
with io.open(mono_filename, "rb") as audio_file:
    content = audio_file.read()

audio = speech.RecognitionAudio(content=content)

# Speaker diarization configuration
diarization_config = speech.SpeakerDiarizationConfig(
    enable_speaker_diarization=True,
    min_speaker_count=2,
    max_speaker_count=10,
)

# Recognition configuration
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=44100,  # Match the sample rate of your file
    language_code="en-US",
    diarization_config=diarization_config,
)

# Perform speech recognition
print("Waiting for operation to complete...")
response = client.recognize(config=config, audio=audio)

# The transcript within each result is separate and sequential per result.
# However, the words list within an alternative includes all the words
# from all the results thus far. Thus, to get all the words with speaker
# tags, you only have to take the words list from the last result:
result = response.results[-1]

words_info = result.alternatives[0].words

# Print out the recognized words with speaker tags
for word_info in words_info:
    print(f"word: '{word_info.word}', speaker_tag: {word_info.speaker_tag}")

print("Transcription complete.")
