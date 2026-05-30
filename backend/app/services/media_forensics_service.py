"""
Media Forensics Service for OSINT-Pro
Handles image processing, reverse image search simulations, and basic forensics
"""

import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image, ExifTags
import imagehash
import io
import os

logger = logging.getLogger(__name__)

class MediaForensicsService:
    """Service for analyzing images and media files for OSINT purposes"""
    
    def __init__(self):
        # Known hash databases for reverse image search simulation
        # In a real deployment, this would connect to actual reverse image search APIs
        # or maintain a local database of known hashes
        self.known_hashes = {}  # Would be populated from threat intel feeds
    
    def analyze_image(self, image_data: bytes) -> Dict[str, Any]:
        """
        Perform comprehensive image forensics analysis
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            Dictionary containing analysis results
        """
        if not image_data:
            return self._empty_result()
            
        try:
            # Open image from bytes
            image = Image.open(io.BytesIO(image_data))
            
            # Basic image info
            info = self._get_basic_info(image)
            
            # EXIF data extraction
            exif_data = self._extract_exif(image)
            
            # Perceptual hashes for reverse image search
            hashes = self._compute_perceptual_hashes(image)
            
            # Basic forensics checks
            forensics = self._basic_forensics_check(image)
            
            # Reverse image search simulation (placeholder)
            reverse_search_results = self._simulate_reverse_image_search(hashes)
            
            return {
                "basic_info": info,
                "exif_data": exif_data,
                "perceptual_hashes": hashes,
                "forensics_checks": forensics,
                "reverse_image_search": reverse_search_results,
                "processing_note": f"Analyzed {info.get('format', 'unknown')} image {info.get('width', 0)}x{info.get('height', 0)}"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "error": str(e),
                "processing_note": "Image analysis failed"
            }
    
    def _get_basic_info(self, image: Image.Image) -> Dict[str, Any]:
        """Extract basic image properties"""
        return {
            "format": image.format,
            "mode": image.mode,
            "width": image.width,
            "height": image.height,
            "size_bytes": len(image.tobytes()),
            "aspect_ratio": round(image.width / image.height, 2) if image.height > 0 else 0
        }
    
    def _extract_exif(self, image: Image.Image) -> Dict[str, Any]:
        """Extract and interpret EXIF data"""
        exif_data = {}
        try:
            if hasattr(image, '_getexif') and image._getexif() is not None:
                exif = image._getexif()
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = value
                    
            # Interpret GPS data if present
            gps_info = self._interpret_gps(exif_data)
            if gps_info:
                exif_data['GPS_Interpreted'] = gps_info
                
        except Exception as e:
            logger.warning(f"Could not extract EXIF data: {e}")
            exif_data["error"] = str(e)
            
        return exif_data
    
    def _interpret_gps(self, exif_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Convert GPS EXIF data to decimal degrees"""
        try:
            gps_info = {}
            if 'GPSInfo' in exif_data:
                gps_data = exif_data['GPSInfo']
                
                # Get latitude
                lat_ref = gps_data.get(1, 'N')  # 1 = LatitudeRef
                lat_dms = gps_data.get(2)       # 2 = Latitude
                if lat_dms and len(lat_dms) == 3:
                    lat = self._dms_to_decimal(lat_dms, lat_ref)
                    gps_info['latitude'] = lat
                
                # Get longitude
                lon_ref = gps_data.get(3, 'E')  # 3 = LongitudeRef
                lon_dms = gps_data.get(4)       # 4 = Longitude
                if lon_dms and len(lon_dms) == 3:
                    lon = self._dms_to_decimal(lon_dms, lon_ref)
                    gps_info['longitude'] = lon
                    
                return gps_info if gps_info else None
        except Exception as e:
            logger.warning(f"Could not interpret GPS data: {e}")
            
        return None
    
    def _dms_to_decimal(self, dms: Tuple[float, float, float], ref: str) -> float:
        """Convert degrees, minutes, seconds to decimal degrees"""
        degrees, minutes, seconds = dms
        decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
        if ref in ['S', 'W']:  # South and West are negative
            decimal = -decimal
        return decimal
    
    def _compute_perceptual_hashes(self, image: Image.Image) -> Dict[str, str]:
        """Compute various perceptual hashes for reverse image search"""
        try:
            # Different hash algorithms for different types of similarity
            hashes = {
                "average_hash": str(imagehash.average_hash(image)),
                "perceptual_hash": str(imagehash.phash(image)),
                "difference_hash": str(imagehash.dhash(image)),
                "wavelet_hash": str(imagehash.whash(image)),
                "color_hash": str(imagehash.colorhash(image)) if hasattr(imagehash, 'colorhash') else None
            }
            # Remove None values
            return {k: v for k, v in hashes.items() if v is not None}
        except Exception as e:
            logger.warning(f"Could not compute perceptual hashes: {e}")
            return {"error": str(e)}
    
    def _basic_forensics_check(self, image: Image.Image) -> Dict[str, Any]:
        """Perform basic forensics checks on image"""
        checks = {}
        
        try:
            # Check if image might be manipulated (basic checks)
            checks["has_transparency"] = image.mode in ('RGBA', 'LA', 'P') and 'transparency' in image.info
            
            # Check for animation (GIF)
            checks["is_animated"] = getattr(image, "is_animated", False)
            
            # Basic noise/blur assessment (simplified)
            # In a real implementation, we'd use more sophisticated techniques
            checks["likely_photograph"] = image.mode in ('RGB', 'L') and image.format in ('JPEG', 'PNG', 'TIFF')
            
            # File size consistency check
            expected_size = image.width * image.height * len(image.mode)
            actual_size = len(image.tobytes())
            checks["size_consistent"] = abs(expected_size - actual_size) < (expected_size * 0.5)  # Allow 50% variance
            
        except Exception as e:
            logger.warning(f"Forensics check error: {e}")
            checks["error"] = str(e)
            
        return checks
    
    def _simulate_reverse_image_search(self, hashes: Dict[str, str]) -> Dict[str, Any]:
        """
        Simulate reverse image search by comparing hashes against known database
        In production, this would connect to services like Google Images, TinEye, etc.
        or check against a threat intelligence database
        """
        results = {
            "matches_found": 0,
            "potential_matches": [],
            "search_note": "Reverse image search simulation - would connect to external APIs in production"
        }
        
        # Simulate checking against known threat image database
        # This is a placeholder - in reality, you'd check against:
        # - Known malware distribution images
        # - Propaganda material hashes
        # - Identified threat actor symbols
        # - etc.
        
        if hashes and not hashes.get("error"):
            # For demonstration, we'll check if any hash matches our known database
            matches = []
            for hash_type, hash_value in hashes.items():
                if hash_value in self.known_hashes:
                    matches.append({
                        "hash_type": hash_type,
                        "hash_value": hash_value,
                        "match_info": self.known_hashes[hash_value],
                        "confidence": 0.85  # Placeholder confidence
                    })
            
            if matches:
                results["matches_found"] = len(matches)
                results["potential_matches"] = matches
                results["search_note"] = f"Found {len(matches)} matches in threat intelligence database"
        
        return results
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            "basic_info": {},
            "exif_data": {},
            "perceptual_hashes": {},
            "forensics_checks": {},
            "reverse_image_search": {"matches_found": 0, "potential_matches": [], "search_note": "No image data provided"},
            "processing_note": "No image data to analyze"
        }
    
    def add_to_known_hashes(self, hash_value: str, info: Dict[str, Any]):
        """Add a hash to the known database (for threat intelligence)"""
        self.known_hashes[hash_value] = info
        logger.info(f"Added hash {hash_value} to known hashes database")

# Singleton instance
media_forensics_service = MediaForensicsService()

def analyze_image_data(image_data: bytes) -> Dict[str, Any]:
    """Convenience function to analyze image data"""
    return media_forensics_service.analyze_image(image_data)

def analyze_image_file(file_path: str) -> Dict[str, Any]:
    """Analyze an image file from disk"""
    try:
        with open(file_path, 'rb') as f:
            image_data = f.read()
        return analyze_image_data(image_data)
    except Exception as e:
        logger.error(f"Could not read image file {file_path}: {e}")
        return {"error": f"Could not read file: {str(e)}"}