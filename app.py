from flask import Flask, request,render_template 
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os

app = Flask(__name__)

# Load your OpenAI API key from an environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Basic GPT prompt generator with language control
def generate_prompt(user_input, lang="Hindi"):
    if lang == "Assamese":
        return f"Explain this concept to a Class 10 Assamese student in Assamese: {user_input}"
    elif lang == "English":
        return f"Explain this clearly to a Class 10 student: {user_input}"
    else:  # Default is Hindi
        return f"Explain this concept to a Class 10 Hindi-medium student in Hindi: {user_input}"

@app.route("/bot", methods=["POST"])
def bot():
    incoming_msg = request.form.get('Body')
    lang = "Hindi"  # Default language; change based on user preference later

    try:
        # Get GPT response
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": generate_prompt(incoming_msg, lang)}
            ]
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"Sorry, something went wrong: {str(e)}"

    # Prepare Twilio reply
    twilio_response = MessagingResponse()
    twilio_response.message(answer)
    return str(twilio_response)

@app.route("/")
def home():
    return render_template("index.html")
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render uses environment variable PORT
    app.run(host="0.0.0.0", port=port)
