import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
import httpx
import google.generativeai as genai
from api.models import (
    AIMessageRequest, ParseEventRequest, ConflictDetectionRequest,
    ConflictResponse, MorningBriefingResponse, AIAnalysisResponse,
    ParseEventResponse, EventModel
)
from api.database import (
    get_user_events, get_user_ai_history, save_ai_message,
    get_user_by_id, get_user_behavior_events, upsert_user
)
from api.deps import get_current_user
from api.routers.memory import build_gemini_system_prompt

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def build_system_prompt_with_memory(timezone: str, local_time: str, day_of_week: str, memory_context=None) -> str:
    """Build system prompt with temporal context, user persona, and memory injection"""
    
    # Use memory-aware system prompt builder if memory context available
    if memory_context:
        return build_gemini_system_prompt(None, memory_context)
    
    # Fallback to basic prompt
    prompt = f"""You are JARVIS, an elite AI personal event manager and life optimizer. You are direct, proactive, and opinionated.

CRITICAL TEMPORAL CONTEXT (NEVER GUESS):
- User's current local time: {local_time}
- User's timezone: {timezone}
- Current day of week: {day_of_week}
- All times you reference or create MUST be in the user's timezone: {timezone}

CAPABILITIES:
- Parse natural language to create/update/delete events
- Detect scheduling conflicts and propose resolutions
- Analyze behavior patterns and provide proactive nudges
- Generate morning briefings based on the day's schedule
- Categorize and tag notes intelligently
- Remember user preferences and adapt behavior
- Learn from interactions and proactively suggest improvements

RESPONSE STYLE:
- Be concise and direct. No filler phrases.
- When creating events, always confirm the exact time back to the user.
- When detecting conflicts, always propose a specific resolution.
- Remember user preferences from past interactions.
- Proactively learn new preferences from user statements."""
    
    return prompt


async def call_gemini_with_memory(messages: list, system_prompt: str) -> str:
    """Call Gemini API with memory-injected system prompt"""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API not configured")
    
    try:
        # Use Gemini SDK for better handling
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(
            "gemini-1.5-flash",
            system_instruction=system_prompt
        )
        
        # Convert messages to text format
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
        
        response = model.generate_content(conversation_text)
        return response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")


async def call_gemini(messages: list) -> str:
    """Call Gemini API and return response text (legacy)"""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                json={
                    "contents": [{"parts": [{"text": msg["content"]}]} for msg in messages],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topP": 0.95,
                        "topK": 40,
                        "maxOutputTokens": 1024,
                    }
                },
                timeout=30.0
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {str(e)}")


