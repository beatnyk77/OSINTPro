# OSINT-Pro: Defence-Grade Open Source Intelligence System

A theatre-configurable, air-gapped OSINT intelligence system designed for defence applications. Features credibility scoring, content analysis, media forensics, real-time Telegram ingestion, and automated intelligence briefing generation.

## 🎯 Purpose

OSINT-Pro is designed to help defence analysts rapidly collect, assess, and analyze open-source information from social media and other open sources. The system is built for air-gapped deployment with mission-configurable profiles for different operational theatres.

## ⚡ Key Features

### 1. **Multi-Source Ingestion**
- **Twitter/X**: Real-time tweet collection with credibility scoring
- **Telegram**: Async polling of channels/groups with media processing
- **Configurable Sources**: Mission-profile driven source prioritization

### 2. **Credibility Scoring**
- **Twitter**: Account age, verification status, follower/following ratio
- **Telegram**: Chat age, member count, chat type, description quality
- **News Domains**: Domain trust, SSL, news keyword presence, content length
- **Score Range**: 0.0-1.0 for transparent, auditable assessment

### 3. **Advanced Content Analysis**
- **spaCy NER**: Named entity recognition (PERSON, ORG, GPE, etc.)
- **TextRank Summarization**: Extractive summarization (3 sentences default)
- **Entity Resolution**: Linking to ISO country codes, NATO military symbols
- **Confidence Scoring**: Each entity gets reliability score (0.0-1.0)

### 4. **Media Forensics** 🆕
- **EXIF Extraction**: Timestamps, camera settings, GPS coordinates
- **Perceptual Hashing**: Reverse image search simulation (average, phash, dhash, whash)
- **Basic Forensics**: Transparency, animation, size consistency checks
- **Threat Intel Integration**: Check against known hash databases

### 5. **Intelligence Briefing Generator** 🆕
- **Executive Summaries**: Auto-generated from high-credibility events
- **Key Events Ranking**: By credibility and recency
- **Entity Analysis**: Top-mentioned entities with frequency counts
- **Source Breakdown**: Platform credibility averages
- **Trend Detection**: Activity spikes, location frequency, entity diversity

### 6. **Mission Configurable**
- **YAML Profiles**: Theatre-specific configuration (geo_bounds, sources, narratives)
- **Rapid Adaptation**: Switch theatres by changing profile, no code changes
- **Example Profile**: LAC Logistics Monitoring included

### 7. **Air-Gapped Ready**
- **Zero External Dependencies**: All processing happens locally
- **Pre-bundled Models**: spaCy model included in Docker image
- **Simulated Services**: Perceptual hashing enables offline reverse image search
- **Update Mechanism**: Threat databases updatable via secure air-gapped transfers

### 8. **Traceability & Transparency**
- **Raw Data Preservation**: Original text/media stored alongside analysis
- **Source Attribution**: Every intelligence point links to raw source
- **Processing Logic**: Credibility scores and analysis explainable
- **Audit Trail**: Timestamps, source IDs, confidence scores

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│   Twitter API   │    │  Telegram Bot    │    │   Other Sources    │
└─────────┬───────┘    └─────────┬────────┘    └──────────┬──────────┘
          │                      │                       │
          ▼                      ▼                       ▼
┌───────────────────────────────────────────────────────────────────┐
│                   Ingestion Services (Async)                      │
│  - Twitter Service    │  Telegram Service   │  Future Services    │
└─────────┬─────────────┴─────────────┬───────┴─────────────────────┘
          │                           │                         │
          ▼                           ▼                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                  Analysis & Enrichment Pipeline                   │
│                                                                   │
│  Credibility Scoring  │  Content Analysis  │  Media Forensics    │
│  (spaCy + heuristics) │ (NER + Summarization) │ (EXIF + Hashing)  │
└─────────┬─────────────┴─────────────┬───────┴─────────────────────┘
          │                           │                         │
          ▼                           ▼                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                    Storage & Enrichment Layer                     │
