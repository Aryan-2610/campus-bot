"""
Text-to-Speech using Sarvam AI.
Converts text to natural-sounding Indian language speech and outputs in OGG Opus format.
"""

import requests
import base64
import os
import logging
import uuid
import subprocess
import shutil
from dotenv import load_dotenv
from typing import Union
from langdetect import detect, LangDetectException

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
TTS_API_URL = "https://api.sarvam.ai/text-to-speech"
TTS_HEADERS = {
    "api-subscription-key": SARVAM_API_KEY,
    "Content-Type": "application/json"
}

AUDIO_OUTPUT_DIR = "temp_audio_files"
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

VOICE_MAPPING = {
    "hi-IN": {"speaker": "anushka", "name": "Hindi"},
    "en-IN": {"speaker": "anushka", "name": "Hindi"},
}

def get_optimal_voice(language_code: str) -> str:
    """Gets the optimal speaker for a given language code."""
    return VOICE_MAPPING.get(language_code, VOICE_MAPPING["hi-IN"])["speaker"]

def text_to_speech(text: str, language: str = "hi-IN") -> Union[str, None]:
    """
    Converts text to speech, and ensures the output is in OGG Opus format.
    Includes a check to prevent generating English audio when Hindi is expected.
    """
    if not shutil.which("ffmpeg"):
        logger.error("ffmpeg is not installed or not in PATH. Cannot convert audio to OGG.")
        return None
        
    try:
        if not SARVAM_API_KEY:
            logger.error("SARVAM_API_KEY is not set. TTS is disabled.")
            return None
        
        logger.info(f"Converting text to speech in '{language}': {text[:100]}...")

        MAX_TTS_LENGTH = 500
        clean_text = text.strip()[:MAX_TTS_LENGTH]
        
        if not clean_text:
            logger.warning("Cannot generate speech from empty text.")
            return None

        # --- LANGUAGE MISMATCH CHECK ---
        # If the requested language is Hindi, but the text provided is English,
        # it means the upstream translation likely failed. We should not generate
        # incorrect audio in this case.
        if language == "hi-IN":
            try:
                detected_text_lang = detect(clean_text)
                if detected_text_lang != 'hi':
                    logger.error(
                        f"Language mismatch: Expected Hindi text for TTS but detected '{detected_text_lang}'. "
                        "Translation likely failed upstream. Aborting audio generation."
                    )
                    return None # Fail gracefully, causing a fallback to a text message
            except LangDetectException:
                # If language detection fails on the text, it's safer to abort.
                logger.warning("Could not determine language of the final text for TTS. Aborting audio generation.")
                return None # <-- CRITICAL FIX: Also fail gracefully here.

        speaker = get_optimal_voice(language)

        payload = {
            "inputs": [clean_text], 
            "target_language_code": "hi-IN", # Always use hi-IN for the bulbul:v2 model
            "speaker": speaker, 
            "model": "bulbul:v2"
        }

        response = requests.post(TTS_API_URL, headers=TTS_HEADERS, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        if "audios" in result and result["audios"]:
            audio_base64 = result["audios"][0]
            audio_bytes = base64.b64decode(audio_base64)
            
            unique_id = uuid.uuid4()
            temp_mp3_path = os.path.join(AUDIO_OUTPUT_DIR, f"{unique_id}_temp.mp3")
            final_ogg_path = os.path.join(AUDIO_OUTPUT_DIR, f"{unique_id}.ogg")

            try:
                with open(temp_mp3_path, "wb") as f:
                    f.write(audio_bytes)
                
                ffmpeg_command = [
                    "ffmpeg", "-i", temp_mp3_path, "-acodec", "libopus",
                    "-vbr", "on", "-vn", final_ogg_path
                ]
                
                logger.info("Converting TTS output from MP3 to OGG Opus...")
                subprocess.run(ffmpeg_command, check=True, capture_output=True)
                
                logger.info(f"✅ TTS OGG audio generated: {final_ogg_path}")
                return final_ogg_path

            finally:
                if os.path.exists(temp_mp3_path):
                    os.remove(temp_mp3_path)

        else:
            logger.error(f"No audio data received from TTS API. Response: {result}")
            return None

    except requests.HTTPError as e:
        logger.error(f"TTS API HTTP error: {e}, Response: {e.response.text}")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg conversion failed: {e.stderr.decode()}")
        return None
    except Exception as e:
        logger.error(f"TTS processing failed: {str(e)}")
        return None

