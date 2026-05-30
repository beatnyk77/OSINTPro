from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.core.config import settings
import os
import asyncio
from app.services.telegram_service import telegram_service

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)

# Startup and shutdown events for Telegram service
@app.on_event("startup")
async def startup_event():
    # Start Telegram listener if configured
    if settings.TELEGRAM_BOT_TOKEN and settings.TELEGRAM_USER_ID:
        try:
            await telegram_service.initialize()
            # Start polling in the background
            asyncio.create_task(telegram_service.start_polling())
            print("📱 Telegram listener started")
        except Exception as e:
            print(f"❌ Failed to start Telegram listener: {e}")
    else:
        print("⚠️ Telegram credentials not configured, listener not started")

@app.on_event("shutdown")
async def shutdown_event():
    # Stop Telegram listener
    try:
        await telegram_service.stop()
        print("📱 Telegram listener stopped")
    except Exception as e:
        print(f"❌ Error stopping Telegram listener: {e}")