import re
import json
import spacy
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Load spaCy model for NER
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    logger.warning("spaCy model not found. Please run: python -m spacy download en_core_web_sm")
    nlp = None

# Entity resolution databases
ISO_COUNTRY_CODES = {
    "AF": "Afghanistan", "AX": "Åland Islands", "AL": "Albania", "DZ": "Algeria",
    "AS": "American Samoa", "AD": "Andorra", "AO": "Angola", "AI": "Anguilla",
    "AQ": "Antarctica", "AG": "Antigua and Barbuda", "AR": "Argentina",
    "AM": "Armenia", "AW": "Aruba", "AU": "Australia", "AT": "Austria",
    "AZ": "Azerbaijan", "BS": "Bahamas", "BH": "Bahrain", "BD": "Bangladesh",
    "BB": "Barbados", "BY": "Belarus", "BE": "Belgium", "BZ": "Belize",
    "BJ": "Benin", "BM": "Bermuda", "BT": "Bhutan", "BO": "Bolivia",
    "BQ": "Bonaire, Sint Eustatius and Saba", "BA": "Bosnia and Herzegovina",
    "BW": "Botswana", "BV": "Bouvet Island", "BR": "Brazil",
    "IO": "British Indian Ocean Territory", "BN": "Brunei Darussalam",
    "BG": "Bulgaria", "BF": "Burkina Faso", "BI": "Burundi", "CV": "Cabo Verde",
    "KH": "Cambodia", "CM": "Cameroon", "CA": "Canada", "KY": "Cayman Islands",
    "CF": "Central African Republic", "TD": "Chad", "CL": "Chile",
    "CN": "China", "CX": "Christmas Island", "CC": "Cocos (Keeling) Islands",
    "CO": "Colombia", "KM": "Comoros", "CG": "Congo", "CD": "Congo, DR",
    "CK": "Cook Islands", "CR": "Costa Rica", "HR": "Croatia", "CU": "Cuba",
    "CW": "Curaçao", "CY": "Cyprus", "CZ": "Czechia", "CI": "Côte d'Ivoire",
    "DK": "Denmark", "DJ": "Djibouti", "DM": "Dominica", "DO": "Dominican Republic",
    "EC": "Ecuador", "EG": "Egypt", "SV": "El Salvador", "GQ": "Equatorial Guinea",
    "ER": "Eritrea", "EE": "Estonia", "SZ": "Eswatini", "ET": "Ethiopia",
    "FK": "Falkland Islands", "FO": "Faroe Islands", "FJ": "Fiji", "FI": "Finland",
    "FR": "France", "GF": "French Guiana", "PF": "French Polynesia",
    "TF": "French Southern Territories", "GA": "Gabon", "GM": "Gambia",
    "GE": "Georgia", "DE": "Germany", "GH": "Ghana", "GI": "Gibraltar",
    "GR": "Greece", "GL": "Greenland", "GD": "Grenada", "GP": "Guadeloupe",
    "GU": "Guam", "GT": "Guatemala", "GG": "Guernsey", "GN": "Guinea",
    "GW": "Guinea-Bissau", "GY": "Guyana", "HT": "Haiti", "HM": "Heard Island and McDonald Islands",
    "VA": "Holy See", "HN": "Honduras", "HK": "Hong Kong", "HU": "Hungary",
    "IS": "Iceland", "IN": "India", "ID": "Indonesia", "IR": "Iran, Islamic Republic of",
    "IQ": "Iraq", "IE": "Ireland", "IM": "Isle of Man", "IL": "Israel",
    "IT": "Italy", "JM": "Jamaica", "JP": "Japan", "JE": "Jersey",
    "JO": "Jordan", "KZ": "Kazakhstan", "KE": "Kenya", "KI": "Kiribati",
    "KP": "Korea, North", "KR": "Korea, South", "KW": "Kuwait", "KG": "Kyrgyzstan",
    "LA": "Lao PDR", "LV": "Latvia", "LB": "Lebanon", "LS": "Lesotho",
    "LR": "Liberia", "LY": "Libya", "LI": "Liechtenstein", "LT": "Lithuania",
    "LU": "Luxembourg", "MO": "Macao", "MG": "Madagascar", "MW": "Malawi",
    "MY": "Malaysia", "MV": "Maldives", "ML": "Mali", "MT": "Malta",
    "MH": "Marshall Islands", "MQ": "Martinique", "MR": "Mauritania",
    "MU": "Mauritius", "YT": "Mayotte", "MX": "Mexico", "FM": "Micronesia",
    "MD": "Moldova", "MC": "Monaco", "MN": "Mongolia", "ME": "Montenegro",
    "MS": "Montserrat", "MA": "Morocco", "MZ": "Mozambique", "MM": "Myanmar",
    "NA": "Namibia", "NR": "Nauru", "NP": "Nepal", "NL": "Netherlands",
    "NC": "New Caledonia", "NZ": "New Zealand", "NI": "Nicaragua", "NE": "Niger",
    "NG": "Nigeria", "NU": "Niue", "NF": "Norfolk Island", "MK": "North Macedonia",
    "MP": "Northern Mariana Islands", "NO": "Norway", "OM": "Oman",
    "PK": "Pakistan", "PW": "Palau", "PS": "Palestine, State of",
    "PA": "Panama", "PG": "Papua New Guinea", "PY": "Paraguay", "PE": "Peru",
    "PH": "Philippines", "PN": "Pitcairn", "PL": "Poland", "PT": "Portugal",
    "PR": "Puerto Rico", "QA": "Qatar", "RE": "Réunion", "RO": "Romania",
    "RU": "Russian Federation", "RW": "Rwanda", "BL": "Saint Barthélemy",
    "SH": "Saint Helena, Ascension and Tristan da Cunha", "KN": "Saint Kitts and Nevis",
    "LC": "Saint Lucia", "MF": "Saint Martin (French part)", "PM": "Saint Pierre and Miquelon",
    "VC": "Saint Vincent and the Grenadines", "WS": "Samoa", "SM": "San Marino",
    "ST": "Sao Tome and Principe", "SA": "Saudi Arabia", "SN": "Senegal",
    "RS": "Serbia", "SC": "Seychelles", "SL": "Sierra Leone", "SG": "Singapore",
    "SX": "Sint Maarten (Dutch part)", "SK": "Slovakia", "SI": "Slovenia",
    "SB": "Solomon Islands", "SO": "Somalia", "ZA": "South Africa",
    "GS": "South Georgia and the South Sandwich Islands", "SS": "South Sudan",
    "ES": "Spain", "LK": "Sri Lanka", "SD": "Sudan", "SR": "Suriname",
    "SJ": "Svalbard and Jan Mayen", "SE": "Sweden", "CH": "Switzerland",
    "SY": "Syrian Arab Republic", "TW": "Taiwan", "TJ": "Tajikistan",
    "TZ": "Tanzania, United Republic of", "TH": "Thailand", "TL": "Timor-Leste",
    "TG": "Togo", "TK": "Tokelau", "TO": "Tonga", "TT": "Trinidad and Tobago",
    "TN": "Tunisia", "TR": "Turkey", "TM": "Turkmenistan", "TC": "Turks and Caicos Islands",
    "TV": "Tuvalu", "UG": "Uganda", "UA": "Ukraine", "AE": "United Arab Emirates",
    "GB": "United Kingdom", "US": "United States", "UM": "United States Minor Outlying Islands",
    "UY": "Uruguay", "UZ": "Uzbekistan", "VU": "Vanuatu", "VE": "Venezuela",
    "VN": "Vietnam", "VG": "British Virgin Islands", "VI": "US Virgin Islands",
    "WF": "Wallis and Futuna", "EH": "Western Sahara", "YE": "Yemen", "ZM": "Zambia",
    "ZW": "Zimbabwe"
}

