import re
import json
from typing import List, Dict, Any

def summarize_text(text: str, max_length: int = 200) -> str:
    """
    Create a simple summary by truncating to max_length.
    In a more advanced version, we could use NLP summarization.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    # Try to break at a sentence or word boundary
    summary = text[:max_length]
    # Find the last period or space to avoid cutting words
    last_period = summary.rfind('.')
    last_space = summary.rfind(' ')
    # Prefer breaking at a period, then space
    if last_period > max_length * 0.7:  # If we found a period in the latter 30%
        return summary[:last_period+1]
    elif last_space > max_length * 0.8:  # If we found a space in the latter 20%
        return summary[:last_space]
    else:
        return summary + "..."

def extract_entities(text: str) -> List[str]:
    """
    Extract simple entities using regex patterns.
    Returns a list of unique entity strings.
    """
    if not text:
        return []
    
    entities = set()
    
    # Pattern 1: Dates (MM/DD/YYYY, DD-MM-YYYY, YYYY-MM-DD)
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b'
    ]
    for pattern in date_patterns:
        matches = re.findall(pattern, text)
        entities.update(matches)
    
    # Pattern 2: Numbers with commas and decimals (e.g., 1,000, 98.6%)
    number_pattern = r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b'
    matches = re.findall(number_pattern, text)
    entities.update(matches)
    
    # Pattern 3: Capitalized words (potential proper nouns) - excluding first word of sentence
    # We'll look for words that start with capital letter and are not at the start of the sentence
    # This is simplistic and will have false positives (e.g., first word after a period)
    # But for simplicity, we'll do:
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    entities.update(words)
    
    # Pattern 4: Acronyms (all caps, 2+ letters)
    acronym_pattern = r'\b[A-Z]{2,}\b'
    matches = re.findall(acronym_pattern, text)
    entities.update(matches)
    
    # Convert to list and return
    return list(entities)