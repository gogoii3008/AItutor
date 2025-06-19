'''import os
import subprocess
from flask import Flask, request, render_template
import requests
import json
from gtts import gTTS

app = Flask(__name__)
'''
# Get Gemini API key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key={GEMINI_API_KEY}"

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
        if lang.lower() == 'hindi':
            tts_lang = 'hi'
        elif lang.lower() == 'assamese':
            tts_lang = 'as'
        else:
            tts_lang = 'en'
        tts = gTTS(text=answer, lang='en')  # Or 'hi' or 'as' based on lang
        tts.save("static/answer.mp3")
        return answer
    except Exception as e:
        return f"Gemini error: {str(e)}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
'''
# -------------------------------------
# 🔧 Step 1: Setup Flask App
# -------------------------------------
app = Flask(__name__)

# Create 'static' folder if it doesn't exist (to store audio files)
if not os.path.exists("static"):
    os.makedirs("static")

# -------------------------------------
# 🔑 Step 2: Configure Gemini API
# -------------------------------------
# Replace with your actual Gemini API key
GOOGLE_API_KEY = "YOUR_GEMINI_API_KEY_HERE"
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini model
model = genai.GenerativeModel("gemini-pro")

# -------------------------------------
# 📄 Step 3: Serve index.html
# -------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------
# 🤖 Step 4: Handle User Question + Language
# -------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    try:
        # 📥 Get form data: question and language
        question = request.form.get("question", "").strip()
        lang = request.form.get("language", "english").lower()

        if not question:
            return jsonify({"error": "Please enter a question"}), 400

        # 🔍 Get AI response from Gemini
        response = model.generate_content(question)
        answer = response.text.strip()

        # 🌐 Determine TTS language code
        if lang == "hindi":
            tts_lang = "hi"
        elif lang == "assamese":
            tts_lang = "as"
        else:
            tts_lang = "en"  # Default to English

        # 🔊 Generate speech using gTTS
        filename = f"answer_{uuid.uuid4().hex}.mp3"  # Unique filename
        filepath = os.path.join("static", filename)
        tts = gTTS(text=answer, lang=tts_lang)
        tts.save(filepath)

        # ✅ Return the answer and audio path
        return jsonify({
            "answer": answer,
            "audio": f"/static/{filename}"
        })

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500


# -------------------------------------
# 🚀 Step 5: Run the Flask App
# -------------------------------------
if __name__ == "__main__":
    app.run(debug=True)'''




import os
import uuid
import subprocess
import json
from flask import Flask, request, render_template, jsonify
import requests
from gtts import gTTS
import google.generativeai as genai

# -------------------------------------
# 🔧 Step 1: Setup Flask App
# -------------------------------------
app = Flask(__name__)

# Create 'static' folder if it doesn't exist (to store audio files)
if not os.path.exists("static"):
    os.makedirs("static")

# -------------------------------------
# 🔑 Step 2: Configure Gemini API
# -------------------------------------
# Use env variable or paste your API key directly
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY", "YAIzaSyA5JvmQ1PbN5KGWMsuvpjf759b4GOCWfUI")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# -------------------------------------
# 📄 Step 3: Serve index.html
# -------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

# -------------------------------------
# 🧠 Step 4: Handle User Question + Language
# -------------------------------------
@app.route("/ask", methods=["POST"])
def ask():
    try:
        question = request.form.get("question", "").strip()
        lang = request.form.get("language", "english").lower()

        if not question:
            return jsonify({"error": "Please enter a question"}), 400

        # Generate content from Gemini
        response = model.generate_content(question)
        answer = response.text.strip()

        # Set TTS language
        if lang == "hindi":
            tts_lang = "hi"
        elif lang == "assamese":
            tts_lang = "as"
        else:
            tts_lang = "en"

        # Generate unique filename and save TTS
        filename = f"answer_{uuid.uuid4().hex}.mp3"
        filepath = os.path.join("static", filename)
        tts = gTTS(text=answer, lang=tts_lang)
        tts.save(filepath)

        return jsonify({
            "answer": answer,
            "audio": f"/static/{filename}"
        })

    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

# -------------------------------------
# 🚀 Step 5: Run the Flask App
# -------------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

