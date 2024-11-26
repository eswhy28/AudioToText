from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
from app.whisper_integration import transcribe_audio

transcribe_bp = Blueprint('transcribe', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a', 'flac'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@transcribe_bp.route('/transcribe', methods=['POST'])
def transcribe():
    # Add CORS headers
    response = jsonify({"error": "No file uploaded"})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST')

    if 'file' not in request.files:
        return response, 400

    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)

    # Perform transcription
    result = transcribe_audio(file_path)
    os.remove(file_path)  # Clean up after transcription

    # Add CORS headers to the response
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'POST')

    if result:
        return response, 200
    else:
        return jsonify({"error": "Transcription failed"}), 500
