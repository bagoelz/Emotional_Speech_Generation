# Emotional TTS Web Application

Welcome to the web application for the Emotional Text-to-Speech system! This is an easy-to-use web interface for converting text to speech with various emotional styles.

## 🎯 What Can It Do?

This application allows you to:
- **Convert text to speech** with high quality
- **Choose emotional styles** like happy, sad, angry, or neutral
- **Adjust emotion intensity** from 1-100
- **Select TTS engine** (Coqui for high quality or pyttsx3 for compatibility)
- **Control speech speed** as needed
- **Download audio files** from synthesis results

## 🚀 How to Run

### 1. Environment Setup

```bash
# Create virtual environment (highly recommended)
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Start Server

```bash
# Run FastAPI server
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open in Browser

After the server is running, open your browser and visit:
```
http://localhost:8000
```

## 🎨 How to Use the Interface

### Web Interface
1. **Enter text** you want to convert to speech
2. **Select emotional style** from dropdown (neutral, happy, sad, angry, etc.)
3. **Adjust intensity** with slider (1-100)
4. **Choose TTS engine** (auto/coqui/pyttsx3)
5. **Click "Generate Speech"** and wait for processing
6. **Listen to result** and download if needed

### Keyboard Shortcuts
- **Ctrl+Enter**: Generate speech
- **Ctrl+L**: Clear form
- **Ctrl+E**: Load example text

## 🔧 API Endpoints

This application also provides REST API that can be used programmatically:

### GET `/api/status`
Get system status and TTS engine availability.

**Response:**
```json
{
  "coqui_available": true,
  "pyttsx3_available": true,
  "default_engine": "coqui",
  "total_requests": 42,
  "uptime": "2:30:15"
}
```

### POST `/api/synthesize`
Synchronous text-to-speech synthesis.

**Request Body:**
```json
{
  "text": "Hello, how are you today?",
  "style": "happy",
  "intensity": 75,
  "engine": "auto",
  "voice": null,
  "speed": 1.0
}
```

**Response:**
```json
{
  "success": true,
  "message": "Speech synthesized successfully",
  "audio_url": "/static/audio/tts_20241030_181500_abc123.wav",
  "processing_time": 2.34
}
```

### POST `/api/synthesize-async`
Asynchronous text synthesis for longer texts.

**Request Body:** (same as `/api/synthesize`)

**Response:**
```json
{
  "success": true,
  "message": "Task queued for processing",
  "task_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### GET `/api/task/{task_id}`
Check async task status.

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "result": {
    "audio_url": "/static/audio/tts_async_20241030_181500_550e8400.wav",
    "processing_time": 5.67,
    "file_size": 245760
  }
}
```

### GET `/api/voices`
Get list of available voices.

### GET `/api/styles`
Get list of available emotional styles.

### DELETE `/api/cleanup`
Clean up old audio files (older than 1 hour).

## 🎭 Available Emotional Styles

| Style | Description | Good for |
|-------|-------------|----------|
| **neutral** | Standard, natural voice | Narration, news |
| **happy** | Cheerful and upbeat | Congratulations, promotions |
| **sad** | Melancholic and slow | Condolences, drama |
| **angry** | Intense and forceful | Warnings, protests |
| **excited** | Energetic and fast | Announcements, sports |
| **calm** | Peaceful and steady | Meditation, instructions |
| **dramatic** | Theatrical and expressive | Stories, presentations |

## ⚙️ TTS Engine Settings

### Coqui TTS (Primary Engine)
- **Quality**: Very high, natural voice
- **Features**: Full emotion control, various styles
- **Requirements**: GPU (optional), more RAM
- **Speed**: Slower but best results

### pyttsx3 (Fallback Engine)
- **Quality**: Standard, synthetic voice
- **Features**: Fast, lightweight, compatible
- **Requirements**: Minimal, built-in Windows
- **Speed**: Very fast

## 🔍 Troubleshooting

### Server Cannot Be Accessed
```bash
# Make sure server is running on correct port
uvicorn app:app --host 0.0.0.0 --port 8000

# Check if port 8000 is already in use
netstat -an | findstr :8000
```

### Import Module Error
```bash
# Make sure you're in the correct directory
cd application

# Make sure parent directory is in Python path
# (automatically handled in app.py)
```

### Audio Not Generated
1. **Check system status** at `/api/status`
2. **Make sure dependencies are installed** correctly
3. **Try switching engine** from auto to pyttsx3
4. **Check error logs** in terminal

### Audio Files Cannot Be Downloaded
1. **Make sure audio folder exists**: `static/audio/`
2. **Check folder permissions** for static
3. **Run cleanup** if disk is full: `/api/cleanup`

## 📁 Project Structure

```
application/
├── app.py                 # FastAPI application
├── requirements.txt       # Python dependencies
├── README.md             # Main documentation (this file)
├── README_FRONTEND.md    # Frontend documentation
└── static/
    ├── index.html        # Main page
    ├── style.css         # CSS styling
    ├── app.js           # Frontend JavaScript
    └── audio/           # Generated audio files
```
