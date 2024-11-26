from flask import Flask, send_from_directory, send_file
from app.routes import transcribe_bp
from flask_cors import CORS
import os

# Get the path to the React build directory
REACT_BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build'))

app = Flask(__name__, static_folder=REACT_BUILD_DIR, static_url_path='/')
CORS(app)

# Register the transcription blueprint
app.register_blueprint(transcribe_bp, url_prefix='/api')

# Serve React build files for the root and all other non-API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # Serve index.html for the root and client-side routes
    if path != "" and os.path.exists(os.path.join(REACT_BUILD_DIR, path)):
        return send_from_directory(REACT_BUILD_DIR, path)
    return send_from_directory(REACT_BUILD_DIR, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)