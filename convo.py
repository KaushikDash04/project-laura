import os
import json
import google.generativeai as genai
from gtts import gTTS
import playsound
import speech_recognition as sr

# Set up your Google Gemini API key
genai.configure(api_key="AIzaSyCyuO8VraoqwoztmztC2GVS3Jgc3jigW6k")

# Configuration for the generative model
generation_config = {
    "temperature": 0.5,  # Lower temperature for more focused responses
    "top_p": 0.8,        # Slightly lower top_p to limit response variety
    "top_k": 30,         # Lower top_k for more concise responses
    "max_output_tokens": 150,  # Limit the number of tokens for shorter answers
    "response_mime_type": "text/plain",
}

# Load the conversation data from the JSON file
def load_conversations(filename="conversation_log.json"):
    with open(filename, "r", encoding="utf-8") as log_file:
        return json.load(log_file)

# Generate a response from the AI using only the context from the conversation
def answer_question(conversation_data, question):
    # Start a chat session with Google Gemini
    chat_session = genai.GenerativeModel(
        model_name="gemini-1.5-pro",
        generation_config=generation_config,
    ).start_chat()

    # Combine conversation entries into a single string with timestamps
    conversation_text = "\n".join([f"[{entry['timestamp']}] {entry['text']}" for entry in conversation_data])

    # Create a prompt that includes both the conversation context and the question
    prompt = f"Here is a conversation with timestamps:\n\n{conversation_text}\n\nBased on this conversation, answer the following question concisely:\n\n{question}"
    
    # Send the prompt to Google Gemini for processing
    response = chat_session.send_message(prompt)

    # Return the AI's response
    return response.text

def text_to_speech(text):
    """Convert text to speech and play the audio."""
    tts = gTTS(text)
    audio_filename = "response.mp3"
    tts.save(audio_filename)
    playsound.playsound(audio_filename)
    os.remove(audio_filename)

def speech_to_text():
    """Capture audio input and convert it to text."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Sorry, there was an issue with the speech recognition service.")
            return None

# Main function to load the conversation log and allow interactive questioning
def main():
    # Load the conversation log
    conversations = load_conversations("conversation_log.json")

    print("Conversation data loaded. You can now ask questions based on the conversation context.")

    # Interactive loop for asking questions
    while True:
        print("\nSay something (or type 'exit' to quit):")
        question = speech_to_text()
        if question is None:
            continue
        if 'exit' in question.lower():
            break
        # Get the answer based on the context of the conversation
        answer = answer_question(conversations, question)
        # Convert answer to speech
        text_to_speech(answer)

# Run the main function
if __name__ == "__main__":
    main()
