from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from api.models import UserPersonaModel
from api.database import get_user_by_id, update_user, upsert_user
from api.deps import get_current_user

router = APIRouter()


@router.get("/me")
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.put("/me")
async def update_current_user(update_data: dict, current_user = Depends(get_current_user)):
    """Update current user"""
    update_data["updated_at"] = datetime.utcnow()
    await update_user(str(current_user.id), update_data)
    return {"success": True}


@router.post("/persona")
async def set_persona(persona_data: UserPersonaModel, current_user = Depends(get_current_user)):
    """Set user persona (onboarding)"""
    await update_user(str(current_user.id), {
        "persona": persona_data.dict(),
        "onboarding_completed": True,
        "updated_at": datetime.utcnow(),
    })
    return {"success": True, "message": "Persona set"}


@router.get("/persona")
async def get_persona(current_user = Depends(get_current_user)):
    """Get user persona"""
    user = await get_user_by_id(str(current_user.id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.persona
