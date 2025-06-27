"""
Image processing utilities for Costco HTML parser.
"""

import re
import logging
from bs4 import BeautifulSoup
from typing import List, Tuple
from ..config.settings import IMAGE_SCORES, PROMOTIONAL_TERMS

logger = logging.getLogger(__name__)


def fix_image_urls(html_content: str, original_url: str) -> str:
    """
    Fix relative image URLs to absolute URLs.
    
    Args:
        html_content: HTML content as string
        original_url: Original page URL for context
        
    Returns:
        HTML content with fixed image URLs
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    fixed_count = 0

    for img in soup.find_all('img'):
        src = img.get('src', '')

        if src.startswith('./') or src.startswith('../'):
            filename = src.split('/')[-1]

            # Extract date from filename (format: 09_23_...)
            date_match = re.search(r'(\d{2})_(\d{2})', filename)
            if date_match:
                month_num, year_num = date_match.groups()

                month_names = {
                    '01': 'january', '02': 'february', '03': 'march',
                    '04': 'april', '05': 'may', '06': 'june',
                    '07': 'july', '08': 'august', '09': 'september',
                    '10': 'october', '11': 'november', '12': 'december'
                }

                month_name = month_names.get(month_num, 'october')
                folder = f"static-us-connection-{month_name}-{year_num}"
                new_url = f"https://mobilecontent.costco.com/live/resource/img/{folder}/{filename}"

                img['src'] = new_url
                fixed_count += 1
                logger.info(f"Fixed image: {filename}")

        elif src.startswith('/live/resource/img/'):
            new_url = f"https://mobilecontent.costco.com{src}"
            img['src'] = new_url
            fixed_count += 1

    logger.info(f"Fixed {fixed_count} image URLs")
    return str(soup)


def score_image(src: str, alt: str, content_type: str, is_in_article: bool) -> int:
    """
    Score image relevance based on multiple factors.
    
    Args:
        src: Image source URL
        alt: Image alt text
        content_type: Detected content type
        is_in_article: Whether image is in main article area
        
    Returns:
        Image relevance score
    """
    score = 0
    src_lower = src.lower()
    alt_lower = alt.lower()

    # Boost for article area images
    if is_in_article:
        score += IMAGE_SCORES['article_area_boost']

    # Boost for Costco content domain
    if 'mobilecontent.costco.com' in src_lower:
        score += IMAGE_SCORES['costco_domain_boost']

    # Boost for Connection magazine images
    if 'static-us-connection' in src_lower:
        score += IMAGE_SCORES['connection_magazine_boost']

    # Content-specific scoring
    score += _get_content_specific_score(content_type, alt_lower)

    # Penalize promotional/navigation images
    for term in PROMOTIONAL_TERMS:
        if term in src_lower:
            score += IMAGE_SCORES['promo_penalty']

    # Boost descriptive alt text
    if len(alt) > 8 and len(alt.split()) >= 3:
        score += IMAGE_SCORES['descriptive_alt_boost']

    return score


def _get_content_specific_score(content_type: str, alt_lower: str) -> int:
    """Get content-type specific image scoring."""
    score = 0
    
    if content_type == 'publishers-note':
        if any(term in alt_lower for term in ['publisher', 'editorial', 'note']):
            score += 30
        # Heavy penalty for promotional content
        if any(term in alt_lower for term in ['golf', 'vacation', 'travel', 'deal']):
            score += IMAGE_SCORES['promotional_penalty']

    elif content_type == 'recipe':
        if any(term in alt_lower for term in ['food', 'recipe', 'ingredient', 'dish']):
            score += 30

    elif content_type == 'travel':
        if any(term in alt_lower for term in ['destination', 'city', 'travel']):
            score += 30

    return score


def get_scored_images(soup: BeautifulSoup, article_area, content_type: str) -> List[Tuple[int, str, str, str]]:
    """
    Get and score all images from the page.
    
    Args:
        soup: BeautifulSoup object of the page
        article_area: Main article content area
        content_type: Detected content type
        
    Returns:
        List of tuples (score, src, alt, source_type)
    """
    scored_images = []

    # Get article images first (higher priority)
    if article_area:
        for img in article_area.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                score = score_image(src, alt, content_type, True)
                scored_images.append((score, src, alt, 'ARTICLE'))

    # Get other images
    for img in soup.find_all('img'):
        src = img.get('src', '')
        alt = img.get('alt', '')
        if src and not any(existing[1] == src for existing in scored_images):
            score = score_image(src, alt, content_type, False)
            scored_images.append((score, src, alt, 'OTHER'))

    # Sort by score (highest first)
    scored_images.sort(key=lambda x: x[0], reverse=True)
    return scored_images


def format_images_for_ai(scored_images: List[Tuple[int, str, str, str]], max_images: int = 10) -> str:
    """
    Format scored images for AI prompt.
    
    Args:
        scored_images: List of scored images
        max_images: Maximum number of images to include
        
    Returns:
        Formatted string for AI prompt
    """
    images_list = []
    threshold = IMAGE_SCORES['minimum_quality_threshold']
    
    for score, src, alt, source in scored_images[:max_images]:
        if score > threshold:
            if score >= 150:
                marker = "🎯 PERFECT"
            elif score >= 100:
                marker = "⭐ EXCELLENT"
            elif score >= 50:
                marker = "✓ GOOD"
            else:
                marker = "~ OK"
            images_list.append(f"{marker} ({source}): {src} | Alt: {alt}")
        elif len(images_list) < 3:
            images_list.append(f"❌ POOR ({source}): {src} | Alt: {alt}")

    return '\n'.join(images_list) if images_list else "No good images found"