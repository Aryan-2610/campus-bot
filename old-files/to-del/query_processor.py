import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from prompts import QUERY_EXPANSION_PROMPT
from dotenv import load_dotenv

load_dotenv()

class QueryProcessor:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash")

    def process_query(self, current_query, history):
        last_msg = history[-1] if history else "None"
        check_prompt = f"Last: {last_msg}\nNew: {current_query}\nReply 'INAP', 'NEW', or 'OK'."
        status = self.llm.invoke(check_prompt).content.upper()

        if "INAP" in status:
            return {"safe": False, "queries": [], "new_topic": False}

        raw_expansion = self.llm.invoke([("system", QUERY_EXPANSION_PROMPT), ("human", current_query)]).content
        try:
            clean_json = raw_expansion.replace("```json", "").replace("```", "").strip()
            queries = json.loads(clean_json)
        except:
            queries = [current_query]

        return {"safe": True, "queries": queries, "new_topic": "NEW" in status}