│                                                                   │
│          PostgreSQL + PostGIS (Events with Geospatial)            │
│          Redis (Caching, Rate Limiting)                           │
└─────────┬─────────────┴─────────────┬───────┴─────────────────────┘
          │                           │                         │
          ▼                           ▼                         ▼
┌───────────────────────────────────────────────────────────────────┐
│                   API & Presentation Layer                        │
│                                                                   │
│  FastAPI REST API   │  React Frontend Map View   │  Briefing Gen   │
│  (Ingest, Analysis) │    (Event Visualization)   │ (Reports)       │
└───────────────────────────────────────────────────────────────────┘
```

## 📦 What's Included

### Backend Services (`/backend`)
- **FastAPI Application**: High-performance async API
- **PostgreSQL+PostGIS**: Spatially-enabled database for geolocated events
- **Redis**: Caching and rate limiting
- **Alembic**: Database migration management
- **Modular Services**:
  - `credibility_service.py` - Source trustworthiness scoring
  - `content_analysis_service.py` - NLP pipeline (spaCy + Sumy)
  - `media_forensics_service.py` - Image analysis & forensics
  - `telegram_service.py` - Real-time Telegram ingestion
  - `briefing_service.py` - Intelligence briefing generator
  - `twitter_service.py` - Twitter/X data fetching

### Configuration
- **Docker Compose**: Orchestration of all services
- **Environment Variables**: `.env` file for configuration
- **Mission Profiles**: YAML files in `/mission_profiles/`

### Frontend (`/frontend`)
- **React + Mapbox GL JS**: Interactive event visualization
- **Basic Map View**: Shows events with popup details
- **Extensible Design**: Ready for additional visualization layers

## 🔧 Installation & Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose v2+
- Git (for cloning repository)

### Quick Start (Under 15 Minutes)

1. **Clone the Repository**
   ```bash
   git clone https://github.com/beatnyk77/OSINTPro.git
   cd OSINTPro
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your actual keys:
   #   TWITTER_BEARER_TOKEN=your_x_bearer_token
   #   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   #   TELEGRAM_USER_ID=your_numeric_user_id
   #   MAPBOX_TOKEN=your_mapbox_token
   #   POSTGRES_PASSWORD=your_strong_password
   #   MISSION_PROFILE=lac_logistics
   ```

3. **Build and Start Services**
   ```bash
   docker compose up --build -d
   ```

4. **Initialize Database**
   ```bash
   docker compose exec backend alembic upgrade head
   ```

5. **Verify Deployment**
   - **API Docs**: http://localhost:8000/docs
   - **Frontend Map**: http://localhost:3000
   - **Backend Logs**: docker compose logs -f backend

6. **Test Ingestion**
   ```bash
   # Test Twitter ingest
   curl -X POST "http://localhost:8000/api/v1/ingest/twitter?query=LAC%20logistics%20lang:en"
   
   # Check results
   curl -s "http://localhost:8000/api/v1/events?limit=5" | jq .
   ```

## 📚 API Endpoints

### Ingestion Endpoints
- `POST /api/v1/ingest/twitter` - Start Twitter ingest for query
- `POST /api/v1/ingest/media/analyze` - Upload and analyze image for forensics

### Briefing Endpoints
- `GET /api/v1/ingest/briefing/generate` - Generate briefing from recent events
- `GET /api/v1/ingest/briefing/from-query` - Parameterized briefing generation

### Data Endpoints
- `GET /api/v1/events` - Retrieve events with filtering options
- `GET /api/v1/events/{id}` - Get specific event by ID

### Health & Info
- `GET /` - API welcome message
- `GET /docs` - Interactive API documentation (Swagger UI)

## 📋 Mission Profiles

Mission profiles allow rapid configuration for different operational theatres. Profiles are YAML files in the `mission_profiles/` directory.

### Example: `lac_logistics.yaml`
```yaml
theatre: "LAC Border Logistics Monitoring"
geo_bounds: [78.0, 30.0, 79.5, 32.0]  # [min_lon, min_lat, max_lon, max_lat]
priority_sources:
  - name: "The Hindu"
    url: "https://www.thehindu.com/news/national/"
    type: "news"
    credibility_weight: 0.4
  - name: "Dawn"
    url: "https://www.dawn.com/"
    type: "news"
    credibility_weight: 0.3
