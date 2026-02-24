from flask import Flask, render_template, request, jsonify
import requests
import sqlite3

app = Flask(__name__)

# ----------------------------
# DATABASE SETUP
# ----------------------------
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT,
            bot_reply TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ----------------------------
# LLM FUNCTION
# ----------------------------
def chat_with_llama(prompt):
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=payload)
    return response.json()["response"]

# ----------------------------
# HOME ROUTE
# ----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# ----------------------------
# CHAT ROUTE WITH MEMORY
# ----------------------------
@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json["message"]

    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Get last 5 messages
    c.execute("SELECT user_message, bot_reply FROM chats ORDER BY id DESC LIMIT 5")
    history = c.fetchall()
    history.reverse()

    # Build context
    context = ""
    for user, bot in history:
        context += f"User: {user}\nBot: {bot}\n"

    context += f"User: {user_message}\nBot:"

    # Get response from Llama
    bot_reply = chat_with_llama(context)

    # Save new conversation
    c.execute("INSERT INTO chats (user_message, bot_reply) VALUES (?, ?)",
              (user_message, bot_reply))
    conn.commit()
    conn.close()

    return jsonify({"reply": bot_reply})

# ----------------------------
# FILE UPLOAD ROUTE
# ----------------------------
@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:
        return jsonify({"reply": "No file uploaded!"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"reply": "Please select a file."})

    try:
        # Read file safely
        text = file.read().decode("utf-8", errors="ignore")

        if text.strip() == "":
            return jsonify({"reply": "File is empty or unsupported format."})

        prompt = f"Explain this file content simply:\n{text}"
        reply = chat_with_llama(prompt)

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"reply": f"Error processing file: {str(e)}"})
# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)