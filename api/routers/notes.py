from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from api.models import NoteModel, NoteCreateRequest
from api.database import (
    create_note, get_user_notes, get_note, update_note, delete_note
)
from api.deps import get_current_user

router = APIRouter()


@router.get("/")
async def list_notes(current_user = Depends(get_current_user)):
    """List user notes"""
    notes = await get_user_notes(str(current_user.id))
    return notes


@router.post("/")
async def create_new_note(note_data: NoteCreateRequest, current_user = Depends(get_current_user)):
    """Create new note"""
    note_dict = {
        "user_id": str(current_user.id),
        **note_data.dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    note_id = await create_note(note_dict)
    return {"id": note_id}


@router.get("/{note_id}")
async def get_note_detail(note_id: str, current_user = Depends(get_current_user)):
    """Get note details"""
    note = await get_note(note_id, str(current_user.id))
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.put("/{note_id}")
async def update_note_detail(note_id: str, note_data: dict, current_user = Depends(get_current_user)):
    """Update note"""
    existing = await get_note(note_id, str(current_user.id))
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")
    
    note_data["updated_at"] = datetime.utcnow()
    await update_note(note_id, str(current_user.id), note_data)
    return {"success": True}


@router.delete("/{note_id}")
async def delete_note_detail(note_id: str, current_user = Depends(get_current_user)):
    """Delete note"""
    existing = await get_note(note_id, str(current_user.id))
    if not existing:
        raise HTTPException(status_code=404, detail="Note not found")
    
    await delete_note(note_id, str(current_user.id))
    return {"success": True}