# Common military/NATO symbols and terms for entity resolution
NATO_SYMBOLS = {
    # Unit sizes/symbols
    "SQD": "Squad", "PLT": "Platoon", "COY": "Company", "BTN": "Battalion",
    "REGT": "Regiment", "BDE": "Brigade", "DIV": "Division", "CORPS": "Corps",
    "ARMY": "Army", "ARMYGP": "Army Group",
    
    # Common military terms
    "INF": "Infantry", "ARM": "Armour", "ART": "Artillery", "ENG": "Engineers",
    "SIG": "Signals", "LOG": "Logistics", "MED": "Medical", "INT": "Intelligence",
    "AVN": "Aviation", "ABN": "Airborne", "MTZ": "Mechanized",
    
    # Equipment
    "MBT": "Main Battle Tank", "IFV": "Infantry Fighting Vehicle",
    "APC": "Armoured Personnel Carrier", "SPG": "Self-Propelled Gun",
    "MRL": "Multiple Rocket Launcher", "SAM": "Surface-to-Air Missile",
    "ATGM": "Anti-Tank Guided Missile", "MANPADS": "Man-Portable Air-Defence System",
    
    # Operations
    "OBS": "Observation", "RECCE": "Reconnaissance", "PAT": "Patrol",
    "AMB": "Ambush", "RAID": "Raid", "SEARCH": "Search and Destroy",
    "CLEAR": "Clear and Hold", "DEF": "Defensive", "OFF": "Offensive"
}

