import os
import uuid
import hashlib
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.utils import secure_filename
from sqlalchemy import func, desc

# Import your modules and config
from config import config
import rag_chat as chatbot
from models import db, Conversation, FAQ, BotConfig
from translator import to_english, from_english # ❗ Import translation functions

from models import db, Conversation, FAQ, BotConfig, Ticket
from datetime import datetime
import uuid


# --- App Initialization ---
app = Flask(__name__, static_folder='static', template_folder='templates')
app.config.from_object(config)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# --- Extensions ---
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- Database Setup ---
with app.app_context():
    db.create_all()

# --- API Endpoints ---

@app.route('/api/documents', methods=['POST'])
def post_document():
    """
    Handles document upload by simply saving the file.
    The background 'run_ingestion.py' service will handle the processing.
    """
    if 'file' not in request.files: return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    socketio.emit('documents_updated', {'message': f"File '{filename}' received and queued for processing."})
    return jsonify({"message": f"File '{filename}' was uploaded. Processing will begin shortly."}), 202

@app.route('/api/chat', methods=['POST'])
def handle_chat():
    data = request.json
    query = data.get('query')
    session_id = data.get('sessionId') or str(uuid.uuid4())
    user_lang = data.get('language', 'en-US') # ❗ Get the language from the request
    if not query: return jsonify({"error": "Query is required"}), 400
    # --- PRIVACY IMPLEMENTATION START ---
    remote_ip = request.remote_addr
    hashed_ip = hashlib.sha256(remote_ip.encode('utf-8')).hexdigest()
    # --- PRIVACY IMPLEMENTATION END ---

    # ❗ Translate the user's query to English for the RAG system
    translated_query, _ = to_english(query, source_lang_code=user_lang)

    # Use the translated query with your chatbot
    response_content = chatbot.chat(translated_query)

    # ❗ Translate the response back to the user's language
    final_response = from_english(response_content, target_language_code=user_lang)

    # Save the original query and the translated response
    new_convo = Conversation(
        session_id=session_id,
        query=query,
        response=final_response,
        ip_address=hashed_ip
    )
    db.session.add(new_convo)
    db.session.commit()
    socketio.emit('new_conversation', {'id': new_convo.id, 'query': query, 'timestamp': new_convo.timestamp.isoformat()})
    return jsonify({"response": final_response, "sessionId": session_id})

