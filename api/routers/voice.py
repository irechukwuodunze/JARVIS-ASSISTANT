import os
import base64
from fastapi import APIRouter, HTTPException, Depends
import google.generativeai as genai
from api.models import VoiceTranscriptionRequest, TranscriptionResponse
from api.deps import get_current_user

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)


@router.post("/transcribe")
async def transcribe_audio(request: VoiceTranscriptionRequest, current_user = Depends(get_current_user)):
    """Transcribe audio to text using Gemini 3 Flash multimodal capabilities"""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API not configured")
    
    try:
        import httpx
        
        # Download audio from URL
        async with httpx.AsyncClient() as client:
            audio_response = await client.get(request.audio_url)
            audio_response.raise_for_status()
            audio_data = audio_response.content
        
        # Encode audio to base64
        audio_base64 = base64.standard_b64encode(audio_data).decode("utf-8")
        
        # Determine MIME type from URL or default to wav
        mime_type = "audio/wav"
        if ".mp3" in request.audio_url:
            mime_type = "audio/mpeg"
        elif ".m4a" in request.audio_url:
            mime_type = "audio/mp4"
        elif ".ogg" in request.audio_url:
            mime_type = "audio/ogg"
        
        # Use Gemini to transcribe
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"Transcribe the following audio to text. Language: {request.language or 'en'}."
        if request.prompt:
            prompt += f" Context: {request.prompt}"
        
        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": audio_base64,
            }
        ])
        
        transcription_text = response.text
        
        return TranscriptionResponse(
            text=transcription_text,
            language=request.language or "en"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")


@router.post("/command")
async def parse_voice_command(request: VoiceTranscriptionRequest, current_user = Depends(get_current_user)):
    """Transcribe audio and parse as command using Gemini NLP"""
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API not configured")
    
    try:
        import httpx
        
        # Download audio
        async with httpx.AsyncClient() as client:
            audio_response = await client.get(request.audio_url)
            audio_response.raise_for_status()
            audio_data = audio_response.content
        
        audio_base64 = base64.standard_b64encode(audio_data).decode("utf-8")
        
        mime_type = "audio/wav"
        if ".mp3" in request.audio_url:
            mime_type = "audio/mpeg"
        elif ".m4a" in request.audio_url:
            mime_type = "audio/mp4"
        elif ".ogg" in request.audio_url:
            mime_type = "audio/ogg"
        
        # Use Gemini for transcription and command parsing
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = """Transcribe the audio and parse it as a command. Respond in JSON format:
{
    "transcription": "the transcribed text",
    "command_type": "create_event|update_event|query_schedule|log_expense|check_mood|start_focus_mode|other",
    "command_data": {},
    "confidence": 0.0
}

Command types:
- create_event: "Create event: Meeting at 2 PM"
- update_event: "Move my gym session to 5 PM"
- query_schedule: "What's my schedule for today?"
- log_expense: "Spent £15 on lunch"
- check_mood: "I'm feeling drained"
- start_focus_mode: "Start focus mode for 90 minutes"
- other: anything else
"""
        
        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": audio_base64,
            }
        ])
        
        import json
        try:
            command_data = json.loads(response.text)
        except:
            command_data = {
                "transcription": response.text,
                "command_type": "other",
                "command_data": {},
                "confidence": 0.5
            }
        
        return command_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Command parsing error: {str(e)}")
