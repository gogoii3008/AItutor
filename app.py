from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# Load OpenAI API key from environment
openai.api_key = os.environ.get("AItutor")

# Generate prompt for GPT
def generate_prompt(user_input, lang="Hindi"):
    if lang == "Assamese":
        return f"Explain this concept to a Class 10 Assamese student in Assamese: {user_input}"
    elif lang == "English":
        return f"Explain this clearly to a Class 10 student: {user_input}"
    else:
        return f"Explain this concept to a Class 10 Hindi-medium student in Hindi: {user_input}"

# WhatsApp bot route
@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get('Body')
    lang = "Hindi"  # Default language

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": generate_prompt(incoming_msg, lang)}
            ]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Sorry, something went wrong: {str(e)}"

    twilio_response = MessagingResponse()
    twilio_response.message(answer)
    return str(twilio_response)

# Web interface route
@app.route("/")
def home():
    return render_template("index.html")  # ✅ This loads index.html from /templates

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
