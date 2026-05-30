"""
Analyst Briefing Generator for OSINT-Pro
Generates intelligence briefings from collected events
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import Counter
import json

from app.services.content_analysis_service import analyze_content
from app.core.database import SessionLocal
from app.models.event import Event

logger = logging.getLogger(__name__)

class BriefingService:
    """Service for generating analyst briefings from OSINT events"""
    
    def __init__(self):
        pass
    
    def generate_briefing(self, 
                         events: List[Event], 
                         time_window_hours: int = 24,
                         max_events: int = 50) -> Dict[str, Any]:
        """
        Generate an intelligence briefing from a list of events
        
        Args:
            events: List of Event objects to include in briefing
            time_window_hours: Only include events from the last N hours
            max_events: Maximum number of events to process (for performance)
            
        Returns:
            Dictionary containing the briefing
        """
        if not events:
            return self._empty_briefing()
        
        # Filter by time window if specified
        cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
        recent_events = [
            e for e in events 
            if e.created_at and e.created_at >= cutoff_time
        ]
        
        # Limit events for performance
        if len(recent_events) > max_events:
            # Sort by credibility score (highest first) and take top events
            recent_events.sort(key=lambda e: e.credibility_score or 0.0, reverse=True)
            recent_events = recent_events[:max_events]
        
        if not recent_events:
            return self._empty_briefing("No events in the specified time window")
        
        # Generate briefing components
        executive_summary = self._generate_executive_summary(recent_events)
        key_events = self._extract_key_events(recent_events)
        entity_analysis = self._analyze_entities(recent_events)
        source_breakdown = self._analyze_sources(recent_events)
        trends = self._detect_trends(recent_events)
        
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "time_window_hours": time_window_hours,
            "event_count": len(recent_events),
            "executive_summary": executive_summary,
            "key_events": key_events,
            "entity_analysis": entity_analysis,
            "source_breakdown": source_breakdown,
            "trends": trends,
            "processing_note": f"Generated briefing from {len(recent_events)} events"
        }
    
    def _empty_briefing(self, note: str = "No events available") -> Dict[str, Any]:
        """Return an empty briefing structure"""
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "time_window_hours": 0,
            "event_count": 0,
            "executive_summary": "",
            "key_events": [],
            "entity_analysis": {},
            "source_breakdown": {},
            "trends": [],
            "processing_note": note
        }
    
    def _generate_executive_summary(self, events: List[Event]) -> str:
        """Generate an executive summary from the events"""
        # Combine text from high-credibility events
        high_cred_events = [e for e in events if (e.credibility_score or 0.0) >= 0.6]
        if not high_cred_events:
            high_cred_events = events[:10]  # Fallback to first 10 events
        
        # Extract summaries and combine
        summaries = []
        for event in high_cred_events:
            if event.summary:
                summaries.append(event.summary)
            elif event.text:
                # If no summary, use first 150 chars of text
                summaries.append(event.text[:150] + ("..." if len(event.text) > 150 else ""))
        
        combined_text = " ".join(summaries)
        
        # Generate a summary of the combined text (using our summarization service)
        # We'll limit to 3-5 sentences for the executive summary
        if combined_text:
            # Use the analyze_content function to get a summary
            analysis = analyze_content(combined_text)
            return analysis['summary']
        else:
            return "No significant activity detected in the reporting period."
    
    def _extract_key_events(self, events: List[Event]) -> List[Dict[str, Any]]:
        """Extract the most important events for the briefing"""
        # Sort by credibility score and recency
        sorted_events = sorted(
            events, 
            key=lambda e: (
                (e.credibility_score or 0.0), 
                e.created_at.timestamp() if e.created_at else 0
            ), 
            reverse=True
        )
        
        key_events = []
        for event in sorted_events[:10]:  # Top 10 events
            key_events.append({
                "id": event.id,
                "text_preview": (event.text[:100] + "...") if len(event.text) > 100 else event.text,
                "summary": event.summary,
                "credibility_score": round(event.credibility_score or 0.0, 2),
                "source_type": event.source_type,
                "created_at": event.created_at.isoformat() + "Z" if event.created_at else None,
                "entities_count": len(json.loads(event.entities)) if event.entities else 0
            })
        
        return key_events
    
    def _analyze_entities(self, events: List[Event]) -> Dict[str, Any]:
        """Analyze entities across all events"""
        entity_counter = Counter()
        entity_types = Counter()
        
        for event in events:
            if event.entities:
                try:
                    entities = json.loads(event.entities)
                    if isinstance(entities, list):
                        for entity in entities:
                            if isinstance(entity, dict) and 'text' in entity:
                                entity_text = entity['text']
                                entity_label = entity.get('label', 'UNKNOWN')
                                entity_counter[entity_text] += 1
                                entity_types[entity_label] += 1
                            elif isinstance(entity, str):
                                # Backward compatibility for old string entities
                                entity_counter[entity] += 1
                                entity_types['UNKNOWN'] += 1
                except (json.JSONDecodeError, TypeError):
                    # Skip if entities is not valid JSON
                    continue
        
        # Get top entities
        top_entities = [
            {"text": text, "count": count} 
            for text, count in entity_counter.most_common(10)
        ]
        
        entity_type_dist = dict(entity_types.most_common())
        
        return {
            "top_entities": top_entities,
            "entity_type_distribution": entity_type_dist,
            "total_unique_entities": len(entity_counter)
        }
    
    def _analyze_sources(self, events: List[Event]) -> Dict[str, Any]:
        """Analyze the sources of events"""
        source_counter = Counter()
        source_credibility = {}
        
        for event in events:
            source_type = event.source_type or 'unknown'
            source_counter[source_type] += 1
            
            # Track average credibility by source type
            if source_type not in source_credibility:
                source_credibility[source_type] = []
            if event.credential_score is not None:
                source_credibility[source_type].append(event.credibility_score)
        
        # Calculate average credibility per source type
        avg_credibility = {}
        for source_type, scores in source_credibility.items():
            if scores:
                avg_credibility[source_type] = round(sum(scores) / len(scores), 2)
            else:
                avg_credibility[source_type] = 0.0
        
        return {
            "source_distribution": dict(source_counter),
            "average_credibility_by_source": avg_credibility,
            "total_sources": len(source_counter)
        }
    
    def _detect_trends(self, events: List[Event]) -> List[str]:
        """Detect simple trends in the events (rule-based)"""
        trends = []
        
        # Trend 1: Increasing event frequency
        if len(events) >= 5:
            # Sort by time
            timed_events = [e for e in events if e.created_at]
            timed_events.sort(key=lambda e: e.created_at)
            
            if len(timed_events) >= 2:
                time_span = (timed_events[-1].created_at - timed_events[0].created_at).total_seconds() / 3600  # hours
                if time_span > 0:
                    events_per_hour = len(timed_events) / time_span
                    if events_per_hour > 2:  # More than 2 events per hour
                        trends.append(f"High activity level: {events_per_hour:.1f} events/hour")
        
        # Trend 2: Common locations (from entities)
        location_mentions = []
        for event in events:
            if event.entities:
                try:
                    entities = json.loads(event.entities)
                    if isinstance(entities, list):
                        for entity in entities:
                            if isinstance(entity, dict) and entity.get('type') in ['location', 'geopolitical_entity']:
                                location_mentions.append(entity.get('text', '').lower())
                except (json.JSONDecodeError, TypeError):
                    continue
        
        if location_mentions:
            location_counter = Counter(location_mentions)
            most_common_loc = location_counter.most_common(1)
            if most_common_loc and most_common_loc[0][1] >= 3:  # At least 3 mentions
                trends.append(f"Frequent mention of location: '{most_common_loc[0][0]}' ({most_common_loc[0][1]} times)")
        
        # Trend 3: Rising credibility (if we have recent high-cred events)
        recent_high_cred = [e for e in events if e.created_at and (e.credibility_score or 0.0) >= 0.7]
        if len(recent_high_cred) >= 3:
            trends.append("Multiple high-credibility reports (≥0.7) received in the period")
        
        # Trend 4: New entity types appearing
        entity_types_seen = set()
        for event in events:
            if event.entities:
                try:
                    entities = json.loads(event.entities)
                    if isinstance(entities, list):
                        for entity in entities:
                            if isinstance(entity, dict):
                                entity_types_seen.add(entity.get('label', 'UNKNOWN'))
                except (json.JSONDecodeError, TypeError):
                    continue
        
        if len(entity_types_seen) >= 5:
            trends.append(f"Diverse entity types detected: {', '.join(sorted(entity_types_seen))}")
        
        return trends if trends else ["No significant trends detected"]

# Singleton instance
briefing_service = BriefingService()

def generate_briefing_from_events(events: List[Event], **kwargs) -> Dict[str, Any]:
    """Convenience function to generate a briefing from events"""
    return briefing_service.generate_briefing(events, **kwargs)

def generate_briefing_from_query(query_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a briefing by querying the database (placeholder for future implementation)
    In a full implementation, this would:
    1. Query the events table based on query_params (time, source type, etc.)
    2. Pass the results to generate_briefing_from_events
    """
    # For now, we'll return a placeholder indicating this needs database query implementation
    logger.info("Briefing generation from query parameters requested - would query database in full implementation")
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "processing_note": "Database query-based briefing generation not yet implemented - use generate_briefing_from_events directly",
        "executive_summary": "This briefing generator requires direct event list input. For automated briefings, integrate with event queries.",
        "key_events": [],
        "entity_analysis": {},
        "source_breakdown": {},
        "trends": ["Feature placeholder: database query integration needed"]
    }