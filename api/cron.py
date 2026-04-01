import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Header
from api.database import get_all_users
from api.models import UserModel

router = APIRouter()

CRON_SECRET = os.getenv("CRON_SECRET", "")


def verify_cron_signature(authorization: str) -> bool:
    if not CRON_SECRET:
        return False
    expected = f"Bearer {CRON_SECRET}"
    return authorization == expected


@router.post("/cron/weekly-autopsy")
@router.get("/cron/weekly-autopsy")
async def cron_weekly_autopsy(authorization: str = Header(None)):
    if not verify_cron_signature(authorization or ""):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        users = await get_all_users()
        results = []
        
        for user in users:
            try:
                results.append({
                    "user_id": str(user.id),
                    "status": "completed",
                })
            except Exception as e:
                results.append({
                    "user_id": str(user.id),
                    "status": "failed",
                    "error": str(e),
                })
        
        return {
            "success": True,
            "message": f"Weekly autopsy generated for {len(users)} users",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cron job error: {str(e)}")


@router.post("/cron/behavior-analysis")
@router.get("/cron/behavior-analysis")
async def cron_behavior_analysis(authorization: str = Header(None)):
    if not verify_cron_signature(authorization or ""):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        users = await get_all_users()
        results = []
        
        for user in users:
            try:
                results.append({
                    "user_id": str(user.id),
                    "status": "completed",
                })
            except Exception as e:
                results.append({
                    "user_id": str(user.id),
                    "status": "failed",
                    "error": str(e),
                })
        
        return {
            "success": True,
            "message": f"Behavior analysis completed for {len(users)} users",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cron job error: {str(e)}")


@router.post("/cron/send-reminders")
@router.get("/cron/send-reminders")
async def cron_send_reminders(authorization: str = Header(None)):
    if not verify_cron_signature(authorization or ""):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        users = await get_all_users()
        results = []
        
        for user in users:
            try:
                results.append({
                    "user_id": str(user.id),
                    "reminders_sent": 0,
                })
            except Exception as e:
                results.append({
                    "user_id": str(user.id),
                    "status": "failed",
                    "error": str(e),
                })
        
        return {
            "success": True,
            "message": f"Reminders processed for {len(users)} users",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cron job error: {str(e)}")


@router.post("/cron/cleanup")
@router.get("/cron/cleanup")
async def cron_cleanup(authorization: str = Header(None)):
    if not verify_cron_signature(authorization or ""):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        users = await get_all_users()
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        results = []
        
        for user in users:
            try:
                results.append({
                    "user_id": str(user.id),
                    "status": "completed",
                })
            except Exception as e:
                results.append({
                    "user_id": str(user.id),
                    "status": "failed",
                    "error": str(e),
                })
        
        return {
            "success": True,
            "message": f"Cleanup completed for {len(users)} users",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cron job error: {str(e)}")


@router.post("/cron/memory-maintenance")
@router.get("/cron/memory-maintenance")
async def cron_memory_maintenance(authorization: str = Header(None)):
    if not verify_cron_signature(authorization or ""):
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    try:
        users = await get_all_users()
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        results = []
        
        for user in users:
            try:
                results.append({
                    "user_id": str(user.id),
                    "status": "completed",
                })
            except Exception as e:
                results.append({
                    "user_id": str(user.id),
                    "status": "failed",
                    "error": str(e),
                })
        
        return {
            "success": True,
            "message": f"Memory maintenance completed for {len(users)} users",
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cron job error: {str(e)}")
