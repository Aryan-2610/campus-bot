import os
import logging
import threading
import time  # <--- 1. IMPORT THE TIME MODULE
from flask import Flask, request, send_from_directory
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv

# 1. --- INITIAL SETUP ---
load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# 2. --- HARDCODED RESPONSES ---
HARDCODED_KANNADA_TEXT = "ಗೌರವಾನ್ವಿತ ಉಪಕುಲಪತಿಗಳ ಹೆಸರು ಪ್ರೊ. ಪ್ರತೀಕ್ ಶರ್ಮಾ."
LOCAL_OGG_RESPONSE_FILE = "1.opus"

# 3. --- CLIENT INITIALIZATIONS ---
app = Flask(__name__)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
PUBLIC_BASE_URL = os.getenv('PUBLIC_BASE_URL')
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# 4. --- BACKGROUND TASK FOR HARDCODED REPLIES ---
def process_and_reply(incoming_data):
    from_num = incoming_data['from_num']
    is_voice = incoming_data['is_voice']

    try:
        if is_voice:
            # --- 2. ADD THE DELAY HERE ---
            logger.info("Voice input received. Waiting for 20 seconds before replying...")
            time.sleep(20) # This pauses the execution of this thread for 20 seconds.
            logger.info("Delay finished. Proceeding to send audio reply.")
            # -----------------------------

            public_media_url = f"{incoming_data['base_url']}/static/{LOCAL_OGG_RESPONSE_FILE}"
            logger.info(f"Sending media URL: {public_media_url}")
            twilio_client.messages.create(
                from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                to=from_num,
                media_url=[public_media_url]
            )
        else:
            logger.info(f"Received text input from {from_num}. Replying with hardcoded Kannada text.")
            twilio_client.messages.create(
                from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
                to=from_num,
                body=HARDCODED_KANNADA_TEXT
            )
    except Exception as e:
        logger.error(f"❌ Background task failed: {e}", exc_info=True)


# 5. --- FLASK WEB ROUTES ---
@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    if not PUBLIC_BASE_URL:
        logger.error("FATAL: PUBLIC_BASE_URL is not set in .env file!")
        return str(MessagingResponse())
    incoming = request.values
    task_data = {
        'from_num': incoming.get('From', '').strip(),
        'is_voice': int(incoming.get('NumMedia', 0)) > 0,
        'base_url': PUBLIC_BASE_URL
    }
    thread = threading.Thread(target=process_and_reply, args=(task_data,))
    thread.start()
    return str(MessagingResponse())


@app.route('/static/<path:filename>')
def serve_static_media(filename):
    """
    This route serves files from the 'static' directory.
    This is the conventional and correct way to handle static files in Flask.
    """
    logger.info(f"Attempting to serve '{filename}' from the 'static' directory.")
    try:
        # 'static' is the name of the folder where your media files are.
        return send_from_directory('static', filename, as_attachment=True)
    except FileNotFoundError:
        logger.error(f"❌ File '{filename}' not found in the 'static' directory.")
        return {"error": "File not found"}, 404


@app.route("/health", methods=['GET'])
def health_check():
    return {"status": "healthy"}, 200

# 6. --- MAIN EXECUTION ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)