# ... rest of the app.py file remains the same

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets with optional filtering by status"""
    try:
        status_filter = request.args.get('status', '')
        if status_filter:
            tickets = db.session.execute(
                db.select(Ticket).filter_by(status=status_filter).order_by(Ticket.created_at.desc())
            ).scalars().all()
        else:
            tickets = db.session.execute(
                db.select(Ticket).order_by(Ticket.created_at.desc())
            ).scalars().all()
        
        ticket_list = []
        for ticket in tickets:
            ticket_list.append({
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'query': ticket.query,
                'status': ticket.status,
                'admin_response': ticket.admin_response,
                'created_at': ticket.created_at.isoformat(),
                'closed_at': ticket.closed_at.isoformat() if ticket.closed_at else None
            })
        
        return jsonify({'tickets': ticket_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a specific ticket by ID"""
    try:
        ticket = db.get_or_404(Ticket, ticket_id)
        return jsonify({
            'id': ticket.id,
            'ticket_id': ticket.ticket_id,
            'query': ticket.query,
            'status': ticket.status,
            'admin_response': ticket.admin_response,
            'created_at': ticket.created_at.isoformat(),
            'closed_at': ticket.closed_at.isoformat() if ticket.closed_at else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>/respond', methods=['PUT'])
def respond_to_ticket(ticket_id):
    """Admin responds to a ticket"""
    try:
        data = request.json
        admin_response = data.get('admin_response')
        
        if not admin_response:
            return jsonify({'error': 'Admin response is required'}), 400
            
        ticket = db.get_or_404(Ticket, ticket_id)
        ticket.admin_response = admin_response
        ticket.status = 'answered'  # Change status to answered when admin responds
        
        db.session.commit()
        
        return jsonify({
            'message': 'Response added successfully',
            'ticket': {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'query': ticket.query,
                'status': ticket.status,
                'admin_response': ticket.admin_response,
                'created_at': ticket.created_at.isoformat(),
                'closed_at': ticket.closed_at.isoformat() if ticket.closed_at else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>/close', methods=['PUT'])
def close_ticket(ticket_id):
    """Close a ticket"""
    try:
        ticket = db.get_or_404(Ticket, ticket_id)
        ticket.status = 'closed'
        ticket.closed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Ticket closed successfully',
            'ticket': {
                'id': ticket.id,
                'ticket_id': ticket.ticket_id,
                'query': ticket.query,
                'status': ticket.status,
                'admin_response': ticket.admin_response,
                'created_at': ticket.created_at.isoformat(),
                'closed_at': ticket.closed_at.isoformat() if ticket.closed_at else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tickets/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete a ticket"""
    try:
        ticket = db.get_or_404(Ticket, ticket_id)
        db.session.delete(ticket)
        db.session.commit()
        
        return jsonify({'message': 'Ticket deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/fallback-queries', methods=['GET'])
def get_fallback_queries():
    """Get conversations that triggered fallback responses"""
    try:
        # Find conversations with high fallback scores or fallback messages
        fallback_conversations = db.session.execute(
            db.select(Conversation).filter(
                db.or_(
                    Conversation.fallback_score >= 0.7,
                    Conversation.response.contains("I am sorry, but the information you are looking for is not in my database"),
                    Conversation.response.contains("Sorry, I couldn't find an answer")
                )
            ).order_by(Conversation.timestamp.desc())
        ).scalars().all()
        
        result = []
        for conv in fallback_conversations:
            result.append({
                'id': conv.id,
                'session_id': conv.session_id,
                'query': conv.query,
                'response': conv.response,
                'fallback_score': conv.fallback_score,
                'timestamp': conv.timestamp.isoformat()
            })
        
        return jsonify({'fallback_queries': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/dashboard/stats', methods=['GET'])
def get_stats():
    try:
        conversation_count = db.session.scalar(db.select(func.count(Conversation.id)))
        upload_folder = app.config['UPLOAD_FOLDER']
        document_count = len([name for name in os.listdir(upload_folder) if os.path.isfile(os.path.join(upload_folder, name))]) if os.path.exists(upload_folder) else 0
        stats = {"conversationCount": conversation_count or 0, "totalUsers": 1, "openTickets": 12, "totalDocuments": document_count}
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/documents', methods=['GET'])
def get_documents_list():
    docs = []
    folder = app.config['UPLOAD_FOLDER']
    if os.path.exists(folder):
        for filename in os.listdir(folder):
            filepath = os.path.join(folder, filename)
            if os.path.isfile(filepath):
                docs.append({"filename": filename, "size": os.path.getsize(filepath), "modified": os.path.getmtime(filepath)})
    return jsonify(docs)

@app.route('/api/documents/<path:filename>', methods=['DELETE'])
def delete_document_file(filename):
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
        if os.path.exists(filepath):
            os.remove(filepath)
            socketio.emit('documents_updated', {'message': f"Deleted {filename}"})
            return jsonify({"message": f"File '{filename}' deleted."}), 200
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/faqs', methods=['GET', 'POST'])
def manage_faqs():
    if request.method == 'POST':
        data = request.json
        new_faq = FAQ(question=data['question'], answer=data['answer'], category=data['category'], language=data['language'])
        db.session.add(new_faq)
        db.session.commit()
        return jsonify({"id": new_faq.id, "message": "FAQ created"}), 201
    faqs = db.session.execute(db.select(FAQ)).scalars().all()
    return jsonify([{"id": f.id, "question": f.question, "answer": f.answer, "category": f.category, "language": f.language} for f in faqs])

@app.route('/api/faqs/<int:faq_id>', methods=['PUT', 'DELETE'])
def manage_single_faq(faq_id):
    faq = db.get_or_404(FAQ, faq_id)
    if request.method == 'PUT':
        data = request.json
        faq.question = data.get('question', faq.question)
        faq.answer = data.get('answer', faq.answer)
        faq.category = data.get('category', faq.category)
        faq.language = data.get('language', faq.language)
        db.session.commit()
        return jsonify({"id": faq.id, "message": "FAQ updated"})
    if request.method == 'DELETE':
        db.session.delete(faq)
        db.session.commit()
        return jsonify({"message": "FAQ deleted"})

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    try:
        all_convos = db.session.execute(db.select(Conversation).order_by(desc(Conversation.timestamp))).scalars().all()
        results = [{"id": c.id, "session_id": c.session_id, "query": c.query, "response": c.response, "timestamp": c.timestamp.isoformat()} for c in all_convos]
        return jsonify({"conversations": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/config', methods=['GET', 'POST'])
def manage_bot_config():
    config_entry = db.session.execute(db.select(BotConfig)).scalar_one_or_none()
    if not config_entry:
        config_entry = BotConfig()
        db.session.add(config_entry)
        db.session.commit()
    if request.method == 'POST':
        data = request.json
        config_entry.enable_website = data.get('enable_website', config_entry.enable_website)
        config_entry.enable_whatsapp = data.get('enable_whatsapp', config_entry.enable_whatsapp)
        config_entry.enable_telegram = data.get('enable_telegram', config_entry.enable_telegram)
        config_entry.fallback_message = data.get('fallback_message', config_entry.fallback_message)
        db.session.commit()
        return jsonify({"message": "Config updated successfully"})
    return jsonify({
        "enable_website": config_entry.enable_website,
        "enable_whatsapp": config_entry.enable_whatsapp,
        "enable_telegram": config_entry.enable_telegram,
        "fallback_message": config_entry.fallback_message,
    })

@app.route('/api/embed-code', methods=['GET'])
def get_embed_code():
    return jsonify({"code": f'<script src="{request.url_root}widget.js" defer></script>'})

@app.route('/widget.js')
def serve_widget():
    return send_from_directory(app.static_folder, 'widget.js')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5001)
