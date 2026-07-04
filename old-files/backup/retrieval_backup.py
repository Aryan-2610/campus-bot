import os
import time
import pickle
import pdfplumber
from dotenv import load_dotenv

# Native Google GenAI SDK (Bypasses LangChain's concurrent wrappers)
from google import genai
from google.genai import types

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

load_dotenv()

class CampusRetriever:
    def __init__(self):
        # We keep this helper just for FAISS local loading reconstruction later
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        
        # Initialize the raw official Google Client using your GEMINI_API_KEY env variable
        self.client = genai.Client()
        self.vector_db = None
        self.bm25 = None

    def build_index(self, folder="data", db_folder="db"):
        faiss_path = db_folder
        bm25_path = os.path.join(db_folder, "bm25.pkl")

        # --- 1. LOCAL CACHE CHECK ---
        if os.path.exists(faiss_path) and os.path.exists(bm25_path):
            print(f"🔄 Found local database cache in '{db_folder}'. Loading...")
            self.vector_db = FAISS.load_local(
                faiss_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            with open(bm25_path, "rb") as f:
                self.bm25 = pickle.load(f)
            print("✅ Both FAISS and BM25 loaded from disk. 0 API calls used!")
            return

        # --- 2. GENERATE DOCUMENT CHUNKS ---
        print(f"✨ Local cache missing. Processing source PDFs from '{folder}'...")
        if not os.path.exists(folder): 
            print(f"Error: {folder} not found")
            return
        
        docs = []
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                path = os.path.join(folder, file)
                with pdfplumber.open(path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text: 
                            full_text += page_text + "\n"
                docs.append(Document(page_content=full_text, metadata={"source": file}))

        if not docs:
            print("❌ No PDF files found in data/ folder.")
            return

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        print(f"Total structural chunks generated: {len(chunks)}.")

        # --- 3. SEVERELY THROTTLED NATIVE EMBEDDING GENERATION ---
        print("Starting synchronous raw native embedding generation loop...")
        
        text_embeddings_pairs = []
        metadatas = []

        for idx, chunk in enumerate(chunks, start=1):
            print(f"Embedding chunk {idx}/{len(chunks)} via raw SDK...")
            
            # Direct API request using the native SDK client
            response = self.client.models.embed_content(
                model="text-embedding-004", # Using Google's premier optimized embedding model
                contents=chunk.page_content
            )
            
            # Extract raw vector list
            raw_vector = response.embeddings[0].values
            
            text_embeddings_pairs.append((chunk.page_content, raw_vector))
            metadatas.append(chunk.metadata)
            
            # Force a strict 1.5-second sleep to completely break the 100 RPM ceiling
            time.sleep(1.5)

        # Seeding directly into FAISS from pre-computed text-embedding lists completely locally
        print("Feeding raw vector coordinates into local FAISS index...")
        self.vector_db = FAISS.from_embeddings(
            text_embeddings_pairs, 
            self.embeddings, 
            metadatas=metadatas
        )

        # Build BM25 locally
        print("Building local BM25 index...")
        self.bm25 = BM25Retriever.from_documents(chunks)
        
        # --- 4. CACHE EVERYTHING TO DISK ---
        print(f"Saving indices to '{db_folder}'...")
        os.makedirs(db_folder, exist_ok=True)
        self.vector_db.save_local(faiss_path)
        with open(bm25_path, "wb") as f:
            pickle.dump(self.bm25, f)
            
        print(f"✅ Cache generated successfully! Saved {len(chunks)} chunks locally.")

    def get_fused_context(self, queries):
        if not self.vector_db or not self.bm25:
            return "Error: Index not built or loaded."

        v_docs, k_docs = [], []
        for q in queries:
            v_docs.extend(self.vector_db.as_retriever(search_kwargs={"k": 5}).invoke(q))
            k_docs.extend(self.bm25.invoke(q))

        scores = {}
        for rank, doc in enumerate(v_docs):
            scores[doc.page_content] = scores.get(doc.page_content, 0) + 0.7 * (1 / (60 + rank + 1))
        for rank, doc in enumerate(k_docs):
            scores[doc.page_content] = scores.get(doc.page_content, 0) + 0.3 * (1 / (60 + rank + 1))

        top_chunks = sorted(scores, key=scores.get, reverse=True)[:5]
        
        context_str = ""
        for content in top_chunks:
            source = next((d.metadata['source'] for d in v_docs + k_docs if d.page_content == content), "unknown")
            context_str += f"[{source}]: {content}\n\n"
        return context_str

if __name__ == "__main__":
    ret = CampusRetriever()
    ret.build_index()
    