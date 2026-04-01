import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from api.models import (
    UserModel, EventModel, NoteModel, BehaviorEventModel,
    PushSubscriptionModel, AIConversationModel, ExpenseModel,
    MoodLogModel, FocusModeSessionModel, WeeklyAutopsyModel
)

# MongoDB connection
MONGODB_URI = os.getenv("MONGODB_URI", "")
client: AsyncIOMotorClient = None
db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    global client, db
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable is not set")
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client.jarvis
    # Create indexes
    await db.users.create_index("open_id", unique=True)
    await db.events.create_index("user_id")
    await db.events.create_index("google_event_id")
    await db.notes.create_index("user_id")
    await db.behavior_events.create_index("user_id")
    await db.push_subscriptions.create_index("user_id")
    await db.ai_conversations.create_index("user_id")
    await db.expenses.create_index("user_id")
    await db.mood_logs.create_index("user_id")
    await db.focus_sessions.create_index("user_id")
    await db.weekly_autopsies.create_index("user_id")
    print("[Database] Connected to MongoDB")


async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("[Database] Closed MongoDB connection")


def get_db() -> AsyncIOMotorDatabase:
    if db is None:
        raise RuntimeError("Database not connected")
    return db


# ─── Users ────────────────────────────────────────────────────────────────────
async def upsert_user(user_data: dict) -> str:
    """Upsert user by open_id, return user ID"""
    result = await db.users.update_one(
        {"open_id": user_data["open_id"]},
        {"$set": user_data},
        upsert=True
    )
    if result.upserted_id:
        return str(result.upserted_id)
    # Get the user ID
    user = await db.users.find_one({"open_id": user_data["open_id"]})
    return str(user["_id"])


async def get_user_by_open_id(open_id: str) -> UserModel | None:
    """Get user by open_id"""
    user = await db.users.find_one({"open_id": open_id})
    if user:
        return UserModel(**user)
    return None


async def get_user_by_id(user_id: str) -> UserModel | None:
    """Get user by ID"""
    from bson import ObjectId
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        return UserModel(**user)
    return None


async def update_user(user_id: str, update_data: dict) -> None:
    """Update user fields"""
    from bson import ObjectId
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )


async def get_all_users() -> list[UserModel]:
    """Get all users"""
    users = await db.users.find().to_list(None)
    return [UserModel(**u) for u in users]


# ─── Events ───────────────────────────────────────────────────────────────────
async def create_event(event_data: dict) -> str:
    """Create event, return event ID"""
    result = await db.events.insert_one(event_data)
    return str(result.inserted_id)


async def get_event(event_id: str, user_id: str) -> EventModel | None:
    """Get event by ID and user_id"""
    from bson import ObjectId
    event = await db.events.find_one({
        "_id": ObjectId(event_id),
        "user_id": user_id
    })
    if event:
        return EventModel(**event)
    return None


async def get_user_events(user_id: str, start_time: int | None = None, end_time: int | None = None) -> list[EventModel]:
    """Get user events, optionally filtered by time range"""
    query = {"user_id": user_id, "status": {"$ne": "skipped"}}
    if start_time:
        query["end_time"] = {"$gte": start_time}
    if end_time:
        query["start_time"] = {"$lte": end_time}
    events = await db.events.find(query).sort("start_time", 1).to_list(None)
    return [EventModel(**e) for e in events]


async def update_event(event_id: str, user_id: str, update_data: dict) -> None:
    """Update event"""
    from bson import ObjectId
    await db.events.update_one(
        {"_id": ObjectId(event_id), "user_id": user_id},
        {"$set": update_data}
    )


async def delete_event(event_id: str, user_id: str) -> None:
    """Mark event as skipped (soft delete)"""
    from bson import ObjectId
    await db.events.update_one(
        {"_id": ObjectId(event_id), "user_id": user_id},
        {"$set": {"status": "skipped"}}
    )


async def get_event_by_google_id(google_event_id: str, user_id: str) -> EventModel | None:
    """Get event by Google Calendar ID"""
    event = await db.events.find_one({
        "google_event_id": google_event_id,
        "user_id": user_id
    })
    if event:
        return EventModel(**event)
    return None


# ─── Notes ────────────────────────────────────────────────────────────────────
async def create_note(note_data: dict) -> str:
    """Create note, return note ID"""
    result = await db.notes.insert_one(note_data)
    return str(result.inserted_id)


async def get_user_notes(user_id: str) -> list[NoteModel]:
    """Get all user notes"""
    notes = await db.notes.find({"user_id": user_id}).sort("updated_at", -1).to_list(None)
    return [NoteModel(**n) for n in notes]


async def get_note(note_id: str, user_id: str) -> NoteModel | None:
    """Get note by ID and user_id"""
    from bson import ObjectId
    note = await db.notes.find_one({
        "_id": ObjectId(note_id),
        "user_id": user_id
    })
    if note:
        return NoteModel(**note)
    return None


async def update_note(note_id: str, user_id: str, update_data: dict) -> None:
    """Update note"""
    from bson import ObjectId
    await db.notes.update_one(
        {"_id": ObjectId(note_id), "user_id": user_id},
        {"$set": update_data}
    )


