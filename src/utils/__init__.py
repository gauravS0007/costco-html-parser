# ===== src/utils/__init__.py =====
"""
Utility modules for Costco HTML parser.
"""

# Original utilities
from .image_utils import fix_image_urls, score_image, get_scored_images, format_images_for_ai
from .content_detector import detect_content_type, get_content_byline

# Enhanced utilities
from .enhanced_content_detector import EnhancedContentDetector

# FIXED: Universal content extractor
from .universal_content_extractor import FixedUniversalContentExtractor, ExtractedContent

__all__ = [
    # Original utilities
    'fix_image_urls', 'score_image', 'get_scored_images', 'format_images_for_ai',
    'detect_content_type', 'get_content_byline',
    # Enhanced utilities
    'EnhancedContentDetector',
    # FIXED: Universal extractor
    'FixedUniversalContentExtractor', 'ExtractedContent'
]