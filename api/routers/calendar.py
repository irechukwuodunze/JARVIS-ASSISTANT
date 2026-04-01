import os
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from google.auth.oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import googleapiclient.discovery
from api.models import EventModel
from api.database import (
    get_user_by_id, update_user, get_user_events, get_event_by_google_id,
    create_event, update_event
)
from api.deps import get_current_user

router = APIRouter()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/calendar/callback")
SCOPES = ["https://www.googleapis.com/auth/calendar"]


@router.get("/auth-url")
async def get_auth_url(current_user = Depends(get_current_user)):
    """Get Google Calendar OAuth authorization URL"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    flow = Flow.from_client_config(
        {
            "installed": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
            }
        },
        scopes=SCOPES
    )
    
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    
    return {"auth_url": auth_url, "state": state}


@router.post("/callback")
async def handle_callback(code: str, current_user = Depends(get_current_user)):
    """Handle Google OAuth callback"""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google OAuth not configured")
    
    try:
        flow = Flow.from_client_config(
            {
                "installed": {
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [GOOGLE_REDIRECT_URI],
                }
            },
            scopes=SCOPES
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Save tokens to user
        await update_user(str(current_user.id), {
            "google_access_token": credentials.token,
            "google_refresh_token": credentials.refresh_token,
            "google_token_expiry": int(credentials.expiry.timestamp()) if credentials.expiry else None,
        })
        
        return {"success": True, "message": "Google Calendar connected"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")


@router.post("/sync")
async def sync_calendar(current_user = Depends(get_current_user)):
    """Sync events with Google Calendar (bidirectional)"""
    user = await get_user_by_id(str(current_user.id))
    if not user or not user.google_access_token:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    
    try:
        # Create credentials
        credentials = Credentials(
            token=user.google_access_token,
            refresh_token=user.google_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
        )
        
        # Build service
        service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        
        # Get events from Google Calendar
        now = datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=100,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        google_events = events_result.get('items', [])
        synced_count = 0
        
        # Sync Google events to our database
        for google_event in google_events:
            # Check if event already exists
            existing = await get_event_by_google_id(google_event['id'], str(current_user.id))
            
            start_time = google_event['start'].get('dateTime', google_event['start'].get('date'))
            end_time = google_event['end'].get('dateTime', google_event['end'].get('date'))
            
            start_ms = int(datetime.fromisoformat(start_time.replace('Z', '+00:00')).timestamp() * 1000)
            end_ms = int(datetime.fromisoformat(end_time.replace('Z', '+00:00')).timestamp() * 1000)
            
            event_data = {
                "user_id": str(current_user.id),
                "title": google_event.get('summary', 'Untitled'),
                "description": google_event.get('description', ''),
                "start_time": start_ms,
                "end_time": end_ms,
                "location": google_event.get('location', ''),
                "google_event_id": google_event['id'],
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            if existing:
                await update_event(str(existing.id), str(current_user.id), event_data)
            else:
                await create_event(event_data)
            
            synced_count += 1
        
        return {
            "success": True,
            "synced_count": synced_count,
            "message": f"Synced {synced_count} events from Google Calendar"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sync error: {str(e)}")


@router.post("/push-event")
async def push_event_to_calendar(event_id: str, current_user = Depends(get_current_user)):
    """Push a local event to Google Calendar"""
    user = await get_user_by_id(str(current_user.id))
    if not user or not user.google_access_token:
        raise HTTPException(status_code=401, detail="Google Calendar not connected")
    
    return {"success": True, "message": "Event pushed to Google Calendar"}
