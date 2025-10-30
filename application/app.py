"""
FastAPI Web Interface for Emotional TTS System
Provides REST API endpoints for the dual-engine TTS system.
"""

import os
import sys
import asyncio
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

# Add parent directory to path to import solution.py
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Import from solution.py in parent directory
from solution import DualTTSSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Emotional TTS API",
    description="REST API for Emotional Speech Generation using Dual-Engine TTS System",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize TTS system
tts_system = DualTTSSystem()

# Storage for async tasks
task_storage: Dict[str, Dict[str, Any]] = {}

# Pydantic models
class TTSRequest(BaseModel):
    text: str
    style: str = "neutral"
    intensity: int = 50
    engine: str = "auto"
    voice: Optional[str] = None
    speed: Optional[float] = None

class TTSResponse(BaseModel):
    success: bool
    message: str
    audio_url: Optional[str] = None
    task_id: Optional[str] = None
    processing_time: Optional[float] = None

class SystemStatus(BaseModel):
    coqui_available: bool
    pyttsx3_available: bool
    default_engine: str
    total_requests: int
    uptime: str

class TaskStatus(BaseModel):
    task_id: str
    status: str  # "pending", "processing", "completed", "failed"
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Global counters
request_counter = 0
start_time = datetime.now()

@app.get("/")
async def root():
    """Serve the main frontend page"""
    return FileResponse("static/index.html")

@app.get("/api/status", response_model=SystemStatus)
async def get_system_status():
    """Get system status and engine availability"""
    global request_counter, start_time
    
    status = tts_system.get_status()
    uptime = str(datetime.now() - start_time).split('.')[0]
    
    return SystemStatus(
        coqui_available=status["coqui"],
        pyttsx3_available=status["pyttsx3"],
        default_engine="coqui" if status["coqui"] else "pyttsx3",
        total_requests=request_counter,
        uptime=uptime
    )

@app.get("/api/voices")
async def get_available_voices():
    """Get list of available voices with detailed information"""
    try:
        voices_data = {
            "success": True,
            "pyttsx3": [],
            "coqui": []
        }
        
        # Get pyttsx3 voices if available
        if tts_system.pyttsx and tts_system.pyttsx.available:
            try:
                import pyttsx3
                temp_engine = pyttsx3.init()
                voices = temp_engine.getProperty('voices')
                
                for i, voice in enumerate(voices):
                    name = getattr(voice, 'name', f'Voice {i}')
                    languages = getattr(voice, 'languages', ['Unknown'])
                    
                    # Determine gender based on voice name patterns
                    gender = "female"
                    if any(male_name in name.lower() for male_name in ['david', 'mark', 'paul', 'richard', 'james']):
                        gender = "male"
                    elif any(female_name in name.lower() for female_name in ['zira', 'hazel', 'susan', 'irina', 'huihui', 'hanhan', 'helena', 'sabina']):
                        gender = "female"
                    else:
                        gender = "neutral"
                    
                    # Determine language display
                    lang_display = "English (US)"
                    if isinstance(languages, list) and len(languages) > 0:
                        lang_code = languages[0]
                        if 'ru' in lang_code.lower():
                            lang_display = "Russian"
                        elif 'zh-cn' in lang_code.lower():
                            lang_display = "Chinese (Simplified)"
                        elif 'zh-tw' in lang_code.lower():
                            lang_display = "Chinese (Taiwan)"
                        elif 'en' in lang_code.lower():
                            lang_display = "English (US)"
                    
                    voices_data["pyttsx3"].append({
                        "id": str(i),
                        "name": name,
                        "gender": gender,
                        "language": lang_display,
                        "language_code": languages[0] if isinstance(languages, list) and languages else "en-US",
                        "engine": "pyttsx3",
                        "description": f"{name} - {gender.title()} voice ({lang_display})"
                    })
                
                temp_engine.stop()
                del temp_engine
                
            except Exception as e:
                logger.warning(f"Could not load pyttsx3 voices: {e}")
        
        # Get Coqui voices if available
        if tts_system.coqui and tts_system.coqui.available:
            # Add some common Coqui TTS voices
            coqui_voices = [
                {"name": "jenny", "gender": "female", "language": "English (US)", "quality": "high"},
                {"name": "ljspeech", "gender": "female", "language": "English (US)", "quality": "high"},
            ]
            
            for voice in coqui_voices:
                voices_data["coqui"].append({
                    "id": voice["name"],
                    "name": voice["name"].title(),
                    "gender": voice["gender"],
                    "language": voice["language"],
                    "language_code": "en-US",
                    "engine": "coqui",
                    "quality": voice["quality"],
                    "description": f"{voice['name'].title()} - {voice['gender'].title()} voice ({voice['language']}, {voice['quality']} quality)"
                })
        
        return voices_data
        
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/styles")
async def get_emotional_styles():
    """Get list of available emotional styles"""
    return {
        "success": True,
        "styles": [
            {"id": "neutral", "name": "Neutral", "description": "Standard speech"},
            {"id": "happy", "name": "Happy", "description": "Cheerful and upbeat"},
            {"id": "sad", "name": "Sad", "description": "Melancholic and slow"},
            {"id": "angry", "name": "Angry", "description": "Intense and forceful"},
            {"id": "excited", "name": "Excited", "description": "Energetic and fast"},
            {"id": "calm", "name": "Calm", "description": "Peaceful and steady"},
            {"id": "dramatic", "name": "Dramatic", "description": "Theatrical and expressive"}
        ]
    }