def resolve_entity(entity_text: str, entity_label: str = None) -> Dict[str, Any]:
    """
    Resolve extracted entity to known databases (ISO country codes, NATO symbols, etc.)
    Returns dict with resolved info and confidence score.
    """
    if not entity_text:
        return {"original": entity_text, "resolved": None, "confidence": 0.0, "type": "unknown"}
    
    entity_upper = entity_text.strip().upper()
    entity_clean = entity_text.strip()
    
    # Try ISO country codes (2-letter)
    if len(entity_upper) == 2 and entity_upper in ISO_COUNTRY_CODES:
        return {
            "original": entity_text,
            "resolved": ISO_COUNTRY_CODES[entity_upper],
            "confidence": 0.95,
            "type": "country",
            "code": entity_upper
        }
    
    # Try NATO symbols
    if entity_upper in NATO_SYMBOLS:
        return {
            "original": entity_text,
            "resolved": NATO_SYMBOLS[entity_upper],
            "confidence": 0.90,
            "type": "military_symbol",
            "code": entity_upper
        }
    
    # Try partial matches for longer entities (e.g., "United States" -> "US")
    if len(entity_clean.split()) >= 2:
        # Simple heuristic: take first letters of each word
        acronym = ''.join(word[0].upper() for word in entity_clean.split() if word[0].isalpha())
        if len(acronym) == 2 and acronym in ISO_COUNTRY_CODES:
            return {
                "original": entity_text,
                "resolved": ISO_COUNTRY_CODES[acronym],
                "confidence": 0.80,
                "type": "country",
                "code": acronym,
                "note": f"Inferred from '{entity_clean}' -> '{acronym}'"
            }
    
    # If spaCy is available, use its entity type for better classification
    if nlp and entity_label:
        # Map spaCy labels to our types
        label_mapping = {
            "GPE": "geopolitical_entity",  # Countries, cities, states
            "LOC": "location",           # Non-GPE locations
            "ORG": "organization",       # Companies, agencies, etc.
            "PER": "person",             # People
            "FAC": "facility",           # Buildings, airports, etc.
            "EVENT": "event",            # Named events
            "WORK_OF_ART": "work_of_art", # Books, songs, etc.
            "LAW": "law",                # Laws, documents
            "LANGUAGE": "language",      # Languages
            "DATE": "date",              # Dates
            "TIME": "time",              # Times
            "PERCENT": "percent",        # Percentages
            "MONEY": "money",            # Monetary values
            "QUANTITY": "quantity",      # Measurements
            "ORDINAL": "ordinal",        # Ordinals
            "CARDINAL": "cardinal"       # Cardinals
        }
        
        entity_type = label_mapping.get(entity_label, "unknown")
        return {
            "original": entity_text,
            "resolved": entity_text,  # Keep original as resolved value
            "confidence": 0.70,      # Moderate confidence for NER entities
            "type": entity_type,
            "spacy_label": entity_label
        }
    
    # Default fallback
    return {
        "original": entity_text,
        "resolved": entity_text,
        "confidence": 0.50,
        "type": "unknown"
    }

