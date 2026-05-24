import os
import time
import pickle
import pdfplumber
from dotenv import load_dotenv

from google import genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

load_dotenv()

def run_ingestion(folder="data", db_folder="db"):
    faiss_path = db_folder
    bm25_path = os.path.join(db_folder, "bm25.pkl")
    
    print(f"🧹 Clearing old database files...")
    if os.path.exists(bm25_path): os.remove(bm25_path)
    
    print(f"✨ Processing source PDFs from '{folder}'...")
    if not os.path.exists(folder):
        return print(f"Error: {folder} not found")
        
    docs = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            with pdfplumber.open(path) as pdf:
                full_text = "".join([page.extract_text() or "" for page in pdf.pages])
            docs.append(Document(page_content=full_text, metadata={"source": file}))

    if not docs:
        return print("❌ No PDF files found in data/ folder.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Generated {len(chunks)} text chunks. Starting sequential API embedding generation...")

    # Initialize raw SDK client
    client = genai.Client()
    text_embeddings_pairs = []
    metadatas = []

    for idx, chunk in enumerate(chunks, start=1):
        print(f"🚀 Embedding chunk {idx}/{len(chunks)}...")
        
        # Raw API call (no hidden LangChain concurrency)
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=chunk.page_content
        )
        
        raw_vector = response.embeddings[0].values
        text_embeddings_pairs.append((chunk.page_content, raw_vector))
        metadatas.append(chunk.metadata)
        
        # Hard 2-second sleep to completely respect the free tier rate limits
        time.sleep(2.0)

    print("🧠 Packing coordinates into local FAISS index...")
    dummy_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vector_db = FAISS.from_embeddings(text_embeddings_pairs, dummy_embeddings, metadatas=metadatas)

    print("📚 Building local BM25 keyword index...")
    bm25 = BM25Retriever.from_documents(chunks)

    print(f"💾 Saving local database to '{db_folder}'...")
    os.makedirs(db_folder, exist_ok=True)
    vector_db.save_local(faiss_path)
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25, f)
        
    print(" Ingestion successfully completed! Local cache is fully built.")

if __name__ == "__main__":
    run_ingestion()