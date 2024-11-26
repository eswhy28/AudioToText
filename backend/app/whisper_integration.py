import whisper

# Load the Whisper turbo model
model = whisper.load_model("turbo")

def transcribe_audio(file_path):
    """
    Transcribe an audio file using OpenAI Whisper turbo model.
    Args:
        file_path (str): Path to the audio file.
    Returns:
        dict: Transcription result including detected language and text.
    """
    try:
        # Perform transcription using Whisper's built-in method
        # This will handle all preprocessing internally
        result = model.transcribe(
            file_path,
            fp16=False,  # Disable half-precision to avoid potential issues
            language=None,  # Let the model detect the language
            task="transcribe"
        )

        # Return the transcription result
        return {
            "language": result.get("language", ""),
            "transcription": result.get("text", "")
        }
    except Exception as e:
        return {"error": str(e)}