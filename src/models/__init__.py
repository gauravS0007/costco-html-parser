# ===== src/models/__init__.py =====
"""
Data models for Costco HTML parser.
"""

# Import original components
from .components import BannerComponent, HeadlineComponent, TeaserComponent, PageStructure

# Import enhanced content schemas
from .content_schemas import (
    ContentType, BaseContent, EnhancedPageStructure, 
    RecipeContent, TravelContent, TechContent, LifestyleContent,
    EditorialContent, ShoppingContent, MemberContent
)

__all__ = [
    # Original components
    'BannerComponent', 'HeadlineComponent', 'TeaserComponent', 'PageStructure',
    # Enhanced schemas
    'ContentType', 'BaseContent', 'EnhancedPageStructure', 
    'RecipeContent', 'TravelContent', 'TechContent', 'LifestyleContent',
    'EditorialContent', 'ShoppingContent', 'MemberContent'
]