@router.post("/chat")
async def chat(request: AIMessageRequest, current_user = Depends(get_current_user)):
    """Chat with JARVIS AI"""
    user = await get_user_by_id(str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get upcoming events for context
    now = int(datetime.utcnow().timestamp() * 1000)
    week_ahead = now + 7 * 24 * 60 * 60 * 1000
    upcoming_events = await get_user_events(str(current_user.id), now, week_ahead)
    
    events_context = ""
    if upcoming_events:
        events_context = "\n\nUSER'S UPCOMING EVENTS (next 7 days):\n"
        for e in upcoming_events:
            event_time = datetime.fromtimestamp(e.start_time / 1000).isoformat()
            events_context += f"- \"{e.title}\" at {event_time} ({e.category}, {e.energy_level} energy)\n"
    else:
        events_context = "\n\nNo upcoming events scheduled."
    
    system_prompt = build_system_prompt_with_memory(
        request.timezone,
        request.local_time,
        request.day_of_week,
        user.persona.dict() if user.persona else None
    ) + events_context
    
    # Prepare messages
    messages = [
        {"role": "system", "content": system_prompt},
        *request.conversation_history[-10:],  # Keep last 10 messages
        {"role": "user", "content": request.message}
    ]
    
    # Call Gemini
    assistant_message = await call_gemini(messages)
    
    # Save to history
    await save_ai_message({
        "user_id": str(current_user.id),
        "role": "user",
        "content": request.message,
        "created_at": datetime.utcnow()
    })
    await save_ai_message({
        "user_id": str(current_user.id),
        "role": "assistant",
        "content": assistant_message,
        "created_at": datetime.utcnow()
    })
    
    return {"message": assistant_message}


@router.post("/parse-event")
async def parse_event(request: ParseEventRequest, current_user = Depends(get_current_user)):
    """Parse natural language text to event"""
    system_prompt = f"""You are an event parser. Extract event details from natural language text.
Current time: {request.local_time}, Timezone: {request.timezone}, Day: {request.day_of_week}.
Return ONLY valid JSON with no markdown. If you cannot parse an event, return {{"error": "reason"}}.
JSON schema: {{"title": str, "description": str, "start_time_iso": str, "end_time_iso": str, "location": str, "category": str, "energy_level": str}}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request.text}
    ]
    
    response_text = await call_gemini(messages)
    
    try:
        parsed = json.loads(response_text)
        if "error" in parsed:
            return ParseEventResponse(success=False, error=parsed["error"])
        
        return ParseEventResponse(
            success=True,
            event=EventModel(
                user_id=str(current_user.id),
                title=parsed.get("title", ""),
                description=parsed.get("description", ""),
                start_time=int(datetime.fromisoformat(parsed.get("start_time_iso", "")).timestamp() * 1000),
                end_time=int(datetime.fromisoformat(parsed.get("end_time_iso", "")).timestamp() * 1000),
                location=parsed.get("location", ""),
                category=parsed.get("category", "other"),
                energy_level=parsed.get("energy_level", "medium")
            )
        )
    except Exception as e:
        return ParseEventResponse(success=False, error=f"Failed to parse: {str(e)}")


@router.post("/detect-conflicts")
async def detect_conflicts(request: ConflictDetectionRequest, current_user = Depends(get_current_user)):
    """Detect scheduling conflicts"""
    # Get events in the time range
    events = await get_user_events(
        str(current_user.id),
        request.start_time - 3600000,
        request.end_time + 3600000
    )
    
    # Find conflicts
    conflicts = []
    for e in events:
        if request.exclude_event_id and str(e.id) == request.exclude_event_id:
            continue
        if e.status in ["skipped", "completed"]:
            continue
        if e.start_time < request.end_time and e.end_time > request.start_time:
            conflicts.append(e)
    
    if not conflicts:
        return ConflictResponse(has_conflicts=False)
    
    # Generate suggestion
    conflict_list = ", ".join([f"\"{c.title}\"" for c in conflicts])
    system_prompt = "You are a scheduling assistant. Provide a brief, actionable conflict resolution suggestion in 1-2 sentences."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Conflict with: {conflict_list}. Suggest a resolution."}
    ]
    
    suggestion = await call_gemini(messages)
    
    return ConflictResponse(
        has_conflicts=True,
        conflicts=conflicts,
        suggestion=suggestion
    )


@router.post("/morning-briefing")
async def morning_briefing(request: AIMessageRequest, current_user = Depends(get_current_user)):
    """Generate morning briefing"""
    user = await get_user_by_id(str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get today's events
    today = datetime.utcnow()
    start_of_day = int(datetime(today.year, today.month, today.day).timestamp() * 1000)
    end_of_day = start_of_day + 86400000
    today_events = await get_user_events(str(current_user.id), start_of_day, end_of_day)
    
    event_list = ""
    if today_events:
        event_list = "Today's schedule:\n"
        for e in today_events:
            event_time = datetime.fromtimestamp(e.start_time / 1000).strftime("%H:%M")
            event_list += f"- {e.title} at {event_time} ({e.energy_level} energy, {e.category})\n"
    else:
        event_list = "No events scheduled today."
    
    system_prompt = f"""You are JARVIS. Generate a concise morning briefing in exactly 3 sentences.
Sentence 1: Overview of the day's energy demands.
Sentence 2: The most critical task or event.
Sentence 3: One proactive optimization suggestion.
Be direct, energizing, and specific. Current time: {request.local_time}, {request.day_of_week}.
User persona: Wake up: {user.wake_up_time or 'unknown'}, Goals: {', '.join(user.persona.daily_goals or [])}"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": event_list}
    ]
    
    briefing = await call_gemini(messages)
    
    return MorningBriefingResponse(briefing=briefing)


@router.post("/analyze-behavior")
async def analyze_behavior(current_user = Depends(get_current_user)):
    """Analyze user behavior patterns"""
    behavior_data = await get_user_behavior_events(str(current_user.id), 100)
    
    if len(behavior_data) < 5:
        return AIAnalysisResponse(insights="Not enough data yet. Keep using JARVIS and I'll learn your patterns.")
    
    summary = "\n".join([
        f"{b.action}: event {b.event_id} at {b.created_at.isoformat()}{f' (reason: {b.reason})' if b.reason else ''}"
        for b in behavior_data
    ])
    
    system_prompt = "You are a behavioral analyst. Analyze the user's event management patterns and provide 3 specific, actionable insights. Be direct and data-driven."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Behavior log:\n{summary}"}
    ]
    
    insights = await call_gemini(messages)
    
    # Update user persona
    user = await get_user_by_id(str(current_user.id))
    if user and user.persona:
        user.persona.ai_insights = insights
        await upsert_user({
            "_id": user.id,
            "open_id": user.open_id,
            "persona": user.persona.dict()
        })
    
    return AIAnalysisResponse(insights=insights)


@router.get("/history")
async def get_history(current_user = Depends(get_current_user)):
    """Get AI conversation history"""
    history = await get_user_ai_history(str(current_user.id), 20)
    return history
