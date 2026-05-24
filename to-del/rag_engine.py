import os
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

load_dotenv()

class CampusRAGEngine:
    def __init__(self):
        ## Initializing models using the specific names provided
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.1)
        self.vector_db = None
        self.bm25 = None

    def load_documents(self, folder="campus-assistant/data"):
        if not os.path.exists(folder):
            return print(f"Folder {folder} not found")

        docs = []
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                path = os.path.join(folder, file)
                reader = PdfReader(path)
                text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])
                docs.append(Document(page_content=text, metadata={"source": file}))

        if not docs: return print("No PDFs found")

        ## Splitting text into manageable chunks
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)

        ## Creating the dual-index system
        self.vector_db = FAISS.from_documents(chunks, self.embeddings)
        self.bm25 = BM25Retriever.from_documents(chunks)
        print(f"Indexed {len(chunks)} chunks successfully")

    def _rrf_score(self, vector_docs, keyword_docs):
        ## Reciprocal Rank Fusion to combine semantic and keyword results
        scores = {}
        for rank, doc in enumerate(vector_docs):
            scores[doc.page_content] = scores.get(doc.page_content, 0) + 0.7 * (1 / (60 + rank + 1))
        
        for rank, doc in enumerate(keyword_docs):
            scores[doc.page_content] = scores.get(doc.page_content, 0) + 0.3 * (1 / (60 + rank + 1))

        ## Sorting results and pulling the best unique chunks
        top_contents = sorted(scores, key=scores.get, reverse=True)[:5]
        all_docs = vector_docs + keyword_docs
        return [next(d for d in all_docs if d.page_content == c) for c in top_contents]

    def get_response(self, query):
        if not self.vector_db: return "Load documents first"

        ## Fixed: Using .invoke() to avoid AttributeError
        v_docs = self.vector_db.as_retriever(search_kwargs={"k": 10}).invoke(query)
        k_docs = self.bm25.invoke(query)

        ## Merge results and build context
        fused = self._rrf_score(v_docs, k_docs)
        context = "\n\n".join([f"Source {d.metadata['source']}: {d.page_content}" for d in fused])

        ## Simple prompt structure for generation
        prompt = f"Question: {query}\n\nContext:\n{context}\n\nAnswer:"
        return self.llm.invoke(prompt).content

if __name__ == "__main__":
    engine = CampusRAGEngine()
    engine.load_documents()
    
    user_query = "What is the attendance policy?"
    print(f"\nUser: {user_query}")
    print(f"Bot: {engine.get_response(user_query)}")