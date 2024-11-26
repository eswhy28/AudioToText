from flask import Blueprint, request, jsonify, make_response
from werkzeug.utils import secure_filename
import os
from app.whisper_integration import transcribe_audio

transcribe_bp = Blueprint('transcribe', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


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

    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Perform transcription
    try:
        result = transcribe_audio(file_path)
        os.remove(file_path)  # Clean up after transcription

        # Create response with CORS headers
        response = make_response(jsonify(result))
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'POST')

        return response, 200
    except Exception as e:
        os.remove(file_path)
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500