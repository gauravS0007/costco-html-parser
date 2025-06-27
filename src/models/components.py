"""
Data models for Costco HTML parser components.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class BannerComponent:
    """Banner component with image and metadata."""
    title: str
    url: str
    alt: str
    width: int = 1200
    height: int = 800
    headline: str = ""
    byline: str = ""
    description: str = ""


@dataclass
class HeadlineComponent:
    """Headline component with styling."""
    headline_text: str
    color: str = "black"
    level: int = 1


@dataclass
class TeaserComponent:
    """Teaser component for article previews."""
    title: str
    description: str = ""
    image: str = ""
    alt_text: str = ""
    display_type: str = "compact"


@dataclass
class PageStructure:
    """Complete page structure with all components."""
    url: str
    banner: BannerComponent
    headlines: List[HeadlineComponent]
    teasers: List[TeaserComponent]
    metadata: Dict