async def delete_note(note_id: str, user_id: str) -> None:
    """Delete note"""
    from bson import ObjectId
    await db.notes.delete_one({
        "_id": ObjectId(note_id),
        "user_id": user_id
    })


# ─── Behavior Events ──────────────────────────────────────────────────────────
async def log_behavior_event(behavior_data: dict) -> None:
    """Log behavior event"""
    await db.behavior_events.insert_one(behavior_data)


async def get_user_behavior_events(user_id: str, limit: int = 50) -> list[BehaviorEventModel]:
    """Get user behavior events"""
    events = await db.behavior_events.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(None)
    return [BehaviorEventModel(**e) for e in events]


async def get_behavior_logs_by_date_range(user_id: str, start_date: datetime, end_date: datetime) -> list[BehaviorEventModel]:
    """Get behavior logs within a date range"""
    logs = await db.behavior_events.find({
        "user_id": user_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }).sort("created_at", -1).to_list(None)
    return [BehaviorEventModel(**l) for l in logs]


# ─── Push Subscriptions ───────────────────────────────────────────────────────
async def save_push_subscription(subscription_data: dict) -> None:
    """Save push subscription"""
    await db.push_subscriptions.update_one(
        {"endpoint": subscription_data["endpoint"]},
        {"$set": subscription_data},
        upsert=True
    )


async def get_user_push_subscriptions(user_id: str) -> list[PushSubscriptionModel]:
    """Get active push subscriptions for user"""
    subs = await db.push_subscriptions.find({
        "user_id": user_id,
        "is_active": True
    }).to_list(None)
    return [PushSubscriptionModel(**s) for s in subs]


async def get_all_active_push_subscriptions() -> list[PushSubscriptionModel]:
    """Get all active push subscriptions"""
    subs = await db.push_subscriptions.find({"is_active": True}).to_list(None)
    return [PushSubscriptionModel(**s) for s in subs]


async def deactivate_push_subscription(endpoint: str) -> None:
    """Deactivate push subscription"""
    await db.push_subscriptions.update_one(
        {"endpoint": endpoint},
        {"$set": {"is_active": False}}
    )


# ─── AI Conversations ─────────────────────────────────────────────────────────
async def save_ai_message(message_data: dict) -> None:
    """Save AI conversation message"""
    await db.ai_conversations.insert_one(message_data)


async def get_user_ai_history(user_id: str, limit: int = 20) -> list[AIConversationModel]:
    """Get user AI conversation history"""
    messages = await db.ai_conversations.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(None)
    return [AIConversationModel(**m) for m in messages]


# ─── Expenses ─────────────────────────────────────────────────────────────────
async def create_expense(expense_data: dict) -> str:
    """Create expense, return expense ID"""
    result = await db.expenses.insert_one(expense_data)
    return str(result.inserted_id)


async def get_user_expenses(user_id: str, limit: int = 100) -> list[ExpenseModel]:
    """Get user expenses"""
    expenses = await db.expenses.find({"user_id": user_id}).sort("created_at", -1).limit(limit).to_list(None)
    return [ExpenseModel(**e) for e in expenses]


async def get_expenses_by_date_range(user_id: str, start_date: datetime, end_date: datetime) -> list[ExpenseModel]:
    """Get expenses within a date range"""
    expenses = await db.expenses.find({
        "user_id": user_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }).sort("created_at", -1).to_list(None)
    return [ExpenseModel(**e) for e in expenses]


# ─── Mood Logs ─────────────────────────────────────────────────────────────────
async def create_mood_log(mood_data: dict) -> str:
    """Create mood log entry, return ID"""
    result = await db.mood_logs.insert_one(mood_data)
    return str(result.inserted_id)


async def get_mood_logs_by_date_range(user_id: str, start_date: datetime, end_date: datetime) -> list[MoodLogModel]:
    """Get mood logs within a date range"""
    logs = await db.mood_logs.find({
        "user_id": user_id,
        "created_at": {"$gte": start_date, "$lte": end_date}
    }).sort("created_at", -1).to_list(None)
    return [MoodLogModel(**l) for l in logs]


# ─── Focus Sessions ───────────────────────────────────────────────────────────
async def create_focus_session(session_data: dict) -> str:
    """Create focus session, return session ID"""
    result = await db.focus_sessions.insert_one(session_data)
    return str(result.inserted_id)


async def get_focus_session(session_id: str, user_id: str) -> FocusModeSessionModel | None:
    """Get focus session by ID and user_id"""
    from bson import ObjectId
    session = await db.focus_sessions.find_one({
        "_id": ObjectId(session_id),
        "user_id": user_id
    })
    if session:
        return FocusModeSessionModel(**session)
    return None


async def update_focus_session(session_id: str, user_id: str, update_data: dict) -> None:
    """Update focus session"""
    from bson import ObjectId
    await db.focus_sessions.update_one(
        {"_id": ObjectId(session_id), "user_id": user_id},
        {"$set": update_data}
    )


# ─── Weekly Autopsies ─────────────────────────────────────────────────────────
async def create_weekly_autopsy(autopsy_data: dict) -> str:
    """Create weekly autopsy report, return ID"""
    result = await db.weekly_autopsies.insert_one(autopsy_data)
    return str(result.inserted_id)
