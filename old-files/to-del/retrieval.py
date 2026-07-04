import os
import pdfplumber
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter 
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()
class CampusRetriever:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
        self.vector_db = None
        self.bm25 = None

    def build_index(self, folder="data"):
        if not os.path.exists(folder): return print(f"Error: {folder} not found")
        
        docs = []
        for file in os.listdir(folder):
            if file.endswith(".pdf"):
                path = os.path.join(folder, file)
                ## Using pdfplumber for visual layout preservation (better for tables)
                with pdfplumber.open(path) as pdf:
                    full_text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text: full_text += page_text + "\n"
                
                docs.append(Document(page_content=full_text, metadata={"source": file}))

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(docs)
        
        self.vector_db = FAISS.from_documents(chunks, self.embeddings)
        self.bm25 = BM25Retriever.from_documents(chunks)
        print(f"Index built with {len(chunks)} structural chunks.")

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