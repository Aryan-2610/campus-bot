import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load your GOOGLE_API_KEY from .env
load_dotenv()

def list_my_models():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env")
        return

    genai.configure(api_key=api_key)

    print("--- SEARCHING FOR MODELS ---")
    try:
        models = genai.list_models()
        
        embedding_models = []
        chat_models = []

        for m in models:
            # Check for Embedding support
            if 'embedContent' in m.supported_generation_methods:
                embedding_models.append(m.name)
            
            # Check for Chat/Generation support
            if 'generateContent' in m.supported_generation_methods:
                chat_models.append(m.name)

        print("\n✅ MODELS FOR EMBEDDING (Use one of these in your code):")
        for model in embedding_models:
            print(f" - {model}")

        print("\n✅ MODELS FOR CHAT (Use one of these for LLM):")
        for model in chat_models:
            print(f" - {model}")

    except Exception as e:
        print(f"FAILED to list models. Error: {e}")
        print("\nCheck if your API Key is correct and has Gemini API enabled in Google AI Studio.")

if __name__ == "__main__":
    list_my_models()