narratives_to_detect:
  - "convoy movement"
  - "fuel shortage"
  - "road closure"
  - "bridge damage"
  - "troop buildup"
  - "logistics delay"
alert_threshold: 1.5  # Credibility score multiplier for alerts
refresh_interval_minutes: 15  # How often to check sources
```

To use a mission profile:
1. Create/update YAML file in `mission_profiles/`
2. Set `MISSION_PROFILE` in `.env` to the filename (without `.yaml`)
3. Restart services: `docker compose restart backend`

## 🛡️ Defence Relevance

### Air-Gapped Operation
- Zero external API calls during normal operation
- All models (spaCy, etc.) bundled in Docker image
- Threat intelligence databases updatable via secure transfers
- No dependency on cloud services or external APIs

### Traceability & Accountability
- Every intelligence element traces to:
  - Raw source (tweet, Telegram message, etc.)
  - Collector (Twitter API, Telegram Bot)
  - Processing logic (credibility factors, analysis methods)
  - Timestamps (collection, processing, storage)
- Credibility scores explainable through documented factors

### Operational Security
- Configurable data retention (via database policies)
- Secure credential handling (environment variables, .env)
- Network isolation capable (internal deployments)
- Minimal attack surface (few exposed ports, no unnecessary services)

### Mission Flexibility
- Rapid theatre switching via YAML profiles
- Source prioritization based on reliability
- Narrative-based filtering for relevant intelligence
- Alert thresholds customizable per mission

## 🔬 Technical Details

### Credibility Scoring Algorithm

**Twitter/X Users**:
```
Score = (0.3 × Account Age Factor) + 
        (0.2 × Verification Status) + 
        (0.3 × Follower/Following Ratio) + 
        (0.2 × Profile Completeness)
```

**Telegram Chats/Groups**:
```
Score = (0.3 × Chat Age Factor) + 
        (0.3 × Member Count Factor) + 
        (0.2 × Chat Type Weight) + 
        (0.2 × Description Quality)
```

**News Domains**:
```
Score = (0.4 × Domain Trust) + 
        (0.3 × HTTPS/SSL) + 
        (0.2 × 'news' in Domain) + 
        (0.1 × Content Length Factor)
