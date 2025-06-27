"""
Configuration settings for Costco HTML parser.
"""

import os
from typing import Dict, List

# AWS Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# File Processing
HTML_DIRECTORY = "data/html_files"
OUTPUT_DIRECTORY = "data/results"
SUPPORTED_EXTENSIONS = ['*.html', '*.htm']

# Content Type Detection Patterns
CONTENT_TYPE_PATTERNS = {
    'publishers-note': {
        'keywords': ['publisher', 'note', 'passion', 'editorial'],
        'filename_hints': ['publisher', 'note', 'passion'],
        'byline': 'By Costco Connection'
    },
    'recipe': {
        'keywords': ['recipe', 'ingredients', 'cooking', 'directions'],
        'filename_hints': ['recipe'],
        'byline': 'By Costco Kitchen Team'
    },
    'travel': {
        'keywords': ['travel', 'destination', 'cities', 'vacation'],
        'filename_hints': ['travel'],
        'byline': 'By Costco Travel'
    },
    'member-poll': {
        'keywords': ['poll', 'survey', 'members respond', 'autumn'],
        'filename_hints': ['poll', 'member'],
        'byline': 'By Member Services'
    },
    'tech': {
        'keywords': ['tech', 'technology', 'power up', 'gadget'],
        'filename_hints': ['tech'],
        'byline': 'By Tech Connection'
    },
    'costco-life': {
        'keywords': ['costco life', 'celebrate', 'family'],
        'filename_hints': ['costco life', 'celebrate'],
        'byline': 'By Costco Connection'
    }
}

# Image Scoring Configuration
IMAGE_SCORES = {
    'article_area_boost': 100,
    'costco_domain_boost': 50,
    'connection_magazine_boost': 30,
    'descriptive_alt_boost': 20,
    'promo_penalty': -40,
    'promotional_penalty': -60,
    'minimum_quality_threshold': 20
}

# Article Content Selectors
ARTICLE_SELECTORS = [
    '.article-content', 
    '.post-content', 
    '.entry-content',
    'article', 
    '[role="main"]', 
    '.main-content'
]

# Navigation Terms to Skip
NAVIGATION_TERMS = [
    'nav', 'header', 'footer', 'menu', 'shop', 
    'department', 'compare', 'lenses', 'costco travel'
]

# Promotional Terms for Image Filtering
PROMOTIONAL_TERMS = [
    'espot', 'hero', 'banner', 'nav', 'logo', 
    'membership', 'golf', 'vacation', 'travel', 'deal'
]

# AI Configuration
AI_CONFIG = {
    'max_tokens': 4000,
    'temperature': 0.1,
    'max_images_to_analyze': 10,
    'max_content_length': 12000
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(levelname)s - %(message)s'
}