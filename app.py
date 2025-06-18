from flask import Flask, request
import requests
import openai
from pydub import AudioSegment
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# 🔑 Set your API keys here
openai.api_key = "YOUR_OPENAI_API_KEY"
TWILIO_SID = "YOUR_TWILIO_ACCOUNT_SID"
TWILIO_AUTH_TOKEN = "YOUR_TWILIO_AUTH_TOKEN"
TWILIO_AUTH = (TWILIO_SID, TWILIO_AUTH_TOKEN)


# ✏️ Function to generate prompts based on selected language
def generate_prompt(user_input, lang="Hindi"):
    if lang.lower() == "assamese":
        return f"Explain this concept to a Class 10 Assamese student in Assamese: {user_input}"
    elif lang.lower() == "english":
        return f"Explain this clearly to a Class 10 student: {user_input}"
    else:
        return f"Explain this concept to a Class 10 Hindi-medium student in Hindi: {user_input}"


# 🧠 Transcribe audio using OpenAI Whisper
def transcribe_audio(audio_path):
    with open(audio_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
    return transcript["text"]


# 📲 Main route to handle WhatsApp messages
@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form
    media_url = incoming_msg.get("MediaUrl0")
    msg_type = incoming_msg.get("MessageType", "")
    lang = request.form.get("Language", "English")

    # Case 1: Voice message received
    if media_url and msg_type.lower() == "voice":
        try:
            # Download voice note
            audio_response = requests.get(media_url + ".ogg", auth=TWILIO_AUTH)
            with open("voice.ogg", "wb") as f:
                f.write(audio_response.content)

            # Convert to mp3 for Whisper
            audio = AudioSegment.from_file("voice.ogg")
            audio.export("voice.mp3", format="mp3")

            # Transcribe voice to text
            user_input = transcribe_audio("voice.mp3")

        except Exception as e:
            user_input = None
            answer = f"Could not process audio: {str(e)}"
            twiml = MessagingResponse()
            twiml.message(answer)
            return str(twiml)
    else:
        # Case 2: Text message
        user_input = incoming_msg.get("Body")

    # If input exists, call GPT-4o
    if user_input:
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "user", "content": generate_prompt(user_input, lang)}
                ]
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            answer = f"Sorry, something went wrong: {str(e)}"
    else:
        answer = "No valid input received."

    # Reply back via Twilio
    twiml = MessagingResponse()
    twiml.message(answer)
    return str(twiml)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
