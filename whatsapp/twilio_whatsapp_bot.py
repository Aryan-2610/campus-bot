import os
import logging
import asyncio
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from dotenv import load_dotenv
from rag_chat import chat
from ingest import ingest

# 1) Load env and configure logging
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 2) Initialize Flask and Twilio client
app = Flask(__name__)
TWILIO_ACCOUNT_SID  = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN   = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
twilio_client       = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# 3) Helper to split long messages
def split_long_message(message, max_length=1500):
    if len(message) <= max_length:
        return [message]
    parts = []
    words = message.split(' ')
    current = ""
    for w in words:
        if len(current + ' ' + w) <= max_length:
            current += (' ' + w) if current else w
        else:
            parts.append(current)
            current = w
    if current:
        parts.append(current)
    return parts

# 4) Webhook route
@app.route("/webhook", methods=['POST'])
def whatsapp_webhook():
    # Ensure an asyncio loop exists
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    incoming = request.values.get('Body', '').strip()
    from_num = request.values.get('From', '').strip()
    logger.info(f"Received message from {from_num}: {incoming}")

    resp = MessagingResponse()
    if not incoming:
        resp.message("Hello! I'm DTU Campus Assistant 🎓\n\nJust ask me anything!")
        return str(resp)

    try:
        reply = chat(incoming)
        if len(reply) > 1500:
            for part in split_long_message(reply):
                resp.message(part)
        else:
            resp.message(reply)
        logger.info(f"Sent response to {from_num}")
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        resp.message("Sorry, something went wrong.")
    return str(resp)

# 5) Send-message route
@app.route("/send_message", methods=['POST'])
def send_message():
    data = request.json or {}
    to_num  = data.get('to')
    msg     = data.get('message')
    if not to_num or not msg:
        return {"error": "Missing 'to' or 'message'"}, 400
    try:
        m = twilio_client.messages.create(
            body=msg,
            from_=f"whatsapp:{TWILIO_PHONE_NUMBER}",
            to=f"whatsapp:{to_num}"
        )
        return {"success": True, "sid": m.sid}
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"error": str(e)}, 500

# 6) Health and home routes
@app.route("/health", methods=['GET'])
def health_check():
    return {"status": "healthy"}

@app.route("/", methods=['GET'])
def home():
    return "<h1>DTU WhatsApp Bot Running</h1>"

# 7) Main entry point
if __name__ == "__main__":
    # Only ingest once (in child process if using debug reloader)
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true" or not app.debug:
        logger.info("🔄 Ingesting documents into ChromaDB…")
        ingest()
        logger.info("✅ Ingestion complete.")

    # Validate env vars
    missing = [v for v in ('TWILIO_ACCOUNT_SID','TWILIO_AUTH_TOKEN','TWILIO_PHONE_NUMBER','GOOGLE_API_KEY') if not os.getenv(v)]
    if missing:
        logger.error(f"Missing env vars: {missing}")
        exit(1)

    logger.info("🚀 Starting DTU WhatsApp Bot on port 5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
