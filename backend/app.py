from flask import Flask, send_from_directory
from app.routes import transcribe_bp
from flask_cors import CORS
import os
import ssl

# Absolute path to the React build directory
REACT_BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'build'))

app = Flask(__name__,
            static_folder=REACT_BUILD_DIR,
            static_url_path='/')

# CORS configuration
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Register the transcription blueprint
app.register_blueprint(transcribe_bp, url_prefix='/api')


# Serve React build files for the root and all other non-API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    # Always serve index.html for client-side routing
    if path != "" and os.path.exists(os.path.join(REACT_BUILD_DIR, path)):
        return send_from_directory(REACT_BUILD_DIR, path)
    return send_from_directory(REACT_BUILD_DIR, 'index.html')


if __name__ == '__main__':
    print(f"Serving React build from: {REACT_BUILD_DIR}")

    # Generate self-signed certificate (if not already exists)
    if not os.path.exists('server.key') or not os.path.exists('server.crt'):
        os.system(
            'openssl req -x509 -newkey rsa:4096 -nodes -out server.crt -keyout server.key -days 365 -subj "/CN=localhost"')

    # Create SSL context
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('server.crt', 'server.key')

    # Run with SSL
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context=context)