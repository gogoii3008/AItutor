import os
import subprocess
from flask import Flask, request, render_template
import requests

app = Flask(__name__)

DEEPSEEK_API_KEY = os.environ.get("AItutor")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Prompt generation based on language
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
    lang = request.form.get('Language', 'English')
    incoming_msg = request.form.get('Body', '')
    audio_file = request.files.get('Media0')

    input_path = "input.ogg"
    output_path = "output.wav"

    if audio_file:
        audio_file.save(input_path)
        try:
            subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)
        except subprocess.CalledProcessError:
            return "Audio conversion failed", 500

        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(output_path)
            incoming_msg = result["text"]
        except Exception as e:
            return f"Whisper error: {str(e)}", 500
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

    if not incoming_msg:
        return "No input received", 400

    try:
        prompt = generate_prompt(incoming_msg, lang)
        headers = {
            "Authorization": f"Bearer {AItutor}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}]
        }
        response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"].strip()
        return answer
    except Exception as e:
        return f"DeepSeek error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
