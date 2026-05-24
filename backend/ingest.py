import os
import glob
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import chromadb
from utils import extract_text

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

# --- PATH CORRECTION ---
# Get the absolute path of the directory where this script is located (backend/)
basedir = os.path.abspath(os.path.dirname(__file__))

# Define paths relative to the project root
ROOT_DIR = os.path.join(basedir, '..')
CHROMA_PATH = os.path.join(ROOT_DIR, "db")
DATA_PATH = os.path.join(ROOT_DIR, "data")
# ---------------------

# Initialize ChromaDB Client
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("campus_docs")

def ingest():
    """
    Processes all documents in the root 'data' folder and stores their
    vector embeddings in the root 'db' folder.
    """
    # Use the corrected path to find documents
    doc_files = glob.glob(os.path.join(DATA_PATH, "*.*"))

    for doc_path in doc_files:
        doc_id = os.path.basename(doc_path)

        # Use the more reliable 'where' filter to check for existing documents
        if collection.get(where={"source": doc_id}).get("ids"):
            print(f"[*] Document '{doc_id}' already ingested. Skipping.")
            continue

        print(f"[+] Processing '{doc_id}'...")
        text = extract_text(doc_path)
        if not text:
            print(f"[!] Could not extract text from {doc_path}. Skipping.")
            continue

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = splitter.split_text(text)
        
        if not chunks:
            print(f"[!] No text chunks generated for {doc_path}. Skipping.")
            continue

        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=API_KEY)
        
        batch_size = 100
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i + batch_size]
            ids = [f"{doc_id}_{i+j}" for j in range(len(batch_chunks))]
            
            try:
                vectors = embeddings.embed_documents(batch_chunks)
                collection.add(
                    ids=ids,
                    documents=batch_chunks,
                    embeddings=vectors,
                    metadatas=[{"source": doc_id}] * len(batch_chunks)
                )
                print(f"  - Ingested batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
            
            except Exception as e:
                print(f"[!!] Error processing batch for {doc_id}: {e}")

if __name__ == "__main__":
    ingest()