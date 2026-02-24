import speech_recognition as sr
import pyttsx3
import requests

# Initialize text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def chat_with_llama(prompt):
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(url, json=payload)
        return response.json()["response"]
    except:
        return "Sorry, I cannot connect to the AI."

recognizer = sr.Recognizer()

print("🎤 Voice Assistant Started (Say 'stop' to exit)")

while True:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)

            text = recognizer.recognize_google(audio)
            print("You:", text)

            if text.lower() == "stop":
                speak("Goodbye!")
                break

            reply = chat_with_llama(text)
            print("Bot:", reply)
            speak(reply)

    except Exception as e:
        print("Error:", e)