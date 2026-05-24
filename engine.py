import json
from query_processor import QueryProcessor
from retrieval import CampusRetriever
from prompts import RAG_SYSTEM_PROMPT, get_final_prompt
from langchain_google_genai import ChatGoogleGenerativeAI

class CampusBot:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.1)
        self.processor = QueryProcessor()
        self.retriever = CampusRetriever()
        self.history = []
        self.retriever.build_index()

    def chat(self, user_input):
        p = self.processor.process_query(user_input, self.history)
        if not p["safe"]: return {"answer": "Inappropriate input.", "inap": True}
        if p["new_topic"]: self.history = []

        context = self.retriever.get_fused_context(p["queries"])
        final_prompt = get_final_prompt(user_input, context)
        raw_res = self.llm.invoke([("system", RAG_SYSTEM_PROMPT), ("human", final_prompt)]).content
        
        try:
            clean_json = raw_res.replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
            self.history.append(f"User: {user_input}")
            return data
        except:
            return {"answer": "Error parsing response.", "inap": False}

if __name__ == "__main__":
    bot = CampusBot()
    while True:
        u = input("\nYou: ")
        if u.lower() == "exit": break
        res = bot.chat(u)
        print(f"Bot: {res.get('answer')} (Source: {res.get('source_file')})")