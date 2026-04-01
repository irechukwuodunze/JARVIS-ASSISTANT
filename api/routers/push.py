import os
import json
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pywebpush import webpush
from api.models import PushSubscriptionRequest
from api.database import (
    save_push_subscription, get_user_push_subscriptions,
    deactivate_push_subscription, get_all_active_push_subscriptions,
    get_user_events
)
from api.deps import get_current_user

router = APIRouter()

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY", "")


@router.post("/subscribe")
async def subscribe_to_push(request: PushSubscriptionRequest, current_user = Depends(get_current_user)):
    """Subscribe to push notifications"""
    subscription_data = {
        "user_id": str(current_user.id),
        "endpoint": request.endpoint,
        "p256dh": request.exponent_public_key,
        "auth": request.auth,
        "user_agent": None,
        "is_active": True,
        "created_at": datetime.utcnow(),
    }
    
    await save_push_subscription(subscription_data)
    return {"success": True, "message": "Subscribed to push notifications"}


@router.post("/unsubscribe")
async def unsubscribe_from_push(endpoint: str, current_user = Depends(get_current_user)):
    """Unsubscribe from push notifications"""
    await deactivate_push_subscription(endpoint)
    return {"success": True, "message": "Unsubscribed from push notifications"}


@router.post("/send-nudge")
async def send_nudge(event_id: str, nudge_type: str, current_user = Depends(get_current_user)):
    """Send a push notification nudge (30-15-5 cadence)"""
    if not VAPID_PUBLIC_KEY or not VAPID_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="Web Push not configured")
    
    subscriptions = await get_user_push_subscriptions(str(current_user.id))
    if not subscriptions:
        return {"success": False, "message": "No active subscriptions"}
    
    # Determine nudge message
    messages = {
        "30": "Gentle Prep: Your event is in 30 minutes. Finish up what you're doing.",
        "15": "Friction Warning: 15 minutes. Get your water and open your laptop.",
        "5": "The Hammer: 5 minutes. Drop everything. It's time to start.",
    }
    
    message = messages.get(nudge_type, "Event reminder")
    
    # Send to all subscriptions
    for sub in subscriptions:
        try:
            web_push_result = webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {
                        "p256dh": sub.p256dh,
                        "auth": sub.auth,
                    }
                },
                data=json.dumps({
                    "title": "JARVIS",
                    "body": message,
                    "tag": f"event-{event_id}",
                    "data": {"event_id": event_id, "nudge_type": nudge_type},
                }),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:admin@jarvis.local"},
            )
        except Exception as e:
            print(f"Failed to send push: {e}")
    
    return {"success": True, "message": f"Sent {len(subscriptions)} nudges"}