```

### Content Analysis Pipeline

1. **Text Preprocessing**: Clean HTML, normalize whitespace
2. **Summarization**: TextRank algorithm extracts key sentences
3. **Named Entity Recognition**: spaCy `en_core_web_sm` model identifies entities
4. **Entity Resolution**: 
   - ISO 3166-1 alpha-2 country codes (US → United States)
   - NATO military symbols (MBT → Main Battle Tank)
   - Custom resolution rules
5. **Confidence Assignment**: Based on match certainty and source reliability

### Media Forensics Workflow

1. **Image Validation**: Check format, dimensions, file type
2. **EXIF Extraction**: Parse metadata including GPS if present
3. **Perceptual Hashing**: Generate multiple hash types for similarity detection
4. **Basic Checks**: Transparency, animation, consistency validation
5. **Threat Lookup**: Compare hashes against known bad image database
6. **Result Compilation**: Return structured analysis report

## 📊 Sample Output

### Event Record (Stored in Database)
```json
{
  "id": 1245,
  "text": "Indian Army convoy of 20 vehicles spotted moving north near Pangong Lake",
  "summary": "Indian Army convoy of approximately 20 vehicles was observed moving north along the Line of Actual Control near Pangong Lake.",
  "entities": [
    {
      "text": "Indian Army",
      "label": "ORG",
      "resolved": "Indian Army",
      "confidence": 0.75,
      "type": "organization",
      "metadata": {"spacy_label": "ORG"}
    },
    {
      "text": "Pangong Lake",
      "label": "LOC",
      "resolved": "Pangong Lake",
      "confidence": 0.70,
      "type": "location",
      "metadata": {"spacy_label": "LOC"}
    },
    {
      "text": "LAC",
      "label": "NORP",
      "resolved": "Line of Actual Control",
      "confidence": 0.85,
      "type": "geopolitical_entity",
      "metadata": {"note": "Inferred from 'LAC' -> 'Line of Actual Control'"}
    }
  ],
  "source_type": "twitter",
  "source_id": "1790123456789012456",
  "credibility_score": 0.82,
  "created_at": "2024-05-31T02:15:00Z"
}
```

### Media Forensics Analysis
```json
{
  "basic_info": {
    "format": "JPEG",
    "width": 1920,
    "height": 1080,
    "mode": "RGB",
    "size_bytes": 2457600,
    "aspect_ratio": 1.78
  },
  "exif_data": {
    "DateTimeOriginal": "2024:05-15 14:30:22",
    "Make": "Canon",
    "Model": "EOS R5",
    "GPSInfo": { ... },
    "GPS_Interpreted": {
      "latitude": 28.6139,
      "longitude": 77.2090,
      "altitude": 4350.0
    }
  },
  "perceptual_hashes": {
    "average_hash": "a1b2c3d4e5f67890",
    "perceptual_hash": "f0e1d2c3b4a59687",
    "difference_hash": "1122334455667788",
    "wavelet_hash": "9988776655443322"
  },
  "forensics_checks": {
    "has_transparency": false,
    "is_animated": false,
    "likely_photograph": true,
    "size_consistent": true,
    "file_type_consistent": true
  },
  "reverse_image_search": {
    "matches_found": 0,
    "search_note": "Reverse image search simulation - would connect to external APIs in production",
    "threat_database_note": "No matches in threat intelligence database"
  },
  "processing_note": "Analyzed JPEG image 1920x1080"
}
```

### Intelligence Briefing
```json
{
  "generated_at": "2024-05-31T03:55:00Z",
  "time_window_hours": 24,
  "event_count": 47,
  "executive_summary": "Multiple credible reports indicate increased military activity along the LAC in the Pangong Lake sector, with specific mentions of convoy movements and logistics preparations over the past 24 hours.",
  "key_events": [
    {
      "id": 1245,
      "text_preview": "Indian Army convoy of 20 vehicles spotted moving north near Pangong Lake...",
      "summary": "Indian Army convoy of approximately 20 vehicles was observed moving north along the Line of Actual Control near Pangong Lake.",
      "credibility_score": 0.91,
      "source_type": "twitter",
      "created_at": "2024-05-31T02:15:00Z",
      "entities_count": 8
    }
  ],
  "entity_analysis": {
    "top_entities": [
      {"text": "Pangong Lake", "count": 12},
      {"text": "Indian Army", "count": 10},
      {"text": "PLA", "count": 8},
      {"text": "Convoy", "count": 7}
    ],
    "entity_type_distribution": {
      "LOC": 15,
      "ORG": 12,
      "NORP": 8,
      "FAC": 5
    },
    "total_unique_entities": 29
  },
  "source_breakdown": {
    "source_distribution": {
      "twitter": 28,
      "telegram": 19
    },
    "average_credibility_by_source": {
      "twitter": 0.72,
      "telegram": 0.68
    },
    "total_sources": 2
  },
  "trends": [
    "High activity level: 2.1 events/hour (threshold: 1.5)",
    "Frequent mention of location: 'pangong lake' (12 mentions)",
    "Multiple high-credibility reports (≥0.7) received in the period (8 events)",
    "Diverse entity types detected: LOC, ORG, NORP, FAC"
  ],
  "processing_note": "Generated briefing from 47 events with time_window_hours=24"
}
```

## 🧪 Testing & Verification

### Backend Health Checks
```bash
# Check if all services are running
docker compose ps

