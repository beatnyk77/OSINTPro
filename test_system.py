#!/usr/bin/env python3
"""
Comprehensive Test Script for OSINT-Pro
Tests all major components: ingestion, analysis, forensics, briefing generation
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime, timedelta

# Add the backend directory to path so we can import modules
sys.path.append('/Users/kartikaysharma/Desktop/Work/Vibecode/OSINT Pro/backend')

def test_imports():
    """Test that all modules can be imported successfully"""
    print("🧪 Testing module imports...")
    
    try:
        from app.services.credibility_service import score_twitter_user, score_telegram_chat, score_news_domain
        print("   ✅ Credibility service imported")
    except Exception as e:
        print(f"   ❌ Credibility service import failed: {e}")
        return False
        
    try:
        from app.services.content_analysis_service import analyze_content, summarize_text, extract_entities
        print("   ✅ Content analysis service imported")
    except Exception as e:
        print(f"   ❌ Content analysis service import failed: {e}")
        return False
        
    try:
        from app.services.media_forensics_service import analyze_image_data, MediaForensicsService
        print("   ✅ Media forensics service imported")
    except Exception as e:
        print(f"   ❌ Media forensics service import failed: {e}")
        return False
        
    try:
        from app.services.telegram_service import telegram_service
        print("   ✅ Telegram service imported")
    except Exception as e:
        print(f"   ❌ Telegram service import failed: {e}")
        return False
        
    try:
        from app.services.briefing_service import BriefingService, generate_briefing_from_events
        print("   ✅ Briefing service imported")
    except Exception as e:
        print(f"   ❌ Briefing service import failed: {e}")
        return False
        
    try:
        from app.models.event import Event
        print("   ✅ Event model imported")
    except Exception as e:
        print(f"   ❌ Event model import failed: {e}")
        return False
        
    return True

def test_credibility_service():
    """Test credibility scoring functionality"""
    print("\n🧪 Testing credibility service...")
    
    from app.services.credibility_service import score_twitter_user, score_telegram_chat, score_news_domain
    
    # Test Twitter scoring
    twitter_user_data = {
        'created_at': datetime.utcnow() - timedelta(days=365*2),  # 2 years old
        'verified': True,
        'followers_count': 10000,
        'following_count': 500
    }
    
    try:
        twitter_score = score_twitter_user(twitter_user_data)
        assert 0.0 <= twitter_score <= 1.0, f"Twitter score out of range: {twitter_score}"
        print(f"   ✅ Twitter scoring: {twitter_score:.3f}")
    except Exception as e:
        print(f"   ❌ Twitter scoring failed: {e}")
        return False
    
    # Test Telegram scoring
    telegram_chat_data = {
        'id': 123456789,
        'type': 'supergroup',
        'title': 'Test Defence Group',
        'username': 'defencetest',
        'description': 'A group for discussing defence-related topics',
        'member_count': 500
    }
    
    try:
        telegram_score = score_telegram_chat(telegram_chat_data)
        assert 0.0 <= telegram_score <= 1.0, f"Telegram score out of range: {telegram_score}"
        print(f"   ✅ Telegram scoring: {telegram_score:.3f}")
    except Exception as e:
        print(f"   ❌ Telegram scoring failed: {e}")
        return False
    
    # Test News domain scoring
    try:
        news_score = score_news_domain('reuters.com')
        assert 0.0 <= news_score <= 1.0, f"News score out of range: {news_score}"
        print(f"   ✅ News domain scoring: {news_score:.3f}")
    except Exception as e:
        print(f"   ❌ News domain scoring failed: {e}")
        return False
        
    return True

def test_content_analysis():
    """Test content analysis functionality"""
    print("\n🧪 Testing content analysis service...")
    
    from app.services.content_analysis_service import analyze_content
    
    test_text = """
    Indian Army troops were spotted near Pangong Lake conducting routine patrols 
    along the Line of Actual Control. The convoy consisted of approximately 20 
    vehicles including tanks and personnel carriers. Local sources reported 
    increased activity in the area over the past 48 hours.
    """
    
    try:
        analysis = analyze_content(test_text)
        
        # Check summary
        assert 'summary' in analysis, "Summary missing from analysis"
        assert len(analysis['summary']) > 0, "Summary is empty"
        assert len(analysis['summary']) <= len(test_text), "Summary longer than original text"
        print(f"   ✅ Summarization: {analysis['summary'][:100]}...")
        
        # Check entities
        assert 'entities' in analysis, "Entities missing from analysis"
        assert isinstance(analysis['entities'], list), "Entities should be a list"
        print(f"   ✅ Entity extraction: Found {len(analysis['entities'])} entities")
        
        # Check processing note
        assert 'processing_note' in analysis, "Processing note missing"
        print(f"   ✅ Processing note: {analysis['processing_note']}")
        
        # Check entity structure if entities found
        if analysis['entities']:
            entity = analysis['entities'][0]
            required_fields = ['text', 'label', 'confidence', 'type']
            for field in required_fields:
                assert field in entity, f"Entity missing field: {field}"
            print(f"   ✅ Entity structure validated: {entity['text']} ({entity['label']})")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Content analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_media_forensics():
    """Test media forensics functionality"""
    print("\n🧪 Testing media forensics service...")
    
    from app.services.media_forensics_service import analyze_image_data, MediaForensicsService
    
    # Create a simple test image in memory
    try:
        from PIL import Image
        import io
        
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_data = img_bytes.getvalue()
        
        # Analyze the image
        result = analyze_image_data(img_data)
        
        # Check basic structure
        assert 'basic_info' in result, "Basic info missing"
        assert 'exif_data' in result, "EXIF data missing"
        assert 'perceptual_hashes' in result, "Perceptual hashes missing"
        assert 'forensics_checks' in result, "Forensics checks missing"
        assert 'reverse_image_search' in result, "Reverse image search missing"
        assert 'processing_note' in result, "Processing note missing"
        
        # Check basic info
        basic_info = result['basic_info']
        assert basic_info['width'] == 100, f"Expected width 100, got {basic_info['width']}"
        assert basic_info['height'] == 100, f"Expected height 100, got {basic_info['height']}"
        assert basic_info['format'] == 'JPEG', f"Expected format JPEG, got {basic_info['format']}"
        print(f"   ✅ Basic info: {basic_info['width']}x{basic_info['height']} {basic_info['format']}")
        
        # Check perceptual hashes
        hashes = result['perceptual_hashes']
        assert isinstance(hashes, dict), "Perceptual hashes should be a dict"
        assert len(hashes) > 0, "Should have at least one hash type"
        print(f"   ✅ Perceptual hashes: {list(hashes.keys())}")
        
        # Check forensics checks
        checks = result['forensics_checks']
        assert isinstance(checks, dict), "Forensics checks should be a dict"
        required_checks = ['has_transparency', 'is_animated', 'likely_photograph']
        for check in required_checks:
            assert check in checks, f"Missing forensics check: {check}"
        print(f"   ✅ Forensics checks: {len(checks)} checks performed")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Media forensics failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_briefing_service():
    """Test briefing generation functionality"""
    print("\n🧪 Testing briefing service...")
    
    from app.services.briefing_service import BriefingService, generate_briefing_from_events
    from app.models.event import Event
    
    # Create test events
    test_events = [
        Event(
            id=1,
            text="Indian Army convoy spotted near Pangong Lake moving north",
            summary="Indian Army convoy of approximately 20 vehicles observed moving north along LAC",
            entities=json.dumps([
                {"text": "Indian Army", "label": "ORG", "confidence": 0.75, "type": "organization"},
                {"text": "Pangong Lake", "label": "LOC", "confidence": 0.70, "type": "location"},
                {"text": "LAC", "label": "NORP", "confidence": 0.85, "type": "geopolitical_entity"}
            ]),
            source_type='twitter',
            source_id='12345',
            credibility_score=0.82,
            created_at=datetime.utcnow() - timedelta(hours=2)
        ),
        Event(
            id=2,
            text="Unusual vehicle movements observed in Daulat Beg Oldi sector",
            summary="Increased logistics activity detected near DBO with fuel tankers observed",
            entities=json.dumps([
                {"text": "Daulat Beg Oldi", "label": "LOC", "confidence": 0.80, "type": "location"},
                {"text": "logistics", "label": "NOUN", "confidence": 0.60, "type": "activity"}
            ]),
            source_type='telegram',
            source_id='67890',
            credibility_score=0.75,
            created_at=datetime.utcnow() - timedelta(hours=5)
        )
    ]
    
    try:
        # Test briefing generation
        briefing = generate_briefing_from_events(test_events, time_window_hours=24)
        
        # Check structure
        assert 'generated_at' in briefing, "Generated timestamp missing"
        assert 'executive_summary' in briefing, "Executive summary missing"
        assert 'key_events' in briefing, "Key events missing"
        assert 'entity_analysis' in briefing, "Entity analysis missing"
        assert 'source_breakdown' in briefing, "Source breakdown missing"
        assert 'trends' in briefing, "Trends missing"
        assert 'event_count' in briefing, "Event count missing"
        
        # Check values
        assert briefing['event_count'] == 2, f"Expected 2 events, got {briefing['event_count']}"
        assert len(briefing['key_events']) == 2, f"Expected 2 key events, got {len(briefing['key_events'])}"
        assert isinstance(briefing['executive_summary'], str), "Executive summary should be string"
        assert len(briefing['executive_summary']) > 0, "Executive summary should not be empty"
        print(f"   ✅ Executive summary: {briefing['executive_summary'][:100]}...")
        
        # Check key events structure
        key_event = briefing['key_events'][0]
        required_fields = ['id', 'text_preview', 'summary', 'credibility_score', 'source_type']
        for field in required_fields:
            assert field in key_event, f"Key event missing field: {field}"
        print(f"   ✅ Key events: {len(briefing['key_events'])} events processed")
        
        # Check entity analysis
        entity_analysis = briefing['entity_analysis']
        assert 'top_entities' in entity_analysis, "Top entities missing"
        assert 'entity_type_distribution' in entity_analysis, "Entity type distribution missing"
        assert isinstance(entity_analysis['top_entities'], list), "Top entities should be list"
        print(f"   ✅ Entity analysis: {len(entity_analysis['top_entities'])} top entities")
        
        # Check source breakdown
        source_breakdown = briefing['source_breakdown']
        assert 'source_distribution' in source_breakdown, "Source distribution missing"
        assert 'average_credibility_by_source' in source_breakdown, "Average credibility missing"
        print(f"   ✅ Source breakdown: {source_breakdown['source_distribution']}")
        
        # Check trends
        assert isinstance(briefing['trends'], list), "Trends should be a list"
        print(f"   ✅ Trends: {len(briefing['trends'])} trends detected")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Briefing service failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """Test integration between services"""
    print("\n🧪 Testing service integration...")
    
    try:
        from app.services.twitter_service import store_tweets
        from app.services.content_analysis_service import analyze_content
        from app.services.credibility_service import score_twitter_user
        from app.models.event import Event
        import json
        
        # Simulate processing a tweet through the full pipeline
        tweet_text = "Breaking: Indian Army reports increased PLA activity along Line of Actual Control in Ladakh sector"
        user_data = {
            'created_at': datetime.utcnow() - timedelta(days=365*3),
            'verified': True,
            'followers_count': 15000,
            'following_count': 300
        }
        
        # Step 1: Score credibility
        credibility = score_twitter_user(user_data)
        assert 0.0 <= credibility <= 1.0, "Credibility score invalid"
        print(f"   ✅ Credibility scored: {credibility:.3f}")
        
        # Step 2: Analyze content
        analysis = analyze_content(tweet_text)
        summary = analysis['summary']
        entities = analysis['entities']
        print(f"   ✅ Content analyzed: {len(entities)} entities extracted")
        
        # Step 3: Create event (simulating database storage)
        event = Event(
            text=tweet_text,
            summary=summary,
            entities=json.dumps(entities),
            source_type='twitter',
            source_id='99999',
            credibility_score=credibility
        )
        
        # Verify the event contains all expected data
        assert event.text == tweet_text, "Event text mismatch"
        assert event.summary == summary, "Event summary mismatch"
        assert event.source_type == 'twitter', "Event source type mismatch"
        assert event.credibility_score == credibility, "Event credibility score mismatch"
        
        # Verify entities can be parsed
        parsed_entities = json.loads(event.entities)
        assert isinstance(parsed_entities, list), "Entities should parse to list"
        assert len(parsed_entities) == len(entities), "Entity count mismatch after JSON roundtrip"
        print(f"   ✅ Event creation: Complete pipeline successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🚀 Starting OSINT-Pro Comprehensive Test Suite")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Credibility Service", test_credibility_service),
        ("Content Analysis", test_content_analysis),
        ("Media Forensics", test_media_forensics),
        ("Briefing Service", test_briefing_service),
        ("Service Integration", test_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                print(f"✅ {test_name}: PASSED")
                passed += 1
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: FAILED with exception: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! OSINT-Pro is ready for deployment.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())