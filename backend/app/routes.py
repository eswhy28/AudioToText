import os
import logging
from flask import Blueprint, request, jsonify, make_response
from werkzeug.utils import secure_filename
from app.whisper_integration import WhisperTranscriber  # Ensure this import matches your project structure

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

transcribe_bp = Blueprint('transcribe', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize transcriber
transcriber = None
try:
    transcriber = WhisperTranscriber(model_name="turbo")
except Exception as e:
    logger.critical(f"Failed to initialize Whisper transcriber: {e}")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@transcribe_bp.route('/transcribe', methods=['POST', 'OPTIONS'])
def transcribe():
    # Handle CORS preflight and actual request
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    # Check if transcriber is initialized
    if transcriber is None:
        return jsonify({"error": "Transcription service not available"}), 500

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    try:
        file.save(file_path)

        # Perform transcription
        result = transcriber.transcribe_audio(file_path)

        # Always attempt to remove the file
        try:
            os.remove(file_path)
        except Exception as cleanup_error:
            logger.warning(f"Could not remove temporary file: {cleanup_error}")

        # Create response with CORS headers
        response = make_response(jsonify(result))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')

        return response, 200 if 'error' not in result else 400

    except Exception as e:
        # Ensure file is removed even if transcription fails
        try:
            os.remove(file_path)
        except:
            pass

        logger.error(f"Transcription failed: {e}")
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500