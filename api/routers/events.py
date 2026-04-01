from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from api.models import EventModel, EventCreateRequest, EventUpdateRequest
from api.database import (
    create_event, get_event, get_user_events, update_event, delete_event, log_behavior_event
)
from api.deps import get_current_user

router = APIRouter()


@router.get("/")
async def list_events(start_time: int | None = None, end_time: int | None = None, current_user = Depends(get_current_user)):
    """List user events"""
    events = await get_user_events(str(current_user.id), start_time, end_time)
    return events


@router.post("/")
async def create_new_event(event_data: EventCreateRequest, current_user = Depends(get_current_user)):
    """Create new event"""
    event_dict = {
        "user_id": str(current_user.id),
        **event_data.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    event_id = await create_event(event_dict)
    await log_behavior_event({
        "user_id": str(current_user.id),
        "event_id": event_id,
        "action": "created",
        "metadata": {"title": event_data.title, "category": event_data.category},
        "created_at": datetime.utcnow(),
    })
    return {"id": event_id}


@router.get("/{event_id}")
async def get_event_detail(event_id: str, current_user = Depends(get_current_user)):
    """Get event details"""
    event = await get_event(event_id, str(current_user.id))
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/{event_id}")
async def update_event_detail(event_id: str, event_data: EventUpdateRequest, current_user = Depends(get_current_user)):
    """Update event"""
    existing = await get_event(event_id, str(current_user.id))
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_dict = event_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.utcnow()
    
    await update_event(event_id, str(current_user.id), update_dict)
    
    # Log behavior if time was changed
    if event_data.start_time and event_data.start_time != existing.start_time:
        await log_behavior_event({
            "user_id": str(current_user.id),
            "event_id": event_id,
            "action": "moved",
            "original_start_time": existing.start_time,
            "new_start_time": event_data.start_time,
            "reason": event_data.reason,
            "created_at": datetime.utcnow(),
        })
    
    if event_data.status == "completed":
        await log_behavior_event({
            "user_id": str(current_user.id),
            "event_id": event_id,
            "action": "completed",
            "created_at": datetime.utcnow(),
        })
    
    return {"success": True}


@router.delete("/{event_id}")
async def delete_event_detail(event_id: str, current_user = Depends(get_current_user)):
    """Delete event"""
    existing = await get_event(event_id, str(current_user.id))
    if not existing:
        raise HTTPException(status_code=404, detail="Event not found")
    
    await delete_event(event_id, str(current_user.id))
    await log_behavior_event({
        "user_id": str(current_user.id),
        "event_id": event_id,
        "action": "deleted",
        "created_at": datetime.utcnow(),
    })
    return {"success": True}
