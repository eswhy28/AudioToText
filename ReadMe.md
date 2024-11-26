# AudioToText Application

## Overview
This is a Flask-based backend application for handling audio transcription requests, paired with a React-based frontend for user interaction. The backend serves both the API and the React frontend's static files.

---

## Prerequisites
1. **Python**: Ensure Python 3.12+ is installed on your system.
2. **Node.js**: Needed if you want to build the React frontend manually.

---

## Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd AudioToText
```

### 2. Navigate to the Backend Directory
```bash
cd backend
```

### 3. Create a Virtual Environment
```bash
python3 -m venv venv
```

### 4. Activate the Virtual Environment
- **On Linux/macOS:**
  ```bash
  source venv/bin/activate
  ```
- **On Windows (Command Prompt):**
  ```bash
  venv\Scripts\activate
  ```

### 5. Install Dependencies
Use `pip` to install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 6. Run the Flask Application
Start the backend server by running:
```bash
python app.py
```

This will:
- Launch the Flask backend server on `http://0.0.0.0:5000` by default.
- Serve the static files of the React application (located in the `frontend/build` directory).
- Provide APIs at the `/api` endpoint.

---

## Frontend Integration
Ensure that the React frontend is built and available in the `frontend/build` directory. The Flask backend automatically serves these static files.

If you need to rebuild the React application:
1. Navigate to the `frontend` directory:
   ```bash
   cd ../frontend
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Build the React application:
   ```bash
   npm run build
   ```
4. Return to the backend directory:
   ```bash
   cd ../backend
   ```

---

## Notes
- **Development Mode:** If you're developing the application and want live reloading for the Flask backend, run:
  ```bash
  python app.py
  ```


---

## Directory Structure
```
AudioToText/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── whisper_integration.py
│   │   ├── uploads/
│   ├── venv/            # Virtual environment folder
│   ├── app.py           # Main Flask application
│   ├── requirements.txt # Backend dependencies
├── frontend/
│   ├── build/           # Compiled React files (static)
│   ├── src/             # React source files
```
