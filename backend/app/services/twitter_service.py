import tweepy
import os
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.event import Event
from app.services.credibility_service import score_twitter_user

def fetch_twitter_data(bearer_token: str, query: str, since_id: str = None):
    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    tweets = client.search_recent_tweets(
        query=query, 
        max_results=100,
        since_id=since_id,
        tweet_fields=["created_at", "geo"],
        user_fields=["created_at", "verified", "followers_count", "following_count"],
        expansions=["author_id"]
    )
    
    # Create a lookup dict for users
    users = {u.id: u for u in tweets.includes.get('users', [])} if tweets.includes else {}
    
    result = []
    for tweet in tweets.data or []:
        user = users.get(tweet.author_id)
        user_data = None
        if user:
            user_data = {
                'created_at': getattr(user, 'created_at', None),
                'verified': getattr(user, 'verified', False),
                'followers_count': getattr(user, 'followers_count', 0),
                'following_count': getattr(user, 'following_count', 0)
            }
        result.append({
            'text': tweet.text,
            'created_at': tweet.created_at,
            'id': tweet.id,
            'author_id': tweet.author_id,
            'user_data': user_data
        })
    return result

def store_tweets(bearer_token: str, query: str):
    """Fetch tweets, compute credibility scores, and store in the database."""
    db = SessionLocal()
    try:
        tweets_data = fetch_twitter_data(bearer_token, query)
        for t in tweets_data:
            credibility = score_twitter_user(t.get('user_data'))
            event = Event(
                text=t['text'],
                source_type='twitter',
                source_id=str(t['id']),
                credibility_score=credibility
            )
            db.add(event)
        db.commit()
        print(f"🐦 Stored {len(tweets_data)} tweets with credibility scores.")
    except Exception as e:
        print(f"❌ Error storing tweets: {e}")
        db.rollback()
    finally:
        db.close()