@app.post("/api/synthesize", response_model=TTSResponse)
async def synthesize_speech(request: TTSRequest):
    """Synchronous TTS synthesis"""
    global request_counter
    request_counter += 1
    
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(request.text) > 1000:
            raise HTTPException(status_code=400, detail="Text too long (max 1000 characters)")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_{timestamp}_{uuid.uuid4().hex[:8]}.wav"
        output_path = Path("static/audio") / filename
        
        # Ensure audio directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Record start time
        start_time_synthesis = datetime.now()
        
        # Synthesize speech
        success = tts_system.synthesize(
            text=request.text,
            output_path=output_path,
            engine=request.engine,
            style=request.style,
            intensity=request.intensity,
            voice=request.voice,
            speed=request.speed
        )
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time_synthesis).total_seconds()
        
        if success and output_path.exists():
            audio_url = f"/static/audio/{filename}"
            return TTSResponse(
                success=True,
                message="Speech synthesized successfully",
                audio_url=audio_url,
                processing_time=processing_time
            )
        else:
            raise HTTPException(status_code=500, detail="Speech synthesis failed")
            
    except Exception as e:
        logger.error(f"Synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/synthesize-async", response_model=TTSResponse)
async def synthesize_speech_async(request: TTSRequest, background_tasks: BackgroundTasks):
    """Asynchronous TTS synthesis for longer texts"""
    global request_counter
    request_counter += 1
    
    try:
        # Validate input
        if not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        # Generate task ID
        task_id = str(uuid.uuid4())
        
        # Initialize task status
        task_storage[task_id] = {
            "status": "pending",
            "progress": 0,
            "created_at": datetime.now(),
            "request": request.dict()
        }
        
        # Add background task
        background_tasks.add_task(process_async_synthesis, task_id, request)
        
        return TTSResponse(
            success=True,
            message="Task queued for processing",
            task_id=task_id
        )
        
    except Exception as e:
        logger.error(f"Async synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    """Get status of async synthesis task"""
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    return TaskStatus(
        task_id=task_id,
        status=task["status"],
        progress=task["progress"],
        result=task.get("result"),
        error=task.get("error")
    )

async def process_async_synthesis(task_id: str, request: TTSRequest):
    """Background task for async synthesis"""
    try:
        # Update status
        task_storage[task_id]["status"] = "processing"
        task_storage[task_id]["progress"] = 10
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tts_async_{timestamp}_{task_id[:8]}.wav"
        output_path = Path("static/audio") / filename
        
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update progress
        task_storage[task_id]["progress"] = 30
        
        # Synthesize speech
        start_time = datetime.now()
        success = tts_system.synthesize(
            text=request.text,
            output_path=output_path,
            engine=request.engine,
            style=request.style,
            intensity=request.intensity,
            voice=request.voice,
            speed=request.speed
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if success and output_path.exists():
            # Task completed successfully
            task_storage[task_id].update({
                "status": "completed",
                "progress": 100,
                "result": {
                    "audio_url": f"/static/audio/{filename}",
                    "processing_time": processing_time,
                    "file_size": output_path.stat().st_size
                }
            })
        else:
            # Task failed
            task_storage[task_id].update({
                "status": "failed",
                "progress": 100,
                "error": "Speech synthesis failed"
            })
            
    except Exception as e:
        logger.error(f"Async task {task_id} failed: {e}")
        task_storage[task_id].update({
            "status": "failed",
            "progress": 100,
            "error": str(e)
        })

@app.delete("/api/cleanup")
async def cleanup_old_files():
    """Clean up old audio files (older than 1 hour)"""
    try:
        audio_dir = Path("static/audio")
        if not audio_dir.exists():
            return {"success": True, "message": "No audio directory found"}
        
        cutoff_time = datetime.now() - timedelta(hours=1)
        deleted_count = 0
        
        for file_path in audio_dir.glob("*.wav"):
            if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                file_path.unlink()
                deleted_count += 1
        
        # Also cleanup old tasks
        old_tasks = [
            task_id for task_id, task in task_storage.items()
            if task["created_at"] < cutoff_time
        ]
        for task_id in old_tasks:
            del task_storage[task_id]
        
        return {
            "success": True,
            "message": f"Cleaned up {deleted_count} files and {len(old_tasks)} tasks"
        }
        
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return {"success": False, "error": str(e)}

@app.post("/api/preview-voice")
async def preview_voice(request: dict):
    """Generate a short voice preview"""
    try:
        voice_id = request.get("voice_id", "")
        engine = request.get("engine", "auto")
        
        # Short preview text
        preview_text = "Hello, this is a voice preview. How do you like this voice?"
        
        # Generate unique filename
        preview_id = str(uuid.uuid4())[:8]
        output_path = Path("static/audio") / f"preview_{preview_id}.wav"
        output_path.parent.mkdir(exist_ok=True)
        
        # Synthesize preview
        success = tts_system.synthesize(
            text=preview_text,
            output_path=output_path,
            engine=engine,
            voice=voice_id,
            style="neutral",
            intensity=50
        )
        
        if success:
            return {
                "success": True,
                "audio_url": f"/static/audio/preview_{preview_id}.wav",
                "message": "Voice preview generated successfully"
            }
        else:
            return {"success": False, "error": "Failed to generate voice preview"}
            
    except Exception as e:
        logger.error(f"Voice preview error: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)