# View backend logs for errors
docker compose logs backend | grep -i error

# Check database connectivity
docker compose exec backend pg_isready -U postgres

# Check Redis connectivity
docker compose exec backend redis-cli ping
```

### API Testing
```bash
# Test Twitter ingest endpoint
curl -X POST "http://localhost:8000/api/v1/ingest/twitter?query=test"

# Test media forensics (requires image file)
curl -X POST "http://localhost:8000/api/v1/ingest/media/analyze" \
     -F "file=@/path/to/test_image.jpg"

# Test briefing generation
curl -X GET "http://localhost:8000/api/v1/ingest/briefing/generate?time_window_hours=1"
```

### Sample Data Verification
```bash
# Check that events are being stored
curl -s "http://localhost:8000/api/v1/events?limit=1" | jq '.[0] | {id, text, summary, credibility_score, source_type}'

# Verify entities are properly structured
curl -s "http://localhost:8000/api/v1/events?limit=1" | jq '.[0].entities'

# Check for media analysis if images were processed
curl -s "http://localhost:8000/api/v1/events?limit=1" | jq '.[0] | select(.entities | length > 0)'
```

## 🚀 Next Steps for Enhancement

### Short-Term (1-2 Weeks)
1. **Frontend Enhancements**:
   - Event filtering by source type, credibility, time
   - Click-to-expand event details with analysis
   - Heatmap visualization of activity density
   - Timeline view for temporal analysis

2. **Analysis Improvements**:
   - Geotagging of events from EXIF data and location entities
   - Entity resolution expansion (ISO org codes, military unit IDs)
   - Sentiment analysis for threat assessment
   - Language detection and translation hints

3. **Operational Features**:
   - Export capabilities (CSV, JSON, PDF briefings)
   - Alerting mechanisms (email, webhook for high-cred events)
   - User authentication and role-based access
   - Audit logging for compliance

### Medium-Term (1-3 Months)
1. **Additional Sources**:
   - RSS/news feed ingestion
   - Dark web forum monitoring (Tor-safe)
   - Satellite imagery metadata extraction
   - Aviation/ship tracking (ADS-B, AIS)

2. **Advanced Analytics**:
   - Network analysis (entity relationship mapping)
   - Predictive modeling (activity forecasting)
   - Anomaly detection (unusual patterns)
   - Geo-fencing and alert zones

3. **Integration & Interoperability**:
   - STIX/TAXII output for threat sharing platforms
   - API keys rotation and management
   - Multi-tenancy for different units/departments
   - Backup and disaster recovery procedures

### Long-Term (3+ Months)
1. **AI/ML Enhancements** (Air-Gapped Compatible):
   - Fine-torable models for domain-specific NER
   - Image classification for equipment identification
   - Audio transcription for video analysis
   - Multi-modal fusion (text + image + geo)

2. **Deployable Variants**:
   - Ruggedized laptop/version for field operations
   - Kubernetes deployment for scalable cloud use
   - Disconnected operation with sync capability
   - Mobile app for forward-deployed analysts

3. **Training & Doctrine**:
   - Analyst training curriculum
   - Standard operating procedures (SOPs)
   - Intelligence product templates
   - Validation and accuracy metrics

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/), [spaCy](https://spacy.io/), [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot), [Pillow](https://python-pillow.org/), [imagehash](https://github.com/JohannesBuchner/imagehash), [Sumy](https://github.com/miso-belica/sumy)
- Inspired by defence intelligence requirements and OSINT best practices
- Special thanks to the open-source intelligence community

## 💬 Support

For questions, issues, or contributions:
- **Issues**: Use the GitHub Issues tab
- **Documentation**: Refer to this README and code docstrings
- **Deployment Help**: Check NEXT_STEPS.md for detailed instructions

---

**OSINT-Pro: Turning Open Source Data into Actionable Intelligence** 🔍📊🗺️

*Deployable in under 15 minutes. Mission-configurable. Air-gapped ready. Defence-relevant.*