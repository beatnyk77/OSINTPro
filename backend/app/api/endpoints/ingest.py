from fastapi import APIRouter, BackgroundTasks
from app.services.twitter_service import store_tweets
import os

router = APIRouter()

@router.post("/twitter")
async def ingest_twitter(background_tasks: BackgroundTasks, query: str):
    background_tasks.add_task(
        store_tweets, 
        query=query, 
        bearer_token=os.getenv("TWITTER_BEARER_TOKEN")
    )
    return {"status": "ingest started", "query": query}