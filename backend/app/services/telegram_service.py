"""
Telegram Service for OSINT-Pro
Handles fetching messages from Telegram channels/groups and processing them
"""

import logging
from typing import List, Dict, Any, Optional
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import asyncio
import json
from datetime import datetime

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.event import Event
from app.services.credibility_service import score_telegram_chat
from app.services.content_analysis_service import analyze_content

logger = logging.getLogger(__name__)

class TelegramService:
    """Service for ingesting and processing Telegram messages"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.user_id = settings.TELEGRAM_USER_ID  # For getting chat member info
        self.application = None
        
    async def initialize(self):
        """Initialize the Telegram bot application"""
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN not configured")
            return False
            
        try:
            self.application = Application.builder().token(self.bot_token).build()
            
            # Add handler for messages
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
            )
            
            # Initialize the application
            await self.application.initialize()
            logger.info("Telegram service initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Telegram service: {e}")
            return False
    
    async def start_polling(self):
        """Start polling for messages"""
        if not self.application:
            if not await self.initialize():
                return False
                
        try:
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Telegram polling started")
            return True
        except Exception as e:
            logger.error(f"Error starting Telegram polling: {e}")
            return False
    
    async def stop(self):
        """Stop the Telegram service"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
            logger.info("Telegram service stopped")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming Telegram messages"""
        try:
            message = update.effective_message
            chat = update.effective_chat
            
            if not message or not chat or not message.text:
                return
            
            # Skip if it's from our own bot
            if message.from_user.id == context.bot.id:
                return
                
            logger.info(f"Received Telegram message from chat {chat.id}: {message.text[:50]}...")
            
            # Process the message
            await self._process_telegram_message(message, chat)
            
        except Exception as e:
            logger.error(f"Error handling Telegram message: {e}")
    
    async def _process_telegram_message(self, message, chat):
        """Process a Telegram message and store it as an event"""
        db = SessionLocal()
        try:
            # Get chat information for credibility scoring
            chat_info = await self._get_chat_info(chat.id)
            
            # Compute credibility score
            credibility = score_telegram_chat(chat_info)
            
            # Analyze content (summarization + entity extraction)
            analysis = analyze_content(message.text)
            summary = analysis['summary']
            entities = analysis['entities']
            
            # Check for media attachments
            media_info = None
            if message.photo or message.document or message.video:
                media_info = await self._process_media(message, context.bot)
            
            # Create event record
            event = Event(
                text=message.text,
                summary=summary,
                entities=json.dumps(entities),
                source_type='telegram',
                source_id=f"{chat.id}_{message.message_id}",
                credibility_score=credibility
                # Note: We could add media_analysis field to Event model later if needed
            )
            
            db.add(event)
            db.commit()
            
            logger.info(f"📱 Stored Telegram message from chat {chat.id} with credibility {credibility:.2f}")
            
        except Exception as e:
            logger.error(f"Error processing Telegram message: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def _get_chat_info(self, chat_id: int) -> Dict[str, Any]:
        """Get information about a Telegram chat for credibility scoring"""
        try:
            chat = await self.application.bot.get_chat(chat_id)
            
            # Get member count if it's a group/channel
            member_count = None
            try:
                member_count = await self.application.bot.get_chat_member_count(chat_id)
            except Exception:
                pass  # Might not have permission or chat type doesn't support this
            
            return {
                'id': chat.id,
                'type': chat.type,  # private, group, supergroup, channel
                'title': getattr(chat, 'title', None),
                'username': getattr(chat, 'username', None),
                'description': getattr(chat, 'description', None),
                'member_count': member_count,
                # For supergroups/channels, we might want to get admin info etc.
                'created_at': getattr(chat, 'date', None)  # When the chat was created (if available)
            }
        except Exception as e:
            logger.warning(f"Could not get chat info for {chat_id}: {e}")
            return {
                'id': chat_id,
                'type': 'unknown',
                'title': None,
                'username': None,
                'description': None,
                'member_count': None
            }
    
    async def _process_media(self, message, bot) -> Optional[Dict[str, Any]]:
        """Process media attachments in Telegram messages"""
        try:
            media_info = {
                'has_media': True,
                'media_type': None,
                'file_id': None,
                'file_size': None
            }
            
            # Check for photo
            if message.photo:
                # Get the largest photo
                photo = message.photo[-1]
                media_info['media_type'] = 'photo'
                media_info['file_id'] = photo.file_id
                media_info['file_size'] = photo.file_size
                
                # Download and analyze the image
                try:
                    file_obj = await bot.get_file(photo.file_id)
                    image_bytes = await file_obj.download_as_bytearray()
                    
                    # Analyze with media forensics
                    from app.services.media_forensics_service import analyze_image_data
                    forensics_result = analyze_image_data(bytes(image_bytes))
                    media_info['forensics_analysis'] = forensics_result
                    
                except Exception as e:
                    logger.warning(f"Could not analyze Telegram photo: {e}")
                    media_info['forensics_error'] = str(e)
            
            # Check for document
            elif message.document:
                doc = message.document
                media_info['media_type'] = 'document'
                media_info['file_id'] = doc.file_id
                media_info['file_size'] = doc.file_size
                media_info['file_name'] = doc.file_name
                media_info['mime_type'] = doc.mime_type
                
            # Check for video
            elif message.video:
                video = message.video
                media_info['media_type'] = 'video'
                media_info['file_id'] = video.file_id
                media_info['file_size'] = video.file_size
                media_info['duration'] = video.duration
                media_info['width'] = video.width
                media_info['height'] = video.height
                
            return media_info if media_info['media_type'] else None
            
        except Exception as e:
            logger.warning(f"Error processing Telegram media: {e}")
            return None

# Global service instance
telegram_service = TelegramService()

async def start_telegram_ingest():
    """Start the Telegram ingestion service"""
    return await telegram_service.start_polling()

async def stop_telegram_ingest():
    """Stop the Telegram ingestion service"""
    await telegram_service.stop()

# For backward compatibility with existing code
def fetch_telegram_data(bot_token: str, chat_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Synchronous function to fetch recent Telegram messages (for backward compatibility)
    Note: For real-time ingestion, use the async service above
    """
    # This is a simplified version for backward compatibility
    # In a real implementation, you might want to use the Telethon library or 
    # maintain a persistent connection for polling
    logger.warning("Synchronous Telegram fetch is deprecated. Use async service for real-time ingestion.")
    return []

def store_telegram_messages(bot_token: str, chat_id: str):
    """
    Store recent messages from a Telegram chat (for backward compatibility)
    """
    logger.warning("Synchronous Telegram storage is deprecated. Use async service for real-time ingestion.")