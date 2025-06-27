# src/config/__init__.py
"""
Configuration settings for Costco HTML parser.
"""

from .settings import *

__all__ = [
    'AWS_REGION',
    'BEDROCK_MODEL_ID', 
    'HTML_DIRECTORY',
    'OUTPUT_DIRECTORY',
    'CONTENT_TYPE_PATTERNS',
    'IMAGE_SCORES',
    'ARTICLE_SELECTORS',
    'AI_CONFIG'
]