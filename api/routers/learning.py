import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
import google.generativeai as genai
from api.models import (
    WeeklyAutopsyModel, BehaviorAnalysisModel, UserModel
)
from api.database import (
    get_user_by_id, update_user, get_user_events, get_mood_logs_by_date_range,
    get_expenses_by_date_range, get_behavior_logs_by_date_range, create_weekly_autopsy
)
from api.deps import get_current_user

router = APIRouter()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)


@router.post("/weekly-autopsy")
async def generate_weekly_autopsy(current_user = Depends(get_current_user)):
    """Generate weekly autopsy report with AI analysis"""
    try:
        user = await get_user_by_id(str(current_user.id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get last 7 days of data
        now = datetime.utcnow()
        week_start = now - timedelta(days=7)
        
        events = await get_user_events(str(current_user.id), week_start, now)
        mood_logs = await get_mood_logs_by_date_range(str(current_user.id), week_start, now)
        expenses = await get_expenses_by_date_range(str(current_user.id), week_start, now)
        behavior_logs = await get_behavior_logs_by_date_range(str(current_user.id), week_start, now)
        
        # Analyze high efficiency blocks
        high_efficiency_blocks = []
        for log in mood_logs:
            if log.efficiency_score >= 80:
                high_efficiency_blocks.append({
                    "time": log.created_at.isoformat(),
                    "mood": str(log.mood_level),
                    "efficiency": log.efficiency_score,
                })
        
        # Analyze procrastination patterns
        procrastination_patterns = []
        for behavior in behavior_logs:
            if behavior.action == "moved":
                procrastination_patterns.append({
                    "event": behavior.event_id,
                    "reason": behavior.reason,
                    "timestamp": behavior.created_at.isoformat(),
                })
        
        # Analyze unnecessary spending
        unnecessary_spending = []
        for expense in expenses:
            if expense.is_flagged:
                unnecessary_spending.append({
                    "amount": expense.amount,
                    "category": expense.ai_categorization,
                    "warning": expense.ai_warning,
                })
        
        # Calculate mood-time correlation
        mood_time_correlation = {}
        for log in mood_logs:
            hour = log.created_at.hour
            mood = str(log.mood_level)
            key = f"{mood}_{hour}"
            if key not in mood_time_correlation:
                mood_time_correlation[key] = []
            mood_time_correlation[key].append(log.efficiency_score)
        
        # Calculate phase efficiency
        phase_efficiency = {}
        for event in events:
            phase = event.project_phase or "Other"
            if phase not in phase_efficiency:
                phase_efficiency[phase] = []
            # Calculate efficiency based on mood logs during event time
            for log in mood_logs:
                if event.start_time <= log.created_at.timestamp() * 1000 <= event.end_time:
                    phase_efficiency[phase].append(log.efficiency_score)
        
        # Average phase efficiency
        avg_phase_efficiency = {}
        for phase, scores in phase_efficiency.items():
            avg_phase_efficiency[phase] = sum(scores) / len(scores) if scores else 0
        
        # Calculate total efficiency
        total_efficiency = sum(log.efficiency_score for log in mood_logs) / len(mood_logs) if mood_logs else 0
        
        # Generate AI strategy using Gemini
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        persona_context = ""
        if user.persona:
            persona_context = f"""User Profile:
- Daily Goals: {', '.join(user.persona.daily_goals)}
- Procrastination Task: {user.persona.procrastination_task}
- Focus Hours: {', '.join(user.persona.focus_hours)}
- Monthly Budget: £{user.persona.monthly_budget}
- Hourly Rate: £{user.persona.hourly_rate}
"""
        
        prompt = f"""You are a Savage PA & CFO. Generate a brutal, honest weekly autopsy report.

{persona_context}

Weekly Data:
- High Efficiency Blocks: {len(high_efficiency_blocks)} blocks at 80%+ efficiency
- Procrastination Events: {len(procrastination_patterns)} times events were moved
- Unnecessary Spending: £{sum(e['amount'] for e in unnecessary_spending):.2f} flagged
- Total Efficiency Score: {total_efficiency:.1f}%
- Phase Performance: {avg_phase_efficiency}

Generate a JSON response:
{{
    "strategy": "Specific, actionable strategy for next week (2-3 sentences)",
    "key_insights": ["insight 1", "insight 2", "insight 3"],
    "warnings": ["warning 1", "warning 2"],
    "recommendations": ["recommendation 1", "recommendation 2"]
}}

Be direct, reference specific numbers, and don't sugarcoat the analysis."""
        
        response = model.generate_content(prompt)
        
        import json
        try:
            strategy_data = json.loads(response.text)
        except:
            strategy_data = {
                "strategy": response.text,
                "key_insights": [],
                "warnings": [],
                "recommendations": [],
            }
        
        # Create autopsy record
        autopsy = {
            "user_id": str(current_user.id),
            "week_start": week_start,
            "week_end": now,
            "high_efficiency_blocks": high_efficiency_blocks,
            "procrastination_patterns": procrastination_patterns,
            "unnecessary_spending": unnecessary_spending,
            "ai_generated_strategy": strategy_data.get("strategy", ""),
            "mood_time_correlation": mood_time_correlation,
            "phase_efficiency": avg_phase_efficiency,
            "total_efficiency_score": total_efficiency,
            "generated_at": datetime.utcnow(),
        }
        
        autopsy_id = await create_weekly_autopsy(autopsy)
        
        return {
            "id": autopsy_id,
            "success": True,
            "autopsy": autopsy,
            "strategy_data": strategy_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Autopsy generation error: {str(e)}")


@router.post("/analyze-behavior")
async def analyze_behavior(days: int = 7, current_user = Depends(get_current_user)):
    """Analyze user behavior patterns and suggest persona updates"""
    try:
        user = await get_user_by_id(str(current_user.id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)
        
        # Get behavior data
        behavior_logs = await get_behavior_logs_by_date_range(str(current_user.id), start_date, now)
        mood_logs = await get_mood_logs_by_date_range(str(current_user.id), start_date, now)
        events = await get_user_events(str(current_user.id), start_date, now)
        
        # Analyze patterns
        insights = []
        
        # Procrastination analysis
        moved_count = sum(1 for b in behavior_logs if b.action == "moved")
        if moved_count > 5:
            insights.append(f"You moved {moved_count} events in {days} days. Pattern detected.")
        
        # Energy pattern analysis
        low_energy_events = sum(1 for e in events if str(e.energy_level) == "low")
        if low_energy_events > len(events) * 0.3:
            insights.append("You're consistently low on energy. Consider adjusting sleep or workout schedule.")
        
        # Mood analysis
        drained_count = sum(1 for m in mood_logs if str(m.mood_level) == "drained")
        if drained_count > len(mood_logs) * 0.4:
            insights.append("You're feeling drained frequently. Time to reassess workload.")
        
        # Generate AI recommendations
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""Analyze this user's behavior and suggest persona updates.

Insights: {', '.join(insights)}
Events Moved: {moved_count}
Low Energy Events: {low_energy_events}
Drained Mood Count: {drained_count}

Suggest updates to:
1. Notification cadence (currently {user.persona.notification_cadence if user.persona else [30, 15, 5]})
2. Focus hours (currently {user.persona.focus_hours if user.persona else []})
3. Procrastination task (currently {user.persona.procrastination_task if user.persona else 'None'})

Respond in JSON:
{{
    "new_notification_cadence": [minutes],
    "new_focus_hours": ["HH:MM-HH:MM"],
    "new_procrastination_task": "task",
    "reasoning": "explanation"
}}"""
        
        response = model.generate_content(prompt)
        
        import json
        try:
            recommendations = json.loads(response.text)
        except:
            recommendations = {
                "new_notification_cadence": user.persona.notification_cadence if user.persona else [30, 15, 5],
                "new_focus_hours": user.persona.focus_hours if user.persona else [],
                "new_procrastination_task": user.persona.procrastination_task if user.persona else "",
                "reasoning": response.text,
            }
        
        return {
            "success": True,
            "insights": insights,
            "recommendations": recommendations,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Behavior analysis error: {str(e)}")


@router.post("/update-persona")
async def update_persona_from_learning(current_user = Depends(get_current_user)):
    """Update user persona based on learning analysis"""
    try:
        user = await get_user_by_id(str(current_user.id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Run behavior analysis
        analysis = await analyze_behavior(7, current_user)
        
        if analysis["success"] and "recommendations" in analysis:
            recs = analysis["recommendations"]
            
            # Update persona
            if user.persona:
                user.persona.notification_cadence = recs.get("new_notification_cadence", user.persona.notification_cadence)
                user.persona.focus_hours = recs.get("new_focus_hours", user.persona.focus_hours)
                user.persona.procrastination_task = recs.get("new_procrastination_task", user.persona.procrastination_task)
                user.persona.adaptive_insights = analysis.get("insights", [])
            
            # Save updated user
            await update_user(str(current_user.id), user.dict())
            
            return {
                "success": True,
                "message": "Persona updated based on learning",
                "updates": recs,
            }
        
        return {"success": False, "message": "Could not update persona"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Persona update error: {str(e)}")
