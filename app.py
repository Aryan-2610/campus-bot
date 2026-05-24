import os
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from dotenv import load_dotenv
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
# Import your updated decoupled engine
from rag_engine import CampusRAGEngine

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize the engine once when the server boots.
# This will safely load the FAISS and BM25 databases from the 'db/' folder.
try:
    bot_engine = CampusRAGEngine()
except SystemExit:
    print("❌ Server startup aborted: Local database cache ('db/') is missing.")
    print("👉 Please run 'python ingest.py' before launching app.py.")
    os._exit(1)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing message parameter"}), 400
        
    user_message = data["message"]
    
    try:
        # Get response using your read-only database architecture
        bot_response = bot_engine.get_response(user_message)
        return jsonify({"answer": bot_response})
    except Exception as e:
        print(f"Error handling chat request: {e}")
        return jsonify({"answer": "Sorry, I encountered an internal error parsing that request.", "error": str(e)}), 500

if __name__ == "__main__":
    # Standard development port configuration
    app.run(host="0.0.0.0", port=5001, debug=True)