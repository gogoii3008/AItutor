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
GOOGLE_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyA5JvmQ1PbN5KGWMsuvpjf759b4GOCWfUI")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body", "")
    sender_lang = "english"  # You can extract from metadata or use default
    from_number = request.form.get("From")

    # Generate response using Gemini
    if incoming_msg:
        prompt = f"Explain this clearly to a student: {incoming_msg}"
        response = model.generate_content(prompt)
        answer = response.text.strip()
    else:
        answer = "Please send a valid question."

    # Optional: generate voice response
    tts_lang = 'en'
    filename = f"static/whatsapp_{uuid.uuid4().hex}.mp3"
    gTTS(text=answer, lang=tts_lang).save(filename)

    # Create reply
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(answer)
    # msg.media(f"https://your-domain.com/{filename}")  # Optional: send audio back

    return str(resp)

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
