# Language Agnostic Bot

An advanced, multilingual, omnichannel chatbot solution designed to streamline campus communication. This system leverages Retrieval-Augmented Generation (RAG) to automate responses to routine queries (fees, deadlines, forms) across multiple languages and platforms, while providing a powerful dashboard for administrators.

## 🚀 Features

### For Students (User Facing)
- **Multilingual Support**: Communicate in all 22 Constitutional languages of India via text or voice.
- **Omnichannel Access**: Accessible via a Website widget, WhatsApp, and Telegram.
- **Context-Aware**: Maintains conversation context across multiple turns for natural interaction.
- **Voice Capabilities**: Integrated Speech-to-Text (STT) and Text-to-Speech (TTS) for seamless voice queries.
- **Smart Fallback**: Automatically escalates queries to human support tickets when confidence is low.

### For Administrators (Dashboard)
- **Knowledge Base Management**: Drag-and-drop interface to ingest PDFs, circulars, and notices instantly.
- **Analytics Dashboard**: Real-time insights on conversation volume, language distribution, and unanswered questions.
- **Ticket Management**: View, track, and resolve escalated student queries.
- **FAQ Generation**: Automatically generates FAQs from clustered user queries and usage trends.
- **Privacy Focused**: IP addresses are hashed (BLAKE-3) to ensure student anonymity; only session IDs are stored.

## 🏗️ Architecture & Tech Stack

The system allows for flexible deployment, supporting both cloud-based LLMs (Gemini/GPT) and local privacy-first models (LLaMA).

### Core Components
- **Backend Framework**: Python (Flask)
- **Database**: MongoDB Atlas (for conversation logs and ticketing)
- **Vector Store**: Optimized for semantic search and retrieval
- **OCR Engine**: Tesseract OCR (extracts text from scanned documents/images)

### AI & NLP Pipeline
- **RAG Framework**: Custom pipeline with query rewriting, knowledge refinement, and multi-query generation.
- **Embeddings**: Paraphrase Multilingual MiniLM L12 V2 (384-dim).
- **Translation**: IndicTrans2 (AI4Bharat) for high-accuracy regional translation.
- **Voice Services**: Sarvam AI for Indian language STT and TTS.

### Integrations
- **Messaging**: Twilio API (WhatsApp), Telegram Bot API.
- **Deployment**: Embeddable JavaScript tag for website integration.

## 🛠️ Prerequisites

Before running the project, ensure you have the following installed:
- Python 3.8+
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (must be added to system PATH)
- FFmpeg (for audio processing)
- MongoDB Account

## 📥 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/neural-nomads-bot.git
   cd neural-nomads-bot
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## ⚙️ Configuration

1. Create a `.env` file in the root directory.
2. Add the following configuration keys:

   ```env
   # LLM Providers
   GOOGLE_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_key (optional)

   # Database
   MONGO_URI=your_mongodb_connection_string

   # Integrations
   TWILIO_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TELEGRAM_BOT_TOKEN=your_telegram_token

   # Voice Services
   SARVAM_API_KEY=your_sarvam_key
   ```

## 🚀 Usage

### Starting the Application
1. **Run the Ingestion Script** (if new documents are added):
   ```bash
   python ingest_docs.py
   ```
2. **Start the Flask Server**:
   ```bash
   python app.py
   ```

### Accessing the Dashboard
- Open your browser and navigate to `http://localhost:5000/admin` (or your configured port).
- Use the dashboard to upload new PDFs or view analytics.

### Embedding the Chatbot
Add the generated script tag to your website's `<body>`:
```html
<script src="http://localhost:5000/static/chat-widget.js"></script>
```

## 🐛 Common Troubleshooting

| Error | Possible Cause | Solution |
|-------|----------------|----------|
| `ModuleNotFoundError` | Virtual env not active | Run `source venv/bin/activate` and reinstall requirements. |
| `DefaultCredentialsError` | Missing API Key | Check `.env` file for `GOOGLE_API_KEY`. |
| `TesseractNotFoundError` | Tesseract not installed | Install Tesseract and ensure it is in your system PATH. |# campus-assistant
# campus-assistant
# campus-assistant
# campus-assistant
