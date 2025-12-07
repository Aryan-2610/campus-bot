# translator.py

import os
import torch
import logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Simplified Configuration ---
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
logger.info(f"Using device: {DEVICE}")

# Hardcoded language codes for Hindi and English
HINDI_CODE = "hin_Deva"
ENGLISH_CODE = "eng_Latn"

# IndicTrans model names
XX2EN_MODEL = "ai4bharat/indictrans2-indic-en-1B"
EN2XX_MODEL = "ai4bharat/indictrans2-en-indic-1B"

# --- Model and Tokenizer Initialization ---
try:
    # Model for Indic languages to English
    xx2en_tokenizer = AutoTokenizer.from_pretrained(XX2EN_MODEL, trust_remote_code=True)
    xx2en_model = AutoModelForSeq2SeqLM.from_pretrained(XX2EN_MODEL, trust_remote_code=True).to(DEVICE)

    # Model for English to Indic languages
    en2xx_tokenizer = AutoTokenizer.from_pretrained(EN2XX_MODEL, trust_remote_code=True)
    en2xx_model = AutoModelForSeq2SeqLM.from_pretrained(EN2XX_MODEL, trust_remote_code=True).to(DEVICE)
    logger.info("Translation models loaded successfully.")

except Exception as e:
    logger.critical(f"Failed to load translation models: {e}")
    # You might want to exit or handle this critical failure
    xx2en_tokenizer = xx2en_model = en2xx_tokenizer = en2xx_model = None

# --- Core Translation Functions ---
def safe_generate(model, tokenizer, inputs, max_len=256):
    """Safely generates translation with error handling."""
    try:
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                use_cache=True,
                min_length=0,
                max_length=max_len,
                num_beams=5,
                num_return_sequences=1,
            )
        # Decode the generated ids to a string
        decoded = tokenizer.batch_decode(outputs, skip_special_tokens=True)[0]
        return decoded.strip() if decoded.strip() else ""
    except Exception as e:
        logger.error(f"Translation generation failed: {e}")
        return ""

def to_english(text: str, source_lang_code: str) -> tuple[str, None]:
    """Translates text to English, but only if it's not already English."""
    if not xx2en_model:
        logger.error("Hindi-to-English model is not available.")
        return text, None # Return a tuple with a placeholder

    # Extract the base language code (e.g., 'hi' from 'hi-IN')
    lang_key = source_lang_code.split('-')[0].lower()

    # If the source is English, no translation is needed
    if lang_key == 'en':
        logger.info("Source language is English; skipping translation to English.")
        return text, None # Return a tuple with a placeholder

    try:
        # Prepare the input with language tags for Hindi to English translation
        tagged_input = f"{HINDI_CODE} {ENGLISH_CODE} {text}"
        inputs = xx2en_tokenizer(tagged_input, return_tensors="pt", padding=True).to(DEVICE)

        translation = safe_generate(xx2en_model, xx2en_tokenizer, inputs)
        
        if not translation:
            logger.warning("Empty translation. Returning original text.")
            return text, None # Return a tuple with a placeholder

        logger.info(f"Translated '{text}' from Hindi to English: '{translation}'")
        return translation, None # Return a tuple with a placeholder
    except Exception as e:
        logger.error(f"to_english error: {e}")
        return text, None # Return a tuple with a placeholder


def from_english(text: str, target_language_code: str) -> str:
    """Translates text from English to Hindi, if the target language is Hindi."""
    if not en2xx_model:
        logger.error("English-to-Hindi model is not available.")
        return text
        
    # Extract the base language code (e.g., 'hi' from 'hi-IN')
    target_lang_key = target_language_code.split('-')[0].lower()
    
    # If the target is not Hindi, return the original English text
    if target_lang_key != 'hi':
        logger.info(f"Target language is '{target_lang_key}', not Hindi. Returning original English text.")
        return text

    try:
        # Prepare the input with language tags for English to Hindi translation
        tagged_input = f"{ENGLISH_CODE} {HINDI_CODE} {text}"
        inputs = en2xx_tokenizer(tagged_input, return_tensors="pt", padding=True).to(DEVICE)

        translation = safe_generate(en2xx_model, en2xx_tokenizer, inputs)
        
        if not translation:
            logger.warning("Empty translation. Returning original text.")
            return text

        logger.info(f"Translated '{text}' from English to Hindi: '{translation}'")
        return translation
    except Exception as e:
        logger.error(f"from_english error: {e}")
        return text