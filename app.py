import os
import subprocess
from flask import Flask, request, jsonify
import openai

# Set your OpenAI API Key from environment variable
openai.api_key = os.environ.get("AItutor")

app = Flask(__name__)

# Function to create prompt based on selected language
def generate_prompt(user_input, lang="English"):
    if lang.lower() == "assamese":
        return f"Explain this concept to a Class 10 Assamese student in Assamese: {user_input}"
    elif lang.lower() == "hindi":
        return f"Explain this concept to a Class 10 Hindi-medium student in Hindi: {user_input}"
    else:
        return f"Explain this clearly to a Class 10 student: {user_input}"

@app.route("/")
def home():
    return "AI Tutor is live!"

@app.route("/bot", methods=["POST"])
def bot():
    # Get language from form (default = English)
    lang = request.form.get('Language', 'English')

    # Get audio file from Twilio WhatsApp webhook
    audio_file = request.files.get('Media0')  # Twilio uses Media0 for 1st attachment
    if not audio_file:
        return "No audio received", 400

    # Save uploaded file
    input_path = "input.ogg"
    output_path = "output.wav"
    audio_file.save(input_path)

    # Convert to .wav using ffmpeg
    try:
        subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)
    except subprocess.CalledProcessError as e:
        return f"ffmpeg conversion failed: {e}", 500

    # Transcribe using OpenAI Whisper
    try:
        with open(output_path, "rb") as f:
            transcript = openai.Audio.transcribe("whisper-1", f)
            user_text = transcript["text"]
    except Exception as e:
        return f"Whisper transcription failed: {e}", 500

    # Generate prompt and get GPT response
    try:
        prompt = generate_prompt(user_text, lang)
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        return f"OpenAI GPT error: {e}", 500
    finally:
        # Cleanup files
        if os.path.exists(input_path): os.remove(input_path)
        if os.path.exists(output_path): os.remove(output_path)

    return answer

if __name__ == "__main__":
    app.run(debug=True, port=5000)
