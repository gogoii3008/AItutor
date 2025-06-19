import os
import subprocess
from flask import Flask, request, render_template
import requests
import json

app = Flask(__name__)

# Get Gemini API key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"

# Optional: Whisper will be replaced later with Vosk or real-time STT
def transcribe_audio(audio_path):
    # Placeholder transcription
    return "(transcribed text here)"

# Generate prompt depending on the selected language
def generate_prompt(user_input, lang="English"):
    if lang.lower() == "assamese":
        return f"Explain this concept to a Class 10 Assamese student in Assamese: {user_input}"
    elif lang.lower() == "hindi":
        return f"Explain this concept to a Class 10 Hindi-medium student in Hindi: {user_input}"
    else:
        return f"Explain this clearly to a Class 10 student: {user_input}"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bot", methods=["POST"])
def bot():
    lang = request.form.get("Language", "English")
    incoming_msg = request.form.get("Body", "")
    audio_file = request.files.get("Media0")

    input_path = "input.ogg"
    output_path = "output.wav"

    # Convert audio and transcribe if audio input provided
    if audio_file:
        audio_file.save(input_path)
        try:
            subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)
            incoming_msg = transcribe_audio(output_path)
        except Exception as e:
            return f"Audio processing error: {str(e)}", 500
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

    if not incoming_msg:
        return "No message received", 400

    try:
        prompt = generate_prompt(incoming_msg, lang)
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ]
        }

        response = requests.post(GEMINI_API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        gemini_reply = response.json()
        answer = gemini_reply['candidates'][0]['content']['parts'][0]['text']
        return answer
    except Exception as e:
        return f"Gemini error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
