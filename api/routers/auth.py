import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query
from google.auth.transport.requests import Request
from google.oauth2.id_token import verify_oauth2_token
import jwt

from api.models import UserModel
from api.database import upsert_user, get_user_by_open_id
from api.deps import create_access_token

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")


@router.post("/google-login")
async def google_login(token: str):
    """
    Verify Google OAuth token and create session
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    try:
        # Verify the token
        idinfo = verify_oauth2_token(token, Request(), GOOGLE_CLIENT_ID)
        
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            raise ValueError("Wrong issuer.")
        
        # Extract user info
        open_id = idinfo["sub"]
        email = idinfo.get("email")
        name = idinfo.get("name")
        
        # Upsert user
        user_data = {
            "open_id": open_id,
            "email": email,
            "name": name,
            "login_method": "google",
            "last_signed_in": datetime.utcnow(),
        }
        user_id = await upsert_user(user_data)
        
        # Create JWT token
        access_token = create_access_token(user_id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user_id,
                "email": email,
                "name": name,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")


@router.post("/logout")
async def logout():
    """
    Logout endpoint (client-side token deletion)
    """
    return {"status": "logged_out"}


@router.post("/refresh-token")
async def refresh_token(refresh_token: str):
    """
    Refresh JWT access token
    """
    try:
        payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Create new access token
        access_token = create_access_token(user_id)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
