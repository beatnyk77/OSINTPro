import re
from datetime import datetime
from typing import Dict, Any, Optional

def score_twitter_user(user_data: Dict[str, Any]) -> float:
    """
    Compute a credibility score for a Twitter user based on available metadata.
    Returns a score between 0.0 and 1.0.
    """
    score = 0.0
    max_score = 0.0

    # Factor 1: Account age (older is better)
    max_score += 0.3
    if user_data.get('created_at'):
        score += 0.3
    else:
        score += 0.1

    # Factor 2: Verified status
    max_score += 0.2
    if user_data.get('verified', False):
        score += 0.2

    # Factor 3: Follower/following ratio
    max_score += 0.3
    followers = user_data.get('followers_count', 0)
    following = user_data.get('following_count', 1)
    if following > 0:
        ratio = followers / following
        if ratio >= 1:
            score += 0.3
        else:
            score += 0.3 * ratio
    else:
        score += 0.1

    if max_score > 0:
        return min(score / max_score, 1.0)
    return 0.0

def score_telegram_chat(chat_data: Dict[str, Any]) -> float:
    """
    Compute a credibility score for a Telegram chat (channel or group).
    Returns a score between 0.0 and 1.0.
    """
    score = 0.0
    max_score = 0.0

    # Factor 1: Chat age
    max_score += 0.4
    score += 0.2  # Placeholder

    # Factor 2: Member count
    max_score += 0.3
    member_count = chat_data.get('member_count', 0)
    if member_count > 0:
        import math
        score += 0.3 * min(math.log(member_count + 1) / math.log(1001), 1.0)
    else:
        score += 0.1

    # Factor 3: Channel vs group
    max_score += 0.2
    if chat_data.get('type') == 'channel':
        score += 0.2
    else:
        score += 0.1

    # Factor 4: Description length
    max_score += 0.1
    description = chat_data.get('description', '')
    if description and len(description) > 10:
        score += 0.1
    else:
        score += 0.05

    if max_score > 0:
        return min(score / max_score, 1.0)
    return 0.0

def score_news_domain(domain: str) -> float:
    """
    Compute a credibility score for a news domain based on simple heuristics.
    Returns a score between 0.0 and 1.0.
    """
    score = 0.0
    max_score = 0.0

    # Factor 1: Domain age (placeholder)
    max_score += 0.4
    trusted_domains = [
        'thehindu.com',
        'dawn.com',
        'reuters.com',
        'bbc.com',
        'cnn.com',
        'aljazeera.com',
        'theguardian.com',
        'nytimes.com',
        'washingtonpost.com',
        'economist.com'
    ]
    if any(trusted in domain for trusted in trusted_domains):
        score += 0.4
    else:
        score += 0.1

    # Factor 2: SSL (HTTPS)
    max_score += 0.3
    score += 0.3

    # Factor 3: Presence of 'news'
    max_score += 0.2
    if 'news' in domain.lower():
        score += 0.2
    else:
        score += 0.05

    # Factor 4: Domain length
    max_score += 0.1
    if len(domain) > 5 and len(domain) < 20:
        score += 0.1
    else:
        score += 0.05

    if max_score > 0:
        return min(score / max_score, 1.0)
    return 0.0