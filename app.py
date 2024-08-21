import sounddevice as sd
from scipy.io.wavfile import write
import wavio as wv
from pydub import AudioSegment
from google.cloud import speech_v1p1beta1 as speech
import io
import json
from datetime import datetime

# Set up the Google Speech-to-Text API client
client = speech.SpeechClient()

# Initialize conversation list
conversations = []

def record_audio(duration=5, freq=44100, channels=2, output_filename="recording.wav"):
    print("Recording...")
    recording = sd.rec(int(duration * freq), samplerate=freq, channels=channels)
    sd.wait()  # Wait for the recording to finish
    print("Recording complete.")
    wv.write(output_filename, recording, freq, sampwidth=2)

    return output_filename

def convert_to_mono(input_filename, output_filename="recording_mono.wav"):
    print("Converting to mono...")
    audio = AudioSegment.from_wav(input_filename)
    audio = audio.set_channels(1)
    audio.export(output_filename, format="wav")

    return output_filename

def perform_speech_recognition(filename, min_speaker_count=2, max_speaker_count=10):
    with io.open(filename, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    diarization_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=min_speaker_count,
        max_speaker_count=max_speaker_count,
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,  # Match the sample rate of your file
        language_code="en-US",
        diarization_config=diarization_config,
    )

    print("Waiting for operation to complete...")
    response = client.recognize(config=config, audio=audio)

    return response

def save_conversation_log(conversations, json_filename="conversation_log.json", text_filename="conversation_log.txt"):
    with open(json_filename, "w") as log_file, open(text_filename, "w", encoding="utf-8") as log_text_file:
        json.dump(conversations, log_file, indent=4)
        for entry in conversations:
            log_text_file.write(f"{entry['timestamp']}: {entry['text']}\n")

def process_and_save_conversation():
    # Record and process continuously until manually stopped
    try:
        while True:
            # Step 1: Record audio
            wav_filename = record_audio()

            # Step 2: Convert to mono
            mono_filename = convert_to_mono(wav_filename)

            # Step 3: Perform speech recognition with speaker diarization
            response = perform_speech_recognition(mono_filename)

            # Step 4: Process the response and save conversation log
            for result in response.results:
                words_info = result.alternatives[0].words
                for word_info in words_info:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    speaker_tag = word_info.speaker_tag
                    word = word_info.word
                    text = f"Speaker {speaker_tag}: {word}"

                    # Append the record to the conversation list
                    conversations.append({"timestamp": timestamp, "speaker_tag": speaker_tag, "text": text})

            # Save conversations periodically
            save_conversation_log(conversations)

    except KeyboardInterrupt:
        print("Stopped recording.")
        save_conversation_log(conversations)
        print("Conversations processed and saved.")

if __name__ == "__main__":
    process_and_save_conversation()
