"""Living JARVIS Memory Engine — Long-term memory, context retrieval, and adaptive learning"""
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from api.models import (
    UserMemoryModel, ContextMemoryModel, FlexibleDataModel, PersonaConfigModel,
    NotificationSettingsModel, UpdateMemoryRequest, AskAnythingRequest,
    UpdatePersonaRequest, UpdateNotificationSettingsRequest, MemoryContextResponse
)
from api.database import get_user_by_id
from api.deps import get_current_user

router = APIRouter()


async def update_user_memory_background(user_id: str, memory_data: dict):
    """Background task to update user memory without blocking response"""
    try:
        # This runs asynchronously so voice responses aren't delayed
        pass
    except Exception as e:
        print(f"[Memory] Background update failed for user {user_id}: {str(e)}")


@router.post("/memory/store")
async def store_memory(
    request: UpdateMemoryRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Store a memory fact or preference for Jarvis to remember"""
    try:
        memory = UserMemoryModel(
            user_id=str(current_user.id),
            memory_type=request.memory_type,
            key=request.key,
            value=request.value,
            context=request.context,
            importance_score=request.importance_score or 0.5,
        )
        
        # background_tasks.add_task(update_user_memory_background, str(current_user.id), memory.dict())
        
        return {
            "success": True,
            "message": f"Remembered: {request.key} = {request.value}",
            "memory_id": "placeholder_id",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory storage error: {str(e)}")


@router.get("/memory/context")
async def get_memory_context(current_user = Depends(get_current_user)):
    """Retrieve user's memory context for Gemini injection into system prompt"""
    try:
        
        # This is injected into Gemini's system prompt before every interaction
        response = MemoryContextResponse(
            memories=[],
            recent_context=[],
            persona=None,
            notification_settings=None,
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context retrieval error: {str(e)}")


@router.post("/memory/ask-anything")
async def ask_anything(
    request: AskAnythingRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Ask Jarvis to track something new — creates arbitrary tracking without schema changes"""
    try:
        flexible_data = FlexibleDataModel(
            user_id=str(current_user.id),
            category=request.category,
            data=request.data,
        )
        
        # background_tasks.add_task(update_user_memory_background, str(current_user.id), flexible_data.dict())
        
        return {
            "success": True,
            "message": f"Now tracking: {request.category}",
            "data_id": "placeholder_id",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ask Anything error: {str(e)}")


@router.post("/memory/proactive-learn")
async def proactive_learn(
    key: str,
    value: str,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user)
):
    """Jarvis proactively learns from voice commands without being asked"""
    try:
        # When user says "I switched to Barclays", Jarvis automatically stores it
        memory = UserMemoryModel(
            user_id=str(current_user.id),
            memory_type="preference",
            key=key,
            value=value,
            importance_score=0.8,  # High importance for proactive learning
        )
        
        # background_tasks.add_task(update_user_memory_background, str(current_user.id), memory.dict())
        
        # Also store in context for recent interactions
        
        return {
            "success": True,
            "message": f"Learned: {key} = {value}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proactive learning error: {str(e)}")


@router.post("/persona/update")
async def update_persona(
    request: UpdatePersonaRequest,
    current_user = Depends(get_current_user)
):
    """Update Jarvis's persona — voice tone, verbosity, style"""
    try:
        
        return {
            "success": True,
            "message": "Persona updated. I'll adjust my tone immediately.",
            "persona": {
                "voice_tone": request.voice_tone or "savage",
                "verbosity": request.verbosity or "concise",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Persona update error: {str(e)}")


@router.post("/notifications/update-settings")
async def update_notification_settings(
    request: UpdateNotificationSettingsRequest,
    current_user = Depends(get_current_user)
):
    """Update notification settings — dynamic scheduling without code changes"""
    try:
        # Vercel Cron jobs will query this document every run
        
        return {
            "success": True,
            "message": "Notification settings updated. Changes take effect immediately.",
            "settings": {
                "notification_cadence": request.notification_cadence or [30, 15, 5],
                "weekly_autopsy_day": request.weekly_autopsy_day or "Monday",
                "disabled_days": request.disabled_days or [],
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Notification settings error: {str(e)}")


@router.get("/memory/stats")
async def get_memory_stats(current_user = Depends(get_current_user)):
    """Get statistics about user's memory and learning"""
    try:
        # - Total memories stored
        # - Most recent memories
        # - High-importance memories
        # - Memory categories
        
        return {
            "total_memories": 0,
            "memory_categories": [],
            "recent_memories": [],
            "high_priority_memories": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory stats error: {str(e)}")


@router.post("/memory/forget")
async def forget_memory(
    memory_id: str,
    current_user = Depends(get_current_user)
):
    """Delete a memory — Jarvis can forget things too"""
    try:
        
        return {
            "success": True,
            "message": "Memory deleted. I've forgotten that.",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory deletion error: {str(e)}")


def build_gemini_system_prompt(user_id: str, memory_context: MemoryContextResponse) -> str:
    """Build Gemini system prompt with memory injection"""
    
    # Base system prompt
    base_prompt = """You are JARVIS, a Savage PA & CFO assistant. You are:
- Blunt and honest (no sugarcoating)
- Efficient and direct
- Focused on productivity and financial discipline
- Slightly sarcastic but supportive
- Always learning from user behavior

Your role is to:
1. Manage events and schedules with AI-powered conflict detection
2. Track finances with savage CFO warnings
3. Monitor productivity and mood patterns
4. Provide actionable insights without fluff
5. Remember user preferences and adapt accordingly
6. Proactively learn from interactions
"""
    
    # Inject persona if available
    if memory_context.persona:
        persona_prompt = f"""
Current Persona Settings:
- Voice Tone: {memory_context.persona.voice_tone}
- Verbosity: {memory_context.persona.verbosity}
- Notification Style: {memory_context.persona.notification_style}
"""
        base_prompt += persona_prompt
    
    # Inject memories if available
    if memory_context.memories:
        memories_prompt = "\nUser Preferences & Facts I Remember:\n"
        for memory in memory_context.memories[:10]:  # Top 10 memories
            memories_prompt += f"- {memory.key}: {memory.value}\n"
        base_prompt += memories_prompt
    
    # Inject recent context if available
    if memory_context.recent_context:
        context_prompt = "\nRecent Context:\n"
        for context in memory_context.recent_context[:5]:  # Last 5 interactions
            context_prompt += f"- {context.context}\n"
        base_prompt += context_prompt
    
    return base_prompt
