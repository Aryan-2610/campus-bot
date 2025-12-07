"""
Audio processing utilities using FFmpeg.
Downloads and converts audio files for STT processing.
"""
import requests
import subprocess
import tempfile
import os
import logging
from dotenv import load_dotenv
from typing import Union  # <-- CHANGE 1: Import Union

# --- Configuration ---
load_dotenv() # Loads variables from your .env file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Twilio credentials directly from environment
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

def download_and_convert_audio(media_url: str) -> Union[str, None]: # <-- CHANGE 2: Use Union
    """
    Download audio from an authenticated Twilio URL and convert to WAV.

    Args:
        media_url: The media URL provided by Twilio's webhook.

    Returns:
        Path to the converted WAV file, or None on failure.
    """
    try:
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
            logger.error("Twilio credentials (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) are not set in the .env file. Cannot download audio.")
            return None
            
        # Step 1: Download the audio file with authentication
        logger.info(f"Downloading audio from: {media_url}")
        response = requests.get(
            media_url,
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=30
        )
        response.raise_for_status()

        # Step 2: Create a temporary directory to work in
        temp_dir = tempfile.mkdtemp(prefix="audio_pipeline_")
        input_file_path = os.path.join(temp_dir, "input.ogg")
        output_file_path = os.path.join(temp_dir, "output.wav")

        # Step 3: Save downloaded content
        with open(input_file_path, "wb") as f:
            f.write(response.content)

        # Step 4: Convert using FFmpeg to 16kHz mono WAV
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", input_file_path,
            "-ar", "16000",   # Audio sample rate
            "-ac", "1",         # Mono channel
            "-f", "wav",
            output_file_path
        ]

        logger.info("Converting audio with FFmpeg...")
        result = subprocess.run(
            ffmpeg_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if result.returncode != 0:
            logger.error(f"FFmpeg error: {result.stderr}")
            raise RuntimeError(f"Audio conversion failed: {result.stderr}")

        logger.info(f"Audio converted successfully: {output_file_path}")
        return output_file_path

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download audio from Twilio: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}")
        return None