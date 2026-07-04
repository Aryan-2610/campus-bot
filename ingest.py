import os
import time
import pickle
import pdfplumber
import pytesseract
from pdf2image import convert_from_path
from dotenv import load_dotenv

from google import genai
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

load_dotenv()

def extract_text_with_ocr(pdf_path):
    """Extracts text using pdfplumber, with a fallback to Tesseract OCR for scanned pages."""
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            
            # If pdfplumber finds text, use it. Otherwise, it's likely a scanned image.
            if page_text and page_text.strip():
                full_text += page_text + "\n"
            else:
                print(f" No text found on page {i+1}, running OCR fallback...")
                images = convert_from_path(pdf_path, first_page=i+1, last_page=i+1)
                if images:
                    full_text += pytesseract.image_to_string(images[0]) + "\n"
                    
    return full_text

def run_ingestion(folder="data", db_folder="db"):
    faiss_path = db_folder
    bm25_path = os.path.join(db_folder, "bm25.pkl")
    
    print(f"Clearing old database files")
    if os.path.exists(bm25_path): os.remove(bm25_path)
    
    print(f"✨ Processing source PDFs from '{folder}'...")
    if not os.path.exists(folder):
        return print(f"❌ Error: {folder} not found")
        
    docs = []
    for file in os.listdir(folder):
        if file.endswith(".pdf"):
            path = os.path.join(folder, file)
            print(f" Reading: {file}")
            text = extract_text_with_ocr(path)
            docs.append(Document(page_content=text, metadata={"source": file}))

    if not docs:
        return print("No PDF files found in data/ folder.")

    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    print(f"Generated {len(chunks)} text chunks. Starting batched API embedding generation...")

    client = genai.Client()
    text_embeddings_pairs = []
    metadatas = []

    # Dropped batch size slightly to be gentler on the Tokens-Per-Minute (TPM) limit
    BATCH_SIZE = 50 
    
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        batch_texts = [chunk.page_content for chunk in batch]
        
        print(f" Embedding batch {i // BATCH_SIZE + 1} (Chunks {i+1} to {min(i+BATCH_SIZE, len(chunks))})...")
        
        success = False
        retries = 3 # Allow up to 3 retry attempts per batch
        
        while not success and retries > 0:
            try:
                response = client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=batch_texts
                )
                
                for j, embedding_data in enumerate(response.embeddings):
                    raw_vector = embedding_data.values
                    text_embeddings_pairs.append((batch_texts[j], raw_vector))
                    metadatas.append(batch[j].metadata)
                
                success = True # Batch succeeded, break out of the while loop
                time.sleep(3.0) # Normal throttle between successful batches
                
            except Exception as e:
                error_msg = str(e)
                # Check if it's a rate limit issue
                if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    print(f" Rate limit hit! Waiting 40 seconds to cool down before retrying...")
                    time.sleep(40.0) # Wait out the API's requested timeout
                    retries -= 1
                else:
                    print(f" Unhandled Error on batch {i // BATCH_SIZE + 1}: {e}")
                    break # Break the loop on a critical, non-rate-limit error

    if not text_embeddings_pairs:
        return print("No embeddings were generated. Exiting before overwriting database.")

    print(" Packing coordinates into local FAISS index...")
    dummy_embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
    vector_db = FAISS.from_embeddings(text_embeddings_pairs, dummy_embeddings, metadatas=metadatas)

    print("Building local BM25 keyword index...")
    bm25 = BM25Retriever.from_documents(chunks)

    print(f"Saving local database to '{db_folder}'...")
    os.makedirs(db_folder, exist_ok=True)
    vector_db.save_local(faiss_path)
    with open(bm25_path, "wb") as f:
        pickle.dump(bm25, f)
        
    print("Ingestion successfully completed! Local cache is fully built.")

if __name__ == "__main__":
    run_ingestion()