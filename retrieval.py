import os
import pickle
from dotenv import load_dotenv

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

class CampusRetriever:
    def __init__(self):
        # Synchronized model string to match ingest.py configuration
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vector_db = None
        self.bm25 = None

    def build_index(self, folder="data", db_folder="db"):
        faiss_path = db_folder
        bm25_path = os.path.join(db_folder, "bm25.pkl")

        # --- 1. LOCAL CACHE CHECK ---
        if os.path.exists(faiss_path) and os.path.exists(bm25_path):
            print(f"🔄 Found local database cache in '{db_folder}'. Loading indices...")
            self.vector_db = FAISS.load_local(
                faiss_path, 
                self.embeddings, 
                allow_dangerous_deserialization=True
            )
            with open(bm25_path, "rb") as f:
                self.bm25 = pickle.load(f)
            print("✅ Both FAISS and BM25 loaded from disk. 0 API calls used!")
        else:
            # Prevent accidental fallback generation
            raise FileNotFoundError(
                f"❌ Local database files missing in '{db_folder}'. Please run 'python ingest.py' first!"
            )

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
    try:
        ret.build_index()
        print("\n--- Testing Retrieval ---")
        print(ret.get_fused_context(["attendance"]))
    except Exception as e:
        print(e)