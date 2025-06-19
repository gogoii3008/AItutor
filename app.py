import os
import subprocess
from flask import Flask, request, render_template
import requests
import json
from vosk import Model, KaldiRecognizer
import wave

app = Flask(__name__)

# Setup Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

# Load Vosk model (ensure model directory is downloaded and named 'vosk-model')
VOSK_MODEL_PATH = "vosk-model"
model = Model(VOSK_MODEL_PATH)

# Function to generate custom prompts based on language
def generate_prompt(user_input, lang="English"):
    if lang.lower() == "assamese":
        return f"Explain this concept to a Class 10 Assamese student in Assamese: {user_input}"
    elif lang.lower() == "hindi":
        return f"Explain this concept to a Class 10 Hindi-medium student in Hindi: {user_input}"
    else:
        return f"Explain this clearly to a Class 10 student: {user_input}"

# Gemini API call function
def call_gemini(prompt):
    headers = {
        "Content-Type": "application/json"
    }
    params = {
        "key": GEMINI_API_KEY
    }
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=data)
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]

# Transcribe voice using Vosk
def transcribe_audio(wav_path):
    wf = wave.open(wav_path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result_text += json.loads(rec.Result())["text"] + " "
    result_text += json.loads(rec.FinalResult())["text"]
    return result_text.strip()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/bot", methods=["POST"])
def bot():
    lang = request.form.get('Language', 'English')
    incoming_msg = request.form.get('Body', '')
    audio_file = request.files.get('Media0')

    input_path = "input.ogg"
    output_path = "output.wav"

    # If voice is used, convert and transcribe
    if audio_file:
        audio_file.save(input_path)
        try:
            subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)
            incoming_msg = transcribe_audio(output_path)
        except Exception as e:
            return f"Audio conversion/transcription failed: {str(e)}", 500
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

    if not incoming_msg:
        return "No message received", 400

    try:
        prompt = generate_prompt(incoming_msg, lang)
        answer = call_gemini(prompt)
    except Exception as e:
        return f"Gemini error: {str(e)}", 500

    return answer

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
