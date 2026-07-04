from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), nullable=False)
    query = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    fallback_score = db.Column(db.Float, default=0.0)
    ip_address = db.Column(db.String(64))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class FAQ(db.Model):
    __tablename__ = 'faqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(500), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    language = db.Column(db.String(10), default='en')

class BotConfig(db.Model):
    __tablename__ = 'bot_config'
    id = db.Column(db.Integer, primary_key=True)
    enable_website = db.Column(db.Boolean, default=True)
    enable_whatsapp = db.Column(db.Boolean, default=False)
    enable_telegram = db.Column(db.Boolean, default=False)
    fallback_message = db.Column(
        db.String(500), 
        default="Sorry, I couldn't find an answer to your question. Please try rephrasing it."
    )

class Ticket(db.Model):
    __tablename__ = 'tickets'
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(36), unique=True, nullable=False)
    query = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='open')  # open, in progress, closed
    admin_response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
