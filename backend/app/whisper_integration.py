import os
import logging
import whisper
from typing import Dict, Union

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WhisperTranscriber:
    def __init__(self, model_name: str = "turbo"):
        """
        Initialize the Whisper transcription model.

        Args:
            model_name (str): Name of the Whisper model to load. Defaults to 'turbo'.
        """
        try:
            # Validate model availability
            available_models = ["tiny", "base", "small", "medium", "large", "turbo"]
            if model_name not in available_models:
                raise ValueError(f"Invalid model name. Choose from {available_models}")

            # Load the Whisper model with error handling
            self.model = whisper.load_model(model_name)
            logger.info(f"Whisper {model_name} model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise

    def transcribe_audio(self, file_path: str) -> Dict[str, Union[str, None]]:
        """
        Transcribe an audio file using Whisper model.

        Args:
            file_path (str): Path to the audio file to transcribe.

        Returns:
            Dict containing transcription results or error information.
        """
        # Validate file existence and type
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"error": "File not found"}

        # Check file size (optional, prevents extremely large files)
        max_file_size_mb = 50
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if file_size_mb > max_file_size_mb:
            logger.warning(f"File size {file_size_mb:.2f}MB exceeds limit of {max_file_size_mb}MB")
            return {"error": f"File too large. Maximum size is {max_file_size_mb}MB"}

        try:
            # Transcription with enhanced options
            result = self.model.transcribe(
                file_path,
                fp16=False,  # Disable half-precision for broader compatibility
                language=None,  # Auto-detect language
                task="transcribe",  # Standard transcription
                verbose=False,  # Disable verbose output
                condition_on_previous_text=True  # Improve context recognition
            )

            # Log transcription details
            logger.info(f"Transcription completed for {file_path}")
            logger.info(f"Detected Language: {result.get('language', 'Unknown')}")

            return {
                "language": result.get("language", ""),
                "transcription": result.get("text", ""),
                "segments": result.get("segments", [])  # Optional: Include detailed segments
            }

        except Exception as e:
            logger.error(f"Transcription error for {file_path}: {e}")
            return {"error": str(e)}