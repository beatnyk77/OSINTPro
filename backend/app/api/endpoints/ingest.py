from fastapi import APIRouter, BackgroundTasks, HTTPException, UploadFile, File
from app.services.twitter_service import store_tweets
from app.services.media_forensics_service import analyze_image_data
from app.services.briefing_service import generate_briefing_from_events
from app.core.database import SessionLocal
from app.models.event import Event
import os
import json

router = APIRouter()

@router.post("/twitter")
async def ingest_twitter(background_tasks: BackgroundTasks, query: str):
    background_tasks.add_task(
        store_tweets, 
        query=query, 
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN")
    )
    return {"status": "ingest started", "query": query}

@router.post("/media/analyze")
async def analyze_media(file: UploadFile = File(...)):
    """
    Analyze an uploaded image file for forensics
    """
    # Check file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    image_data = await file.read()
    
    # Analyze with media forensics service
    result = analyze_image_data(image_data)
    
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(image_data),
        "analysis": result
    }

@router.get("/briefing/generate")
async def generate_briefing(
    time_window_hours: int = 24,
    max_events: int = 50,
    source_type: str = None
):
    """
    Generate an intelligence briefing from recent events
    """
    db = SessionLocal()
    try:
        # Build query
        query = db.query(Event)
        
        # Filter by time window
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        query = query.filter(Event.created_at >= cutoff_time)
        
        # Filter by source type if specified
        if source_type:
            query = query.filter(Event.source_type == source_type)
        
        # Get events
        events = query.order_by(Event.created_at.desc()).limit(max_events).all()
        
        # Generate briefing
        briefing = generate_briefing_from_events(
            events, 
            time_window_hours=time_window_hours,
            max_events=max_events
        )
        
        return briefing
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating briefing: {str(e)}")
    finally:
        db.close()

@router.get("/briefing/from-query")
async def generate_briefing_from_query_endpoint(
    time_window_hours: int = 24,
    max_events: int = 50,
    source_type: str = None,
    min_credibility: float = None
):
    """
    Generate a briefing with query parameters (alternative endpoint)
    """
    db = SessionLocal()
    try:
        # Build query
        query = db.query(Event)
        
        # Filter by time window
        from datetime import datetime, timedelta
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        query = query.filter(Event.created_at >= cutoff_time)
        
        # Filter by source type if specified
        if source_type:
            query = query.filter(Event.source_type == source_type)
        
        # Filter by minimum credibility if specified
        if min_credibility is not None:
            query = query.filter(Event.credibility_score >= min_credibility)
        
        # Get events
        events = query.order_by(Event.created_at.desc()).limit(max_events).all()
        
        # Generate briefing
        briefing = generate_briefing_from_events(
            events, 
            time_window_hours=time_window_hours,
            max_events=max_events
        )
        
        # Add query info to briefing
        briefing["query_parameters"] = {
            "time_window_hours": time_window_hours,
            "max_events": max_events,
            "source_type": source_type,
            "min_credibility": min_credibility
        }
        
        return briefing
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating briefing: {str(e)}")
    finally:
        db.close()