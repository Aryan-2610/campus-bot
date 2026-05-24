import os
import pdfplumber
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from dotenv import load_dotenv
import pickle
from sys import exit 
from google.api_core.exceptions import ResourceExhausted
from tenacity import retry, stop_after_attempt, wait_exponential

import time  ## as free tier api restricts >100 embeddings/min

load_dotenv()
class CampusRetriever:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vector_db = None
        self.bm25 = None

    """
    USE IF PAID API AS NO RATE LIMITING ISSUE
    def build_index(self, folder="data"):
        if not os.path.exists(folder): return print(f"Error: {folder} not found")
        
        docs = []
        for file in os.listdir(folder):
            time.sleep(1)
            if file.endswith(".pdf"):
                path = os.path.join(folder, file)
                ## Using pdfplumber for visual layout preservation (better for tables)
                with pdfplumber.open(path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        time.sleep(1)
                        page_text = page.extract_text()
                        if page_text: full_text += page_text + "\n"
                
                docs.append(Document(page_content=full_text, metadata={"source": file}))

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        
        self.vector_db = FAISS.from_documents(chunks, self.embeddings)
        self.bm25 = BM25Retriever.from_documents(chunks)
        print(f"Index built with {len(chunks)} structural chunks.")
     """
    def build_index(self, folder="data", db_folder="db"):
        faiss_path = db_folder
        bm25_path = os.path.join(db_folder, "bm25.pkl")

        # --- 1. IF DB FOLDER EXISTS: Load both FAISS and BM25 instantly ---
        if os.path.exists(faiss_path) and os.path.exists(bm25_path):
            print(f"🔄 Found local database. Loading indices...")
            
            # Load FAISS
            self.vector_db = FAISS.load_local(
                faiss_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            
            # Load BM25 from the pickle file
            with open(bm25_path, "rb") as f:
                self.bm25 = pickle.load(f)
                
            print("✅ Both FAISS and BM25 loaded from disk. 0 API calls used!")
            return

        # --- 2. IF DB FOLDER IS MISSING: Build from scratch ---
        print(f"✨ Local indices missing. Building fresh index from '{folder}'...")
        if not os.path.exists(folder): 
            return print(f"Error: {folder} not found")
        
        docs = []
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                path = os.path.join(folder, file)
                with pdfplumber.open(path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text: full_text += page_text + "\n"
                docs.append(Document(page_content=full_text, metadata={"source": file}))

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        
        # Build both indices in memory
        self.vector_db = FAISS.from_documents(chunks, self.embeddings)
        self.bm25 = BM25Retriever.from_documents(chunks)
        
        # --- 3. SAVE BOTH TO DISK ---
        print(f"Saving indices to '{db_folder}' for fast future loading...")
        os.makedirs(db_folder, exist_ok=True)
        
        # Save FAISS
        self.vector_db.save_local(faiss_path)
        
        # Save BM25 using pickle
        with open(bm25_path, "wb") as f:
            pickle.dump(self.bm25, f)
            
        print(f"✅ Setup complete! Saved {len(chunks)} structural chunks.")
        faiss_path = db_folder
        bm25_path = os.path.join(db_folder, "bm25.pkl")

        # --- 1. IF DB FOLDER EXISTS: Load both FAISS and BM25 instantly ---
        if os.path.exists(faiss_path) and os.path.exists(bm25_path):
            print(f"🔄 Found local database. Loading indices...")
            
            # Load FAISS
            self.vector_db = FAISS.load_local(
                faiss_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            
            # Load BM25 from the pickle file
            with open(bm25_path, "rb") as f:
                self.bm25 = pickle.load(f)
                
            print("✅ Both FAISS and BM25 loaded from disk. 0 API calls used!")
            return

        # --- 2. IF DB FOLDER IS MISSING: Build from scratch ---
        print(f"✨ Local indices missing. Building fresh index from '{folder}'...")
        if not os.path.exists(folder): 
            return print(f"Error: {folder} not found")
        
        docs = []
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                path = os.path.join(folder, file)
                with pdfplumber.open(path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text: full_text += page_text + "\n"
                docs.append(Document(page_content=full_text, metadata={"source": file}))

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        
        # Build both indices in memory
        self.vector_db = FAISS.from_documents(chunks, self.embeddings)
        self.bm25 = BM25Retriever.from_documents(chunks)
        
        # --- 3. SAVE BOTH TO DISK ---
        print(f"Saving indices to '{db_folder}' for fast future loading...")
        os.makedirs(db_folder, exist_ok=True)
        
        # Save FAISS
        self.vector_db.save_local(faiss_path)
        
        # Save BM25 using pickle
        with open(bm25_path, "wb") as f:
            pickle.dump(self.bm25, f)
            
        print(f"✅ Setup complete! Saved {len(chunks)} structural chunks.")
        if not os.path.exists(folder): 
            return print(f"Error: {folder} not found")
        
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

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        
        print(f"Total chunks generated: {len(chunks)}.")
        
        # --- ROBUST RETRY WRAPPERS ---
        # This decorator tells the function to retry if a ResourceExhausted (429) exception occurs
        @retry(
            wait=wait_exponential(multiplier=2, min=4, max=60), 
            stop=stop_after_attempt(5),
            reraise=True
        )
        def safe_init_faiss(initial_chunks):
            return FAISS.from_documents(initial_chunks, self.embeddings)

        @retry(
            wait=wait_exponential(multiplier=2, min=4, max=60), 
            stop=stop_after_attempt(5),
            reraise=True
        )
        def safe_add_chunks(db, chunk_batch):
            db.add_documents(chunk_batch)

        # --- BATCHED EXECUTION ---
        batch_size = 3  # Dropped to a highly conservative batch size for safety
        delay_seconds = 5  # 5 seconds between successful batches
        
        print("Initializing FAISS with the first batch...")
        try:
            first_batch = chunks[:batch_size]
            self.vector_db = safe_init_faiss(first_batch)
            
            for i in range(batch_size, len(chunks), batch_size):
                print(f"Processing chunks {i} to {min(i + batch_size, len(chunks))}...")
                time.sleep(delay_seconds)
                
                batch = chunks[i : i + batch_size]
                safe_add_chunks(self.vector_db, batch)
                
        except Exception as e:
            print(f"\n❌ Failed to build index due to persistent API limits:\n{e}")
            return

        # BM25 is purely local math, no API calls needed here
        self.bm25 = BM25Retriever.from_documents(chunks)
        print(f"\n✅ Index successfully built with {len(chunks)} chunks!")
        if not os.path.exists(folder): 
            return print(f"Error: {folder} not found")
        
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

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        
        # --- FIX FOR RATE LIMITS: BATCHED EMBEDDINGS ---
        print(f"Total chunks generated: {len(chunks)}. Initializing FAISS in batches...")
        
        # 1. Initialize FAISS with just the first small batch
        batch_size = 5  # Safe number of embeddings per API call
        delay_seconds = 4  # Wait time between batches
        
        first_batch = chunks[:batch_size]
        self.vector_db = FAISS.from_documents(first_batch, self.embeddings)
        
        # 2. Add the remaining chunks incrementally with a pause
        for i in range(batch_size, len(chunks), batch_size):
            print(f"Processing chunks {i} to {min(i + batch_size, len(chunks))}...")
            time.sleep(delay_seconds)  # Give the API cooling-off time
            
            batch = chunks[i : i + batch_size]
            self.vector_db.add_documents(batch)
        
        # BM25 is purely mathematical and runs locally; no API rate limits apply here.
        self.bm25 = BM25Retriever.from_documents(chunks)
        print(f"Successfully built index with {len(chunks)} structural chunks.")
    def get_fused_context(self, queries):
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
            source = next(d.metadata['source'] for d in v_docs + k_docs if d.page_content == content)
            context_str += f"[{source}]: {content}\n\n"
        return context_str

if __name__ == "__main__":
    ret = CampusRetriever()
    ret.build_index()
    print(ret.get_fused_context(["exam schedule"]))