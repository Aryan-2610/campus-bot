from flask import Flask, render_template, request, jsonify
from engine import CampusBot

app = Flask(__name__)

## Initialize the bot once when the server starts
bot = CampusBot()

@app.route("/")
def home():
    ## Renders your DTU Clone HTML
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "No message"}), 400
    
    ## Get response from your existing engine.py
    response_data = bot.chat(user_input)
    
    ## Send back the JSON response to the widget
    return jsonify(response_data)

if __name__ == "__main__":
    app.run(port=5001, debug=True)