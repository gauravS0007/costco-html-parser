"""
Enhanced content schemas for Costco Connection articles.
Based on real content analysis of Recipe, Travel, Tech, Lifestyle, etc.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union
from enum import Enum


class ContentType(Enum):
    """Content type enumeration based on actual Costco Connection content."""
    RECIPE = "recipe"
    TRAVEL = "travel" 
    TECH = "tech"
    LIFESTYLE = "lifestyle"
    EDITORIAL = "editorial"
    SHOPPING = "shopping"
    MEMBER = "member"
    SEASONAL = "seasonal"


@dataclass
class BaseContent:
    """Base content structure shared by all content types."""
    title: str
    headline: str = ""
    byline: str = ""
    description: str = ""
    featured_image: str = ""
    image_alt: str = ""
    content_type: ContentType = ContentType.EDITORIAL
    tags: List[str] = field(default_factory=list)
    publish_date: str = ""


@dataclass 
class RecipeContent(BaseContent):
    """Recipe-specific content schema."""
    content_type: ContentType = ContentType.RECIPE
    
    # Recipe specifics
    ingredients: List[str] = field(default_factory=list)
    instructions: List[str] = field(default_factory=list)
    prep_time: str = ""
    cook_time: str = ""
    servings: str = ""
    difficulty: str = ""
    
    # Additional info
    recipe_source: str = ""
    recipe_author: str = ""
    nutritional_info: Dict[str, str] = field(default_factory=dict)
    equipment_needed: List[str] = field(default_factory=list)
    
    # Brand information
    brand_images: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class TravelContent(BaseContent):
    """Travel/vacation content schema."""
    content_type: ContentType = ContentType.TRAVEL
    
    # Author details (matching tech structure)
    author: Dict[str, Union[str, Dict[str, str]]] = field(default_factory=dict)
    
    # Travel specifics
    destinations: List[str] = field(default_factory=list)
    attractions: List[str] = field(default_factory=list)
    restaurants: List[str] = field(default_factory=list)
    activities: List[str] = field(default_factory=list)
    
    # Additional images (Alamo, city views, etc.)
    additional_images: List[Dict[str, str]] = field(default_factory=list)
    
    # Practical info
    best_time_to_visit: str = ""
    estimated_cost: str = ""
    travel_tips: List[str] = field(default_factory=list)
    cultural_notes: List[str] = field(default_factory=list)
    
    # Costco Travel integration
    costco_travel_packages: List[str] = field(default_factory=list)


@dataclass
class TechContent(BaseContent):
    """Enhanced tech content schema matching target structure."""
    content_type: ContentType = ContentType.TECH
    
    # Article metadata
    section_label: str = ""
    subheadline: str = ""
    publication: str = "Costco Connection"
    
    # Hero image with full details
    hero_image: Dict[str, str] = field(default_factory=dict)
    
    # Enhanced author object
    author: Dict[str, Union[str, Dict[str, str]]] = field(default_factory=dict)
    
    # Introduction paragraph
    intro_paragraph: str = ""
    
    # Callouts for supplementary content
    callouts: List[Dict[str, Union[str, List[str]]]] = field(default_factory=list)
    
    # Topic tags
    tags: List[str] = field(default_factory=list)
    
    # Legacy fields for backward compatibility
    products: List[str] = field(default_factory=list)
    brands: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    buying_guide: List[str] = field(default_factory=list)


@dataclass
class LifestyleContent(BaseContent):
    """Lifestyle/family content schema."""
    content_type: ContentType = ContentType.LIFESTYLE
    
    # Lifestyle specifics
    topics: List[str] = field(default_factory=list)
    life_stage: str = ""  # family, retirement, young adult, etc.
    wellness_tips: List[str] = field(default_factory=list)
    home_improvement: List[str] = field(default_factory=list)
    
    # Family focus
    family_activities: List[str] = field(default_factory=list)
    seasonal_content: List[str] = field(default_factory=list)


@dataclass
class EditorialContent(BaseContent):
    """Editorial/opinion content schema."""
    content_type: ContentType = ContentType.EDITORIAL
    
    # Editorial specifics
    editorial_type: str = ""  # publishers-note, opinion, commentary
    key_messages: List[str] = field(default_factory=list)
    call_to_action: str = ""
    
    # Company focus
    costco_values: List[str] = field(default_factory=list)
    member_benefits: List[str] = field(default_factory=list)


@dataclass
class ShoppingContent(BaseContent):
    """Shopping/product feature content schema."""
    content_type: ContentType = ContentType.SHOPPING
    
    # Shopping specifics
    featured_products: List[str] = field(default_factory=list)
    product_categories: List[str] = field(default_factory=list)
    seasonal_items: List[str] = field(default_factory=list)
    buying_tips: List[str] = field(default_factory=list)
    
    # Costco specific
    kirkland_signature: List[str] = field(default_factory=list)
    member_deals: List[str] = field(default_factory=list)
    warehouse_locations: List[str] = field(default_factory=list)


@dataclass
class MemberContent(BaseContent):
    """Member-focused content schema."""
    content_type: ContentType = ContentType.MEMBER
    
    # Member specifics
    member_stories: List[str] = field(default_factory=list)
    poll_questions: List[str] = field(default_factory=list)
    poll_results: Dict[str, str] = field(default_factory=dict)
    member_comments: List[str] = field(default_factory=list)
    
    # Community focus
    member_spotlights: List[str] = field(default_factory=list)
    community_events: List[str] = field(default_factory=list)


@dataclass
class EnhancedPageStructure:
    """Enhanced page structure with rich content schema."""
    url: str
    content: Union[RecipeContent, TravelContent, TechContent, LifestyleContent, 
                   EditorialContent, ShoppingContent, MemberContent]
    
    # SEO and metadata
    meta_title: str = ""
    meta_description: str = ""
    keywords: List[str] = field(default_factory=list)
    
    # Content structure
    sections: List[Dict[str, str]] = field(default_factory=list)
    related_articles: List[str] = field(default_factory=list)
    
    # Analytics
    content_quality_score: int = 0
    extraction_metadata: Dict = field(default_factory=dict)