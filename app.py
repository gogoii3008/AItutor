import os
import subprocess
from flask import Flask, request, render_template, jsonify
import openai

app = Flask(__name__)

# Load your OpenAI key from environment variable
openai.api_key = os.environ.get("AItutor")

# Generate prompt based on selected language
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
    # Get language selection
    lang = request.form.get('Language', 'English')
    incoming_msg = request.form.get('Body', '')
    audio_file = request.files.get('Media0')

    input_path = "input.ogg"
    output_path = "output.wav"

    # Case 1: Audio message received
    if audio_file:
        audio_file.save(input_path)
        try:
            subprocess.run(["ffmpeg", "-y", "-i", input_path, output_path], check=True)
        except subprocess.CalledProcessError:
            return "Error: Audio conversion failed", 500

        try:
            with open(output_path, "rb") as f:
                transcript = openai.Audio.transcribe("whisper-1", f)
                incoming_msg = transcript["text"]
        except Exception as e:
            return f"Whisper error: {str(e)}", 500
        finally:
            if os.path.exists(input_path): os.remove(input_path)
            if os.path.exists(output_path): os.remove(output_path)

    # Case 2: Text message received
    if not incoming_msg:
        return "No message received", 400

    try:
        prompt = generate_prompt(incoming_msg, lang)
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        return f"GPT error: {str(e)}", 500

    return answer

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
