import os
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.database import connect_to_mongo, close_mongo_connection
from api.deps import get_current_user
from api.routers import events, notes, ai, voice, calendar, push, auth, user
from api.routers import analytics, finance, focus, learning, memory
from api import cron

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    logger.info("Application startup complete")
    yield
    await close_mongo_connection()
    logger.info("Application shutdown complete")


app = FastAPI(
    title="JARVIS Event Manager API",
    description="AI-powered personal event management system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": True},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": True},
    )


@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(user.router, prefix="/api/user", tags=["user"], dependencies=[Depends(get_current_user)])
app.include_router(events.router, prefix="/api/events", tags=["events"], dependencies=[Depends(get_current_user)])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"], dependencies=[Depends(get_current_user)])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"], dependencies=[Depends(get_current_user)])
app.include_router(voice.router, prefix="/api/voice", tags=["voice"], dependencies=[Depends(get_current_user)])
app.include_router(calendar.router, prefix="/api/calendar", tags=["calendar"], dependencies=[Depends(get_current_user)])
app.include_router(push.router, prefix="/api/push", tags=["push"], dependencies=[Depends(get_current_user)])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"], dependencies=[Depends(get_current_user)])
app.include_router(finance.router, prefix="/api/finance", tags=["finance"], dependencies=[Depends(get_current_user)])
app.include_router(focus.router, prefix="/api/focus", tags=["focus"], dependencies=[Depends(get_current_user)])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"], dependencies=[Depends(get_current_user)])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"], dependencies=[Depends(get_current_user)])
app.include_router(cron.router, tags=["cron"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
