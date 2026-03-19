import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def verify_gemini_setup():
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in .env file.")
        return

    genai.configure(api_key=api_key)

    print("--- 1. Available Models ---")
    try:
        # List all models and their supported methods
        for m in genai.list_models():
            # Filters for models that support 'embedContent' or 'generateContent'
            methods = ", ".join(m.supported_generation_methods)
            print(f"Model: {m.name:30} | Methods: {methods}")
    except Exception as e:
        print(f"Failed to list models: {e}")

    print("\n--- 2. Quick Connection Test ---")
    try:
        # Simple test using the Flash model
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'API Connection Successful!'")
        print(f"Response: {response.text.strip()}")
    except Exception as e:
        print(f"Connection test failed: {e}")

if __name__ == "__main__":
    verify_gemini_setup()