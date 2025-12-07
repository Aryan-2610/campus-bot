# translator.py

import os
import torch
import logging
from langdetect import detect_langs, DetectorFactory
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Union

# --- Configuration ---
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini API key from environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-2.5-pro')
else:
    logger.warning("GEMINI_API_KEY not found. Translation will fail.")
    gemini_model = None

DetectorFactory.seed = 0

LANG_MAPPING = {
    "hi": {"name": "Hindi", "sarvam": "hi-IN"},
    "bn": {"name": "Bengali", "sarvam": "bn-IN"},
    "ta": {"name": "Tamil", "sarvam": "ta-IN"},
    "te": {"name": "Telugu", "sarvam": "te-IN"},
    "mr": {"name": "Marathi", "sarvam": "mr-IN"},
    "gu": {"name": "Gujarati", "sarvam": "gu-IN"},
    "kn": {"name": "Kannada", "sarvam": "kn-IN"},
    "ml": {"name": "Malayalam", "sarvam": "ml-IN"},
    "pa": {"name": "Punjabi", "sarvam": "pa-IN"},
    "or": {"name": "Odia", "sarvam": "or-IN"},
    "ur": {"name": "Urdu", "sarvam": None},
    "en": {"name": "English", "sarvam": "en-IN"},
}

def detect_language(text: str) -> str:
    try:
        detections = detect_langs(text)
        for det in detections:
            if det.lang in LANG_MAPPING and det.prob > 0.85:
                return det.lang
        # Return the first supported language detected, even with lower confidence
        for det in detections:
            if det.lang in LANG_MAPPING:
                return det.lang
    except Exception as e:
        logger.warning(f"Language detection failed: {e}")
    return "hi" # Default to Hindi

def to_english(text: str, source_lang_code: str = None) -> tuple[str, str]:
    try:
        if not gemini_model:
            raise RuntimeError("Gemini API key not configured, cannot translate.")
            
        lang = source_lang_code or detect_language(text)
        sarvam_code = LANG_MAPPING.get(lang, LANG_MAPPING["hi"])["sarvam"] or "hi-IN"

        # If already English, no need to translate
        if lang == "en":
            return text, sarvam_code

        prompt = f"Translate the following text to English:\n\n'{text}'"
        
        response = gemini_model.generate_content(prompt)
        translation = response.text.strip() if response and response.text else ""

        if not translation:
            logger.warning("Empty translation from Gemini. Returning original text.")
            return text, sarvam_code

        logger.info(f"Translated to English via Gemini: {translation}")
        return translation, sarvam_code

    except Exception as e:
        logger.error(f"to_english error: {e}")
        return text, "hi-IN"

def from_english(text: str, target_language_code: str) -> str:
    """
    Translates English text to the target language using the Gemini API.
    """
    try:
        if not gemini_model:
            raise RuntimeError("Gemini API key not configured, cannot translate.")

        target_lang_name = "Hindi" # Default
        for lang_code, details in LANG_MAPPING.items():
            if details.get("sarvam") == target_language_code:
                target_lang_name = details["name"]
                break
        
        # If the target is English, no need to translate
        if target_lang_name == "English":
            return text

        prompt = f"Translate the following English text to {target_lang_name}:\n\n'{text}'"

        response = gemini_model.generate_content(prompt)
        translation = response.text.strip() if response and response.text else ""

        if not translation:
            logger.warning("Empty translation from Gemini. Returning original English text.")
            return text
        
        logger.info(f"Translated from English to {target_lang_name} via Gemini: {translation}")
        return translation

    except Exception as e:
        logger.error(f"from_english (Gemini) error: {e}")
        # Fallback to returning the original English text if API fails
        return text