def summarize_text(text: str, max_sentences: int = 3) -> str:
    """
    Create an extractive summary using TextRank algorithm.
    Returns summary with specified number of sentences.
    """
    if not text or len(text.strip()) == 0:
        return ""
    
    try:
        parser = PlaintextParser.from_string(text, Tokenizer("english"))
        summarizer = TextRankSummarizer()
        summary_sentences = summarizer(parser.document, max_sentences)
        
        # Join sentences back together
        summary = ' '.join([str(sentence) for sentence in summary_sentences])
        return summary.strip()
    except Exception as e:
        logger.warning(f"TextRank summarization failed: {e}. Falling back to simple truncation.")
        # Fallback to simple method
        if len(text) <= 200:
            return text
        summary = text[:200]
        last_period = summary.rfind('.')
        last_space = summary.rfind(' ')
        if last_period > 140:  # If we found a period in the latter 30%
            return summary[:last_period+1]
        elif last_space > 160:  # If we found a space in the latter 20%
            return summary[:last_space]
        else:
            return summary + "..."

def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract entities using spaCy NER with confidence scoring and entity resolution.
    Returns list of dicts containing entity info.
    """
    if not text or len(text.strip()) == 0:
        return []
    
    entities = []
    
    if nlp:
        # Use spaCy for NER
        doc = nlp(text)
        seen_entities = set()  # Avoid duplicates
        
        for ent in doc.ents:
            # Normalize entity text for deduplication
            normalized = ent.text.strip().lower()
            if normalized in seen_entities:
                continue
            seen_entities.add(normalized)
            
            # Resolve entity to known databases
            resolved_info = resolve_entity(ent.text, ent.label_)
            
            entities.append({
                "text": ent.text,
                "start": ent.start_char,
                "end": ent.end_char,
                "label": ent.label_,
                "resolved": resolved_info["resolved"],
                "confidence": resolved_info["confidence"],
                "type": resolved_info["type"],
                "metadata": {
                    "code": resolved_info.get("code"),
                    "note": resolved_info.get("note"),
                    "spacy_label": resolved_info.get("spacy_label")
                }
            })
    else:
        # Fallback to regex-based extraction if spaCy not available
        # (This is the original implementation for backward compatibility)
        regex_entities = _extract_entities_regex(text)
        for entity_text in regex_entities:
            resolved_info = resolve_entity(entity_text)
            entities.append({
                "text": entity_text,
                "start": text.find(entity_text) if entity_text in text else 0,
                "end": text.find(entity_text) + len(entity_text) if entity_text in text else len(entity_text),
                "label": "UNKNOWN",  # Regex doesn't provide labels
                "resolved": resolved_info["resolved"],
                "confidence": resolved_info["confidence"],
                "type": resolved_info["type"],
                "metadata": {
                    "code": resolved_info.get("code"),
                    "note": resolved_info.get("note")
                }
            })
    
    return entities

def _extract_entities_regex(text: str) -> List[str]:
    """
    Original regex-based entity extraction (fallback when spaCy unavailable).
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
    
    # Pattern 3: Capitalized words (potential proper nouns)
    words = re.findall(r'\b[A-Z][a-z]+\b', text)
    entities.update(words)
    
    # Pattern 4: Acronyms (all caps, 2+ letters)
    acronym_pattern = r'\b[A-Z]{2,}\b'
    matches = re.findall(acronym_pattern, text)
    entities.update(matches)
    
    return list(entities)

def analyze_content(text: str) -> Dict[str, Any]:
    """
    Main function to perform content analysis: summarization + entity extraction + resolution.
    Returns dict with summary, entities, and processing metadata.
    """
    if not text:
        return {
            "summary": "",
            "entities": [],
            "processing_note": "No text provided"
        }
    
    # Generate summary
    summary = summarize_text(text, max_sentences=3)
    
    # Extract and resolve entities
    entities = extract_entities(text)
    
    # Calculate overall confidence
    if entities:
        avg_confidence = sum(e["confidence"] for e in entities) / len(entities)
    else:
        avg_confidence = 0.0
    
    return {
        "summary": summary,
        "entities": entities,
        "processing_note": f"Processed {len(entities)} entities with avg confidence {avg_confidence:.2f}",
        "entity_count": len(entities),
        "average_confidence": round(avg_confidence, 3)
    }