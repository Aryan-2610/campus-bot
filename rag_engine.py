import os
import sys
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from retrieval import CampusRetriever
from prompts import RAG_SYSTEM_PROMPT
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
load_dotenv()

class CampusRAGEngine:
    def __init__(self):
        print("🤖 Initializing CampusRAGEngine...")
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.1)
        
       
        self.retriever = CampusRetriever()
        
        # Load indices from disk safely
        try:
            self.retriever.build_index()
        except FileNotFoundError as e:
            print(f"\n{e}\n")
         
            print(" ACTION REQUIRED: Please run the ingestion script first:")
            print("   python ingest.py")
            sys.exit(1)

    def get_response(self, query):
        import json

        #  Fetch the context using  hybrid search
        context = self.retriever.get_fused_context([query])
        
        if "Error: Index not loaded" in context:
            return "Database index not ready."

        # Build a structured message format for the LLM
        user_prompt = f"Question: {query}\n\nContext:\n{context}"
        
        # Pass the system prompt as a system message instruct
        messages = [
            ("system", RAG_SYSTEM_PROMPT),
            ("human", user_prompt)
        ]
        
        raw_res = self.llm.invoke(messages).content
        
        #  Clean and parse the JSON string safely
        try:
            clean_json = raw_res.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            
            # Extract just the plain string answer for your UI engine loop
            return data.get("answer", "No answer field found.")
        except Exception as e:
            print(f"JSON Parsing Error: {e} | Raw Output: {raw_res}")
            return "Error parsing response into a clean format."

if __name__ == "__main__":
    engine = CampusRAGEngine()
    
    user_query = "who is dean of dtu"

    print(f"\nUser: {user_query}")
    print(f"Bot: {engine.get_response(user_query)}")