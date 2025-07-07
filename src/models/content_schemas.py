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
    MAGAZINE_FRONT_COVER = "magazine_front_cover"
    UNKNOWN = "unknown"


@dataclass
class BaseContent:
    """Base content structure shared by all content types."""
    title: str
    headline: str = ""
    byline: str = ""
    description: str = ""
    featured_image: str = ""
    image_alt: str = ""
    image_caption: str = ""
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
    
    # Seasonal focus
    seasonal_content: List[str] = field(default_factory=list)


@dataclass
class EditorialContent(BaseContent):
    """Editorial/opinion content schema."""
    content_type: ContentType = ContentType.EDITORIAL
    
    # Editorial specifics
    editorial_type: str = ""  # publishers-note, opinion, commentary
    call_to_action: str = ""
    
    # Author details (matching tech/travel structure)
    author: Dict[str, Union[str, Dict[str, str]]] = field(default_factory=dict)
    
    # Organized editorial content structure
    editorial_article: Dict[str, Union[str, List[str]]] = field(default_factory=dict)
    upcoming_features: Dict[str, str] = field(default_factory=dict)
    editorial_staff: Dict[str, Union[Dict[str, str], List[str], Dict[str, Union[str, List[str]]]]] = field(default_factory=dict)
    legal_disclaimers: List[str] = field(default_factory=list)
    
    # Legacy fields for backward compatibility
    key_messages: List[str] = field(default_factory=list)
    costco_values: List[str] = field(default_factory=list)
    member_benefits: List[str] = field(default_factory=list)
    main_content_paragraphs: List[str] = field(default_factory=list)
    product_highlights: List[str] = field(default_factory=list)
    upcoming_content: List[str] = field(default_factory=list)
    sidebar_content: List[str] = field(default_factory=list)


@dataclass
class ShoppingContent(BaseContent):
    """Shopping/product feature content schema."""
    content_type: ContentType = ContentType.SHOPPING
    
    # Shopping specifics
    product_categories: List[str] = field(default_factory=list)
    seasonal_items: List[str] = field(default_factory=list)
    buying_tips: List[str] = field(default_factory=list)
    
    # Costco specific
    kirkland_signature: List[str] = field(default_factory=list)
    member_deals: List[str] = field(default_factory=list)
    warehouse_locations: List[str] = field(default_factory=list)
    author: Dict[str, Union[str, Dict[str, str]]] = field(default_factory=dict)

@dataclass
class MemberContent(BaseContent):
    """Member-focused content schema with structured sections."""
    content_type: ContentType = ContentType.MEMBER
    
    # Structured member content sections
    member_sections: List[Dict[str, Union[str, Dict[str, str]]]] = field(default_factory=list)
    
    # Poll-specific content
    poll_questions: List[str] = field(default_factory=list)
    poll_results: Dict[str, Union[str, int, List[str]]] = field(default_factory=dict)
    
    # Member responses and interactions
    member_responses: List[Dict[str, str]] = field(default_factory=list)
    
    # Contact and additional content sections
    contact_info: Dict[str, str] = field(default_factory=dict)
    additional_sections: List[Dict[str, Union[str, Dict[str, str]]]] = field(default_factory=list)
    
    # Legacy fields for backward compatibility
    member_stories: List[str] = field(default_factory=list)
    member_comments: List[str] = field(default_factory=list)
    member_spotlights: List[str] = field(default_factory=list)
    community_events: List[str] = field(default_factory=list)


@dataclass
class MagazineFrontCoverContent(BaseContent):
    """Magazine front cover content schema for Costco Connection front pages."""
    content_type: ContentType = ContentType.MAGAZINE_FRONT_COVER
    
    # Cover story information
    cover_story: Dict[str, str] = field(default_factory=dict)  # title, description, link
    cover_image: str = ""
    cover_image_alt: str = ""
    
    # Magazine sections and article categories
    in_this_issue: List[Dict[str, str]] = field(default_factory=list)  # article previews
    special_sections: List[Dict[str, str]] = field(default_factory=list)  # special themed sections
    featured_sections: List[Dict[str, str]] = field(default_factory=list)  # regular magazine sections
    
    # Article links organized by category
    article_categories: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)
    
    # Magazine metadata
    issue_date: str = ""
    volume_number: str = ""
    pdf_download_link: str = ""
    
    # Navigation and additional content
    navigation_sections: List[Dict[str, Union[str, List[str]]]] = field(default_factory=list)
    subscription_info: Dict[str, str] = field(default_factory=dict)


@dataclass
class UnknownContent(BaseContent):
    """Unknown content schema for unmatched content types."""
    content_type: ContentType = ContentType.UNKNOWN
    
    # Raw content preservation
    raw_content: str = ""
    detected_patterns: List[str] = field(default_factory=list)
    
    # Content analysis metadata
    content_analysis: Dict[str, Union[str, int, List[str]]] = field(default_factory=dict)
    potential_categories: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    
    # Structure analysis
    content_structure: Dict[str, int] = field(default_factory=dict)  # headings, paragraphs, lists count
    extracted_entities: List[str] = field(default_factory=list)  # names, places, products mentioned
    
    # Processing metadata
    processing_notes: List[str] = field(default_factory=list)
    requires_manual_review: bool = True


@dataclass
class EnhancedPageStructure:
    """Enhanced page structure with rich content schema."""
    url: str
    content: Union[RecipeContent, TravelContent, TechContent, LifestyleContent, 
                   EditorialContent, ShoppingContent, MemberContent, MagazineFrontCoverContent, UnknownContent]
    
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