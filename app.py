import os
import subprocess
import wave
import json
import requests
from flask import Flask, request, render_template

from vosk import Model, KaldiRecognizer

app = Flask(__name__)

# Load DeepSeek API Key
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Load Vosk model (must be placed in project directory)
VOSK_MODEL_PATH = "vosk-model"

# 🔁 Function to transcribe audio using Vosk
def transcribe_audio(path):
    model = Model(VOSK_MODEL_PATH)
    wf = wave.open(path, "rb")
    rec = KaldiRecognizer(model, wf.getframerate())
    
    text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            text += result.get("text", "") + " "
    
    return text.strip()

# 🔁 Prompt generation based on language
def generate_prompt(user_input, lang="English"):
    lang = lang.lower()
    if lang == "assamese":
        return f"Explain this concept to a Class 10 Assamese student in Assamese: {user_input}"
    elif lang == "hindi":
        return f"Explain this concept to a Class 10 Hindi-medium student in Hindi: {user_input}"
    else:
        return f"Explain this clearly to a Class 10 student: {user_input}"

# 🏠 Home page route
@app.route("/")
def index():
    return render_template("index.html")

# 🤖 Bot endpoint
@app.route("/bot", methods=["POST"])
def bot():
    lang = request.form.get('Language', 'English')
    incoming_msg = request.form.get('Body', '')
    audio_file = request.files.get('Media0')

    input_path = "input.ogg"
    output_path = "output.wav"

    # 🧠 Handle audio input
    if audio_file:
        audio_file.save(input_path)
        try:
            subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)
        except subprocess.CalledProcessError:
            return "Error: Audio conversion failed", 500

        try:
            incoming_msg = transcribe_audio(output_path)
        except Exception as e:
            return f"Transcription error: {str(e)}", 500
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

    # 📭 No input check
    if not incoming_msg:
        return "No message received", 400

    # 💬 Generate response from DeepSeek
    try:
        prompt = generate_prompt(incoming_msg, lang)
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        answer = result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"DeepSeek error: {str(e)}", 500

    return answer

# 🚀 Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
