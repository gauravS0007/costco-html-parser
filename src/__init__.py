# ===== src/__init__.py =====
"""
Costco HTML Parser - A modular AI-powered content extraction tool.
"""

__version__ = "2.0.0"
__author__ = "Your Name"

# Import main components for easy access
from .models.content_schemas import (
    ContentType, EnhancedPageStructure, RecipeContent, TravelContent,
    TechContent, LifestyleContent, EditorialContent, ShoppingContent, MemberContent
)

from .processors.enhanced_html_processor import EnhancedHTMLProcessor
from .processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

# Universal extractor for direct use
from .utils.universal_content_extractor import FixedUniversalContentExtractor

__all__ = [
    'ContentType', 'EnhancedPageStructure', 'RecipeContent', 'TravelContent',
    'TechContent', 'LifestyleContent', 'EditorialContent', 'ShoppingContent', 
    'MemberContent', 'EnhancedHTMLProcessor', 'FixedSuperEnhancedCostcoProcessor',
    'FixedUniversalContentExtractor'
]