import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
import google.generativeai as genai
from api.models import FocusModeCheckInRequest
from api.database import (
    create_focus_session, get_focus_session, update_focus_session,
    get_user_by_id, get_user_events
)
from api.deps import get_current_user

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)


@router.post("/start-focus-mode")
async def start_focus_mode(
    event_id: str,
    duration_minutes: int = 90,
    current_user = Depends(get_current_user)
):
    """Start a focus mode session (Deadman's Switch)"""
    try:
        # Calculate check-in intervals (Pomodoro-style: every 25 minutes)
        total_check_ins = max(1, duration_minutes // 25)
        
        focus_session = {
            "user_id": str(current_user.id),
            "event_id": event_id,
            "start_time": datetime.utcnow(),
            "duration_minutes": duration_minutes,
            "check_in_interval": 25,
            "check_ins_completed": 0,
            "total_check_ins_required": total_check_ins,
            "proof_of_work_submitted": False,
            "is_completed": False,
            "is_failed": False,
        }
        
        session_id = await create_focus_session(focus_session)
        
        return {
            "id": session_id,
            "success": True,
            "message": f"Focus mode started for {duration_minutes} minutes. Check in every 25 minutes.",
            "total_check_ins_required": total_check_ins,
            "next_check_in_at": (datetime.utcnow() + timedelta(minutes=25)).isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Focus mode error: {str(e)}")


@router.post("/check-in/{session_id}")
async def focus_mode_check_in(
    session_id: str,
    check_in_data: FocusModeCheckInRequest,
    current_user = Depends(get_current_user)
):
    """Check in during focus mode (Proof of Work)"""
    try:
        session = await get_focus_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(status_code=404, detail="Focus session not found")
        
        # Update check-in count
        new_check_ins = session.check_ins_completed + 1
        
        update_data = {
            "check_ins_completed": new_check_ins,
            "proof_of_work_submitted": bool(check_in_data.proof_of_work_image_url),
            "proof_of_work_image_url": check_in_data.proof_of_work_image_url,
        }
        
        # Check if all check-ins completed
        if new_check_ins >= session.total_check_ins_required:
            update_data["is_completed"] = True
        
        await update_focus_session(session_id, str(current_user.id), update_data)
        
        # Generate encouraging message with Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""Generate a brief, Savage PA motivational message for someone who just completed a focus check-in.
They've completed {new_check_ins} of {session.total_check_ins_required} check-ins.
Be direct, slightly sarcastic, and use specific numbers.
Keep it under 50 words."""
        
        response = model.generate_content(prompt)
        
        return {
            "success": True,
            "check_ins_completed": new_check_ins,
            "total_check_ins_required": session.total_check_ins_required,
            "is_completed": new_check_ins >= session.total_check_ins_required,
            "message": response.text,
            "next_check_in_at": (datetime.utcnow() + timedelta(minutes=25)).isoformat() if new_check_ins < session.total_check_ins_required else None,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check-in error: {str(e)}")


@router.post("/end-focus-mode/{session_id}")
async def end_focus_mode(session_id: str, current_user = Depends(get_current_user)):
    """End focus mode session"""
    try:
        session = await get_focus_session(session_id, str(current_user.id))
        if not session:
            raise HTTPException(status_code=404, detail="Focus session not found")
        
        # Check if all check-ins were completed
        is_failed = session.check_ins_completed < session.total_check_ins_required
        
        update_data = {
            "end_time": datetime.utcnow(),
            "is_completed": not is_failed,
            "is_failed": is_failed,
        }
        
        await update_focus_session(session_id, str(current_user.id), update_data)
        
        # Generate summary message
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        if is_failed:
            prompt = f"""Generate a Savage PA message for someone who failed their focus mode session.
They completed {session.check_ins_completed} of {session.total_check_ins_required} check-ins.
Be blunt about the failure, reference their goals, and suggest what went wrong.
Keep it under 100 words."""
        else:
            prompt = f"""Generate a Savage PA congratulatory message for someone who completed their focus mode session.
They completed all {session.total_check_ins_required} check-ins.
Be direct, slightly sarcastic, and reference their productivity.
Keep it under 100 words."""
        
        response = model.generate_content(prompt)
        
        return {
            "success": True,
            "is_completed": not is_failed,
            "is_failed": is_failed,
            "check_ins_completed": session.check_ins_completed,
            "total_check_ins_required": session.total_check_ins_required,
            "message": response.text,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"End focus mode error: {str(e)}")


@router.get("/focus-history")
async def get_focus_history(days: int = 7, current_user = Depends(get_current_user)):
    """Get focus mode history and stats"""
    try:
        return {
            "total_sessions": 0,
            "completed_sessions": 0,
            "failed_sessions": 0,
            "total_focus_time_minutes": 0,
            "average_check_in_rate": 0.0,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"History error: {str(e)}")
