"""
Content type detection utilities for Costco HTML parser.
"""

import logging
from typing import Dict
from ..config.settings import CONTENT_TYPE_PATTERNS

logger = logging.getLogger(__name__)


def detect_content_type(html_content: str, url: str, filename: str) -> Dict[str, str]:
    """
    Detect Costco content type based on content, URL, and filename.
    
    Args:
        html_content: HTML content as string
        url: Page URL
        filename: Source filename
        
    Returns:
        Dictionary with content_type, byline, and score
    """
    text_content = html_content.lower()
    url_lower = url.lower()
    filename_lower = filename.lower()

    best_type = 'general'
    best_score = 0

    for content_type, config in CONTENT_TYPE_PATTERNS.items():
        score = _calculate_content_score(
            content_type, config, text_content, url_lower, filename_lower
        )
        
        if score > best_score:
            best_score = score
            best_type = content_type

    result = CONTENT_TYPE_PATTERNS.get(best_type, {'byline': 'By Costco Connection'})
    logger.info(f"Detected content type: {best_type} (score: {best_score})")

    return {
        'content_type': best_type,
        'byline': result['byline'],
        'score': best_score
    }


def _calculate_content_score(content_type: str, config: Dict, text_content: str, 
                           url_lower: str, filename_lower: str) -> int:
    """
    Calculate content type score based on various factors.
    
    Args:
        content_type: Type being evaluated
        config: Configuration for this content type
        text_content: Lowercased HTML content
        url_lower: Lowercased URL
        filename_lower: Lowercased filename
        
    Returns:
        Calculated score
    """
    score = 0

    # Check filename (highest priority - 10 points each)
    for hint in config['filename_hints']:
        if hint in filename_lower:
            score += 10

    # Check URL (medium priority - 5 points)
    if content_type.replace('-', '') in url_lower:
        score += 5

    # Check content keywords (low priority - 1 point each)
    for keyword in config['keywords']:
        if keyword in text_content:
            score += 1

    return score


def get_content_byline(content_type: str) -> str:
    """
    Get the appropriate byline for a content type.
    
    Args:
        content_type: Detected content type
        
    Returns:
        Appropriate byline string
    """
    config = CONTENT_TYPE_PATTERNS.get(content_type, {})
    return config.get('byline', 'By Costco Connection')