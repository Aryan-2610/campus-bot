import os
import re
import json
import uuid
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import chromadb
from langchain.prompts import ChatPromptTemplate
import nest_asyncio
from flask import current_app
from models import db, Ticket
from datetime import datetime

# Safeguard for async libraries in threads
nest_asyncio.apply()

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize AI models with error handling
print("Initializing AI models...")
try:
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=API_KEY)
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
    print("AI models initialized successfully.")
except Exception as e:
    print(f"!!! CRITICAL ERROR initializing AI models: {e}")
    llm = None
    embeddings = None

# Initialize ChromaDB vector store
CHROMA_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', "db")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("campus_docs")

# Pre-defined responses for simple small talk
SMALL_TALK = {
    "hi": "Hello! How can I help you today?",
    "hello": "Hi there 👋 How can I assist?",
    "bye": "Goodbye! Have a great day 🎓",
}

# --- State Management ---
# Global variables to hold conversation state
conversation_history = []
awaiting_ticket_confirmation = False

# System prompt to instruct the language model
SYSTEM_PROMPT = """
You are a campus administration assistant.
Always respond ONLY in valid JSON format.
Do not include explanations, markdown, or text outside the JSON.

The JSON must have these keys:
- intent: one of ["greeting", "ending", "query", "inap_language"]
- fallback: a float between 0.0 and 1.0
- msg: a natural language assistant reply
- doc: string filename if available, else null
- page: integer if available, else null

Rules:
- For greetings (hi, hello), intent = "greeting"
- For goodbyes (bye), intent = "ending"
- For abusive or inappropriate queries, intent = "inap_language"
- Otherwise, intent = "query"
- fallback ≥ 0.7 only if the information is not available in official notices
- Try to answer as far as possible, minimize escalations
- msg should sound like you already know the policy
- If fallback is 0.7 or higher, the msg should ask the user to raise a ticket (Yes/No).
"""

# Template for structuring the final prompt to the LLM
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{history}\nUser: {query}\nAssistant:")
])

def extract_json(text):
    """Safely extracts a JSON object from a string, with a fallback."""
    try:
        # Use regex to find a string that starts with { and ends with }
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except (json.JSONDecodeError, TypeError):
        # Handle cases where parsing fails or input is not a string
        pass
    # Return a default error structure if JSON extraction fails
    return {
        "intent": "query",
        "fallback": 1.0,
        "msg": "Sorry, I could not process this request correctly.",
        "doc": None,
        "page": None
    }

def retrieve_context(query, k=3):
    """Retrieves relevant document chunks from ChromaDB based on the query."""
    if not embeddings:
        return {}
    query_vector = embeddings.embed_query(query)
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    return results

def raise_ticket(user_query):
    """Creates a new support ticket and saves it to the database."""
    try:
        ticket_id = str(uuid.uuid4())
        new_ticket = Ticket(
            ticket_id=ticket_id, 
            query=user_query, 
            status='open', 
            created_at=datetime.utcnow()
        )
        db.session.add(new_ticket)
        db.session.commit()
        print(f"✓ TICKET CREATED: {ticket_id} for query: '{user_query}'")
        return (
            f"Your request has been submitted successfully. The ticket ID is: {ticket_id}. "
            "Our support team will review your query and get back to you shortly."
        )
    except Exception as e:
        db.session.rollback()
        print(f"✗ ERROR creating ticket: {e}")
        return "Sorry, I am having trouble creating a ticket at the moment. Please try again later."

def chat(query):
    """Main function to handle user queries and generate bot responses."""
    global conversation_history, awaiting_ticket_confirmation

    # --- State 1: Awaiting 'Yes'/'No' for ticket creation ---
    if awaiting_ticket_confirmation:
        user_response = query.lower().strip()
        if user_response == "yes":
            # Retrieve the query that triggered the ticket flow
            previous_query = conversation_history[-2][1] if len(conversation_history) >= 2 else "N/A"
            response_msg = raise_ticket(previous_query)
            awaiting_ticket_confirmation = False
        elif user_response == "no":
            response_msg = "Alright. If you have any other questions, feel free to ask."
            awaiting_ticket_confirmation = False
        else:
            response_msg = "I didn't understand that. Please respond with 'Yes' or 'No' to proceed."
        
        conversation_history.extend([("user", query), ("assistant", response_msg)])
        return response_msg

    # --- State 2: Handling simple small talk ---
    if query.lower().strip() in SMALL_TALK:
        response_msg = SMALL_TALK[query.lower().strip()]
        conversation_history.extend([("user", query), ("assistant", response_msg)])
        return response_msg

    # --- State 3: Main RAG and LLM processing ---
    # Retrieve context from ChromaDB
    results = retrieve_context(query)
    raw_docs = results.get("documents", [[]])
    docs = []
    # Flatten the list of documents
    for doc_list in raw_docs:
        if isinstance(doc_list, list):
            docs.extend(doc_list)
        elif isinstance(doc_list, str):
            docs.append(doc_list)
    context = "\n".join(docs) if docs else ""

    # --- ADDED: Build conversation history context ---
    # This formats the last 6 messages to provide context to the LLM
    history = ""
    for role, msg in conversation_history[-6:]:
        history += f"{role.capitalize()}: {msg}\n"
    # --- END OF ADDED SECTION ---

    # Format the final prompt with history, context, and the new query
    prompt = prompt_template.format(history=history + ("\n" + context if context else ""), query=query)

    try:
        # Invoke the LLM and extract the JSON response
        raw_output = llm.invoke(prompt).content
        data = extract_json(raw_output)
    except Exception as e:
        print(f"✗ LLM Invocation Error: {e}")
        data = {
            "intent": "query",
            "fallback": 1.0,
            "msg": "Sorry, I am unable to connect to the assistant at the moment."
        }

    # If fallback is high, initiate the ticket creation flow
    if data.get("fallback", 0.0) >= 0.7:
        awaiting_ticket_confirmation = True
        data["msg"] = (
            "I am sorry, but the information you are looking for is not in my database. "
            "Would you like to raise a ticket for this issue? Please respond with 'Yes' or 'No'."
        )

    # Update conversation history with the latest exchange
    conversation_history.extend([("user", query), ("assistant", data["msg"])])
    return data["msg"]

if __name__ == "__main__":
    # Simple command-line interface for testing
    print("Starting bot... Type 'quit' or 'exit' to stop.")
    while True:
        user_query = input("User: ")
        if user_query.lower() in ("quit", "exit"):
            break
        bot_response = chat(user_query)
        print("Bot:", bot_response)