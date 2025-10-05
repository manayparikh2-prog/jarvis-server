from flask import Flask, request, jsonify, send_file
import pyttsx3
import requests
import random

app = Flask(__name__)
WEATHER_API_KEY = "03993da73feebfa88d3a5c98c27c8b39"

def speak_to_file(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    voices = engine.getProperty('voices')
    for v in voices:
        if "male" in v.name.lower():
            engine.setProperty('voice', v.id)
            break
    engine.save_to_file(text, "response.mp3")
    engine.runAndWait()

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    data = requests.get(url).json()
    if data.get("cod") != 200:
        return f"Couldn't find weather for {city}"
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    humidity = data["main"]["humidity"]
    return f"{city.title()}: {desc}, {temp}°C, humidity {humidity}%"

def get_synonym(word):
    url = f"https://api.datamuse.com/words?rel_syn={word}"
    data = requests.get(url).json()
    if not data:
        return f"No synonyms found for {word}"
    synonyms = [item["word"] for item in data[:5]]
    return f"Synonyms for {word}: " + ", ".join(synonyms)

def get_joke():
    jokes = [
        "Why did the computer go to therapy? It had too many bytes of emotional baggage.",
        "Jarvis tried to tell a joke once... it was too logical to be funny.",
        "Why don’t robots panic? They have nerves of steel."
    ]
    return random.choice(jokes)

def get_wikipedia(query):
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
    headers = {"User-Agent": "JarvisGlasses/1.0"}
    data = requests.get(url, headers=headers).json()
    return data.get("extract", "No summary found.")

@app.route("/jarvis", methods=["POST"])
def jarvis():
    command = request.json.get("command", "").lower()
    response = "I didn't understand that."

    if "weather" in command:
        city = command.split("in")[-1].strip()
        response = get_weather(city)
    elif "synonym" in command:
        word = command.split("for")[-1].strip()
        response = get_synonym(word)
    elif "joke" in command:
        response = get_joke()
    elif "what is" in command or "who is" in command or "define" in command:
        query = command.replace("what is", "").replace("who is", "").replace("define", "").strip()
        response = get_wikipedia(query)
    elif any(op in command for op in ["+", "-", "*", "/"]):
        try:
            result = eval(command)
            response = f"{command} equals {result}"
        except:
            response = "Math error."

    speak_to_file(response)
    return jsonify({"text": response})

@app.route("/audio", methods=["GET"])
def audio():
    return send_file("response.mp3", mimetype="audio/mpeg")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

