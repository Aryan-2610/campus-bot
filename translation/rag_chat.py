import os
import re
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import chromadb
from langchain.prompts import ChatPromptTemplate

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", google_api_key=API_KEY)

# Initialize DB
CHROMA_PATH = "db"
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_collection("campus_docs")

# Small talk responses
SMALL_TALK = {
    "hi": "Hello! How can I help you today?",
    "hello": "Hi there 👋 How can I assist?",
    "bye": "Goodbye! Have a great day 🎓",
}

# Store conversation history
conversation_history = []

# Strict system prompt
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
"""

# Prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{history}\nUser: {query}\nAssistant:")
])

# Helper to safely extract JSON from model output
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass
    # Fallback if parsing fails
    return {
        "intent": "query",
        "fallback": 1.0,
        "msg": "Sorry, I could not process this request correctly.",
        "doc": None,
        "page": None
    }

# Retrieve context
def retrieve_context(query, k=3):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=API_KEY
    )
    query_vector = embeddings.embed_query(query)
    results = collection.query(query_embeddings=[query_vector], n_results=k)
    return results

# Chat function
def chat(query):
    global conversation_history

    # Handle small talk
    if query.lower().strip() in SMALL_TALK:
        return {
            "intent": "greeting" if query.lower().strip() in ["hi", "hello"] else "ending",
            "fallback": 0.0,
            "msg": SMALL_TALK[query.lower().strip()],
            "doc": None,
            "page": None
        }

    # Retrieve context
    results = retrieve_context(query)
    docs = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0] if results.get("metadatas") else []

    # Extract doc + page safely
    doc_name = None
    page_num = None
    if isinstance(metadatas, dict):
        doc_name = metadatas.get("source")
        page_num = metadatas.get("page")
    elif isinstance(metadatas, list) and metadatas:
        doc_name = metadatas[0].get("source")
        page_num = metadatas[0].get("page")

    context = "\n".join(docs) if docs else ""

    # Build conversation history
    history_text = ""
    for role, msg in conversation_history[-6:]:
        history_text += f"{role.capitalize()}: {msg}\n"

    # Final prompt
    prompt = prompt_template.format(
        history=history_text + ("\n" + context if context else ""),
        query=query
    )

    # Call LLM
    response = llm.invoke(prompt).content

    # Debug: raw model output
    print("=== RAW MODEL RESPONSE ===")
    print(response)
    print("==========================")

    # Parse into JSON
    data = extract_json(response)

    # Attach doc + page if missing
    if not data.get("doc") and doc_name:
        data["doc"] = doc_name
    if not data.get("page") and page_num:
        data["page"] = page_num

    # Update history
    conversation_history.append(("user", query))
    conversation_history.append(("assistant", data["msg"]))

    return data

# Run loop
if __name__ == "__main__":
    while True:
        query = input("User: ")
        if query.lower() in ["quit", "exit"]:
            break
        print("Bot:", chat(query))
