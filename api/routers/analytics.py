import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
import google.generativeai as genai
from api.models import EfficiencyMetricsResponse, MoodLogRequest
from api.database import (
    get_user_by_id, get_user_events, create_mood_log, get_mood_logs_by_date_range,
    get_behavior_logs_by_date_range
)
from api.deps import get_current_user

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)


@router.post("/log-mood")
async def log_mood(mood_data: MoodLogRequest, current_user = Depends(get_current_user)):
    """Log mood and energy level for correlation analysis"""
    try:
        mood_log = {
            "user_id": str(current_user.id),
            "mood_level": str(mood_data.mood_level),
            "energy_level": str(mood_data.energy_level),
            "efficiency_score": mood_data.efficiency_score or 0.0,
            "notes": mood_data.notes,
            "event_id": mood_data.event_id,
            "created_at": datetime.utcnow(),
        }
        
        mood_id = await create_mood_log(mood_log)
        return {"id": mood_id, "success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mood logging error: {str(e)}")


@router.get("/efficiency-metrics")
async def get_efficiency_metrics(
    days: int = 7,
    current_user = Depends(get_current_user)
):
    """Get efficiency metrics and mood-time correlation"""
    try:
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        # Get mood logs
        mood_logs = await get_mood_logs_by_date_range(str(current_user.id), start_date, now)
        
        if not mood_logs:
            return EfficiencyMetricsResponse(
                average_efficiency_score=0.0,
                peak_efficiency_time=None,
                peak_efficiency_mood=None,
                low_efficiency_time=None,
                low_efficiency_mood=None,
                mood_time_correlation={}
            )
        
        # Calculate averages
        avg_efficiency = sum(m.efficiency_score for m in mood_logs) / len(mood_logs)
        
        # Find peak efficiency
        peak_log = max(mood_logs, key=lambda m: m.efficiency_score)
        low_log = min(mood_logs, key=lambda m: m.efficiency_score)
        
        # Group by hour and mood
        hour_efficiency = {}
        mood_efficiency = {}
        
        for log in mood_logs:
            hour = log.created_at.hour
            mood = str(log.mood_level)
            
            if hour not in hour_efficiency:
                hour_efficiency[hour] = []
            hour_efficiency[hour].append(log.efficiency_score)
            
            if mood not in mood_efficiency:
                mood_efficiency[mood] = []
            mood_efficiency[mood].append(log.efficiency_score)
        
        # Calculate correlations
        mood_time_correlation = {}
        for mood, scores in mood_efficiency.items():
            avg_score = sum(scores) / len(scores)
            mood_time_correlation[mood] = avg_score
        
        peak_hour = max(hour_efficiency.items(), key=lambda x: sum(x[1]) / len(x[1]))[0]
        peak_time = f"{peak_hour:02d}:00"
        
        return EfficiencyMetricsResponse(
            average_efficiency_score=avg_efficiency,
            peak_efficiency_time=peak_time,
            peak_efficiency_mood=str(peak_log.mood_level),
            low_efficiency_time=f"{low_log.created_at.hour:02d}:00",
            low_efficiency_mood=str(low_log.mood_level),
            mood_time_correlation=mood_time_correlation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Metrics error: {str(e)}")


@router.get("/productivity-heatmap")
async def get_productivity_heatmap(
    days: int = 7,
    current_user = Depends(get_current_user)
):
    """Get productivity heatmap data (hour x day grid)"""
    try:
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        # Get events and mood logs
        events = await get_user_events(str(current_user.id), start_date, now)
        mood_logs = await get_mood_logs_by_date_range(str(current_user.id), start_date, now)
        
        # Build heatmap: day_of_week x hour
        heatmap = {}
        
        for log in mood_logs:
            day_name = log.created_at.strftime("%A")
            hour = log.created_at.hour
            key = f"{day_name}_{hour}"
            
            if key not in heatmap:
                heatmap[key] = []
            heatmap[key].append(log.efficiency_score)
        
        # Average scores per cell
        heatmap_data = {}
        for key, scores in heatmap.items():
            heatmap_data[key] = sum(scores) / len(scores)
        
        return {"heatmap": heatmap_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap error: {str(e)}")


@router.get("/phase-efficiency")
async def get_phase_efficiency(
    days: int = 7,
    current_user = Depends(get_current_user)
):
    """Get efficiency by project phase (Research, Design, Tech, Presentation)"""
    try:
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        # Get events with project phases
        events = await get_user_events(str(current_user.id), start_date, now)
        
        phase_data = {}
        for event in events:
            phase = event.project_phase or "Other"
            if phase not in phase_data:
                phase_data[phase] = {"total_time": 0, "efficiency_scores": []}
            
            # Calculate event duration
            duration = (event.end_time - event.start_time) / (1000 * 60)  # Convert ms to minutes
            phase_data[phase]["total_time"] += duration
            
            # Add efficiency if available
            if hasattr(event, "efficiency_score"):
                phase_data[phase]["efficiency_scores"].append(event.efficiency_score)
        
        # Calculate averages
        phase_efficiency = {}
        for phase, data in phase_data.items():
            avg_efficiency = sum(data["efficiency_scores"]) / len(data["efficiency_scores"]) if data["efficiency_scores"] else 0
            phase_efficiency[phase] = {
                "total_time_minutes": data["total_time"],
                "average_efficiency": avg_efficiency,
                "time_percentage": 0  # Will be calculated on frontend
            }
        
        return {"phase_efficiency": phase_efficiency}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phase efficiency error: {str(e)}")
