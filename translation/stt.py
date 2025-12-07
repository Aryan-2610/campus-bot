import os
import logging
from typing import Dict
import whisper
from langdetect import detect, LangDetectException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
MODEL_NAME = "base" # A good balance of size and accuracy

try:
    logger.info(f"Loading local Whisper model '{MODEL_NAME}'...")
    model = whisper.load_model(MODEL_NAME)
    logger.info("✅ Whisper model loaded successfully.")
    model_loaded = True
except Exception as e:
    logger.error(f"Failed to load the Whisper model. Please check your installation. Error: {e}")
    model_loaded = False

# --- Public Entry-Point ---

def detect_and_transcribe(wav_file_path: str) -> Dict[str, object]:
    """
    Transcribes audio using a locally-run OpenAI Whisper model, with robust
    language detection directly from the audio.

    Returns a dict with keys: text, language.
    """
    if not model_loaded:
        return {"text": "", "language": "en-IN"}

    try:
        logger.info("Transcribing audio with local Whisper model...")

        # 1. Load the audio file
        audio = whisper.load_audio(wav_file_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # 2. **CRITICAL FIX**: Detect the language directly from the audio mel spectrogram
        _, probs = model.detect_language(mel)
        detected_lang_code = max(probs, key=probs.get)
        logger.info(f"Whisper detected language from audio: '{detected_lang_code}'")

        # 3. Decode the audio into text
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(model, mel, options)
        text = result.text.strip()
        
        logger.info(f"✅ Local Whisper transcription successful: '{text[:100]}...'")

        if not text:
            return {"text": "", "language": "en-IN"}

        # 4. Map the detected language to the format our app uses
        if detected_lang_code == "hi":
            language = "hi-IN"
        else:
            # Default to English for any other detected language
            language = "en-IN"

        return {
            "text": text,
            "language": language
        }

    except Exception as e:
        logger.error(f"An unexpected error occurred during local transcription: {e}")
        return {"text": "", "language": "en-IN"}

