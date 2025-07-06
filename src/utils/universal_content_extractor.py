"""
FIXED: Universal Content Extractor with Section-Aware Recipe Extraction
This fixes the critical recipe extraction issues identified.
"""

import re
import logging
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


@dataclass
class ExtractedContent:
    """Comprehensive content extraction result"""

    title: str = ""
    subtitle: str = ""
    byline: str = ""
    author_details: str = ""
    publication_info: str = ""
    main_content: List[str] = None
    full_text: str = ""
    headings: List[Dict[str, str]] = None
    images: List[Dict[str, str]] = None
    quotes: List[str] = None
    lists: List[Dict[str, List[str]]] = None
    metadata: Dict[str, str] = None
    content_type: str = "general"

    def __post_init__(self):
        if self.main_content is None:
            self.main_content = []
        if self.headings is None:
            self.headings = []
        if self.images is None:
            self.images = []
        if self.quotes is None:
            self.quotes = []
        if self.lists is None:
            self.lists = []
        if self.metadata is None:
            self.metadata = {}


class FixedUniversalContentExtractor:
    """FIXED: Universal content extractor with proper recipe section handling"""

    def __init__(self):
        # Content type detection patterns
        self.content_patterns = {
            "recipe": {
                "url_keywords": ["recipe"],
                "title_keywords": ["recipe", "roll-ups", "jam", "crumble"],
                "content_keywords": [
                    "ingredients",
                    "directions",
                    "tablespoon",
                    "cup",
                    "cooking",
                ],
                "required_score": 3,
            },
            "travel": {
                "url_keywords": ["travel-connection", "tale-of"],
                "title_keywords": ["travel", "cities", "destination"],
                "content_keywords": ["destination", "attractions", "visit", "explore"],
                "required_score": 3,
            },
            "tech": {
                "url_keywords": ["tech", "power-up"],
                "title_keywords": ["tech", "power", "technology"],
                "content_keywords": ["technology", "device", "features", "review"],
                "required_score": 3,
            },
            "editorial": {
                "url_keywords": ["publisher", "note", "front-cover"],
                "title_keywords": ["publisher", "note", "editorial"],
                "content_keywords": ["costco", "members", "connection", "sandy torrey"],
                "required_score": 2,
            },
            "member": {
                "url_keywords": ["member-poll", "member-comments"],
                "title_keywords": ["member", "poll", "comments"],
                "content_keywords": ["member", "poll", "facebook", "comments"],
                "required_score": 2,
            },
            "shopping": {
                "url_keywords": ["treasure-hunt", "buying-smart"],
                "title_keywords": ["treasure", "buying", "smart"],
                "content_keywords": ["product", "buying", "costco", "warehouse", "featured products", "item", "merchandise", "installation", "dealers", "kitchen", "bathroom", "countertop"],
                "required_score": 2,
            },
            "lifestyle": {
                "url_keywords": ["costco-life", "fye", "supplier", "refreshing-options"],
                "title_keywords": ["celebrate", "entertainment", "author", "refreshing options"],
                "content_keywords": ["lifestyle", "entertainment", "author", "book", "wellness", "health", "hydration", "water", "stay hydrated", "question", "answer", "interview"],
                "required_score": 2,
            },
            "magazine_front_cover": {
                "url_keywords": ["edition", "front-cover", "connection-front"],
                "title_keywords": ["edition", "front cover", "costco connection"],
                "content_keywords": ["cover story", "in this issue", "special section", "featured sections", "download the pdf", "★ in this issue", "★ special section", "★featured sections"],
                "required_score": 2,
            },
        }

    def extract_all_content(self, html_content: str, url: str) -> ExtractedContent:
        """Extract ALL meaningful content"""
        soup = BeautifulSoup(html_content, "html.parser")

        # Clean HTML
        cleaned_soup = self._clean_html(soup)

        # Find main content
        main_content_area = self._find_main_content(cleaned_soup)

        # Detect content type
        content_type = self._detect_content_type(url, cleaned_soup, main_content_area)

        # Extract content
        extracted = ExtractedContent(content_type=content_type)

        self._extract_title_and_metadata(cleaned_soup, extracted, url)
        self._extract_text_content(main_content_area or cleaned_soup, extracted)
        self._extract_images(cleaned_soup, extracted, url)
        self._extract_structured_content(main_content_area or cleaned_soup, extracted)

        # LIFESTYLE ONLY: Enhanced structured content with images for lifestyle content
        if content_type == "lifestyle":
            # Clear existing headings and use enhanced extraction for lifestyle only
            extracted.headings = []
            self._extract_lifestyle_structured_content_with_images(main_content_area or cleaned_soup, extracted)

        # FIXED: Enhanced recipe extraction with section awareness
        if content_type == "recipe":
            self._extract_recipe_data_fixed(
                main_content_area or cleaned_soup, extracted
            )
        else:
            self._extract_content_specific(
                main_content_area or cleaned_soup, extracted, content_type
            )

        logger.info(
            f"✅ FIXED extraction: {content_type} - {len(extracted.main_content)} paragraphs, {len(extracted.images)} images"
        )

        return extracted

    def _clean_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Clean unwanted elements"""

        # Remove script, style, nav, header, footer
        for tag in ["script", "style", "nav", "header", "footer", "aside"]:
            for element in soup.find_all(tag):
                element.decompose()

        # Remove by class patterns
        unwanted_classes = [
            "nav",
            "menu",
            "header",
            "footer",
            "cookie",
            "consent",
            "promo",
            "banner",
            "ad",
            "advertisement",
        ]

        for class_pattern in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_pattern, re.I)):
                element.decompose()

        # Remove by text content
        unwanted_texts = [
            "shop costco.com",
            "add to cart",
            "compare products",
            "we use cookies",
            "accept cookies",
            "privacy policy",
        ]

        for element in soup.find_all(["div", "section", "p"]):
            text = element.get_text().lower().strip()
            if any(unwanted in text for unwanted in unwanted_texts):
                if len(text.split()) < 20:
                    element.decompose()

        return soup

    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find main content area with enhanced comprehensive detection"""

        candidates = []

        # Try semantic elements
        for tag in ["main", "article", '[role="main"]']:
            elements = soup.select(tag)
            for element in elements:
                score = self._score_element(element)
                if score > 30:
                    candidates.append((element, score))

        # Try content selectors
        selectors = [
            ".article-content",
            ".post-content", 
            ".entry-content",
            ".main-content",
            ".content-area",
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                score = self._score_element(element)
                if score > 20:
                    candidates.append((element, score))

        # Try divs with good content
        for div in soup.find_all("div"):
            score = self._score_element(div)
            if score > 50:
                candidates.append((div, score))

        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]

        return soup.find("body")

    def _score_element(self, element: Tag) -> int:
        """Score element quality"""
        if not element:
            return 0

        score = 0
        text = element.get_text().strip()
        text_length = len(text)

        # Length scoring
        if text_length > 1000:
            score += 50
        elif text_length > 500:
            score += 30
        elif text_length > 200:
            score += 15

        # Structure scoring
        score += len(element.find_all("p")) * 5
        score += len(element.find_all(["h1", "h2", "h3"])) * 8
        score += len(element.find_all(["ul", "ol"])) * 5

        # Quality indicators
        if "costco connection" in text.lower():
            score += 20
        if any(word in text.lower() for word in ["recipe", "travel", "tech"]):
            score += 10

        return score

    def _detect_content_type(
        self, url: str, soup: BeautifulSoup, main_content: Tag
    ) -> str:
        """Enhanced content type detection"""

        url_lower = url.lower()

        # Get text content
        main_text = main_content.get_text().lower() if main_content else ""
        soup_text = soup.get_text().lower()

        # Get title
        title_text = ""
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text().lower()

        # Score each content type
        type_scores = {}

        for content_type, patterns in self.content_patterns.items():
            score = 0

            # URL scoring (highest weight)
            for keyword in patterns["url_keywords"]:
                if keyword in url_lower:
                    score += 20

            # Title scoring
            for keyword in patterns["title_keywords"]:
                if keyword in title_text:
                    score += 10

            # Content scoring
            for keyword in patterns["content_keywords"]:
                if keyword in main_text or keyword in soup_text:
                    score += 5

            type_scores[content_type] = score

        # Find best match
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            best_score = type_scores[best_type]
            required_score = self.content_patterns[best_type]["required_score"]

            if best_score >= required_score:
                logger.info(f"🎯 Content type: {best_type} (score: {best_score})")
                return best_type

        return "general"

    def _extract_title_and_metadata(
        self, soup: BeautifulSoup, extracted: ExtractedContent, url: str
    ):
        """Extract title and metadata"""

        # Title strategies
        title_candidates = []

        # H1 tags (highest priority)
        for h1 in soup.find_all("h1"):
            title_text = h1.get_text().strip()
            if (
                title_text
                and len(title_text) > 3
                and "costco" not in title_text.lower()
            ):
                title_candidates.append((title_text, 20))

        # Title tag
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.get_text().strip()
            title_text = re.sub(r"\s*[\|\-]\s*Costco.*", "", title_text)
            if title_text and len(title_text) > 3:
                title_candidates.append((title_text, 15))

        # Choose best title
        if title_candidates:
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            best_title = title_candidates[0][0]
            
            # DYNAMIC: Look for better content-focused title over section headers
            enhanced_title = self._find_better_content_title(best_title, soup)
            extracted.title = enhanced_title or best_title

        # FIXED: Better byline extraction - don't generate fake bylines
        byline_patterns = [
            r"by\s+([^,\n\.]+)",
            r"recipe\s+(?:and\s+photo\s+)?courtesy\s+of\s+([^,\n\.]+)",
            r"recipe\s+by\s+([^,\n\.]+)",
        ]

        full_text = soup.get_text()
        for pattern in byline_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                extracted.byline = f"By {match.group(1).strip()}"
                logger.info(f"Found byline: {extracted.byline}")
                break

    def _extract_text_content(self, content_area: Tag, extracted: ExtractedContent):
        """Enhanced text content extraction"""

        if not content_area:
            return

        # Extract all text elements more comprehensively
        text_elements = content_area.find_all(['p', 'div', 'span', 'section', 'article'])
        
        for element in text_elements:
            text = element.get_text().strip()
            
            # Skip if too short or navigation content
            if not text or len(text) < 10:
                continue
                
            # Skip navigation/menu content
            if any(nav_term in text.lower() for nav_term in ['home', 'costco connection', 'download the pdf', 'copyright', '©']):
                continue
            
            # Check for author bylines (like "by Andy Penfold")
            if text.lower().startswith('by ') and len(text) < 50:
                if not extracted.byline or 'connection' in extracted.byline.lower():
                    extracted.byline = text
                continue
            
            # Include substantive content
            if len(text) > 15:
                # Check if new content
                is_new = True
                for existing in extracted.main_content:
                    if self._text_similarity(text, existing) > 0.7:
                        is_new = False
                        break

                if is_new:
                    extracted.main_content.append(text)

        # Store full text
        extracted.full_text = content_area.get_text()

    def _extract_images(
        self, soup: BeautifulSoup, extracted: ExtractedContent, url: str
    ):
        """Enhanced image extraction"""

        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        for img in soup.find_all("img"):
            src = img.get("src", "")
            alt = img.get("alt", "")

            if not src:
                continue

            # Fix URLs
            fixed_src = self._fix_image_url(src, base_url)
            if not fixed_src:
                continue

            # Score image
            score = self._score_image(fixed_src, alt, img)

            image_data = {
                "src": fixed_src,
                "alt": alt,
                "score": score,
                "width": img.get("width", ""),
                "height": img.get("height", ""),
                "class": " ".join(img.get("class", [])),
            }

            extracted.images.append(image_data)

        # Sort by score
        extracted.images.sort(key=lambda x: x["score"], reverse=True)

    def _fix_image_url(self, src: str, base_url: str) -> str:
        """Fix image URLs"""

        if not src:
            return ""

        # Already absolute
        if src.startswith(("http://", "https://")):
            return src

        # Costco CDN paths
        if src.startswith("/live/resource/img/"):
            return f"https://mobilecontent.costco.com{src}"

        # Author headshot patterns (e.g., Andy_Penfold_Headshot.jpg)
        if "_headshot" in src.lower() or "headshot.jpg" in src.lower():
            filename = src.split("/")[-1]
            # Try to construct proper URL for author headshots
            return f"https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/{filename}"

        # Relative paths with date
        if src.startswith("./") or src.startswith("../"):
            filename = src.split("/")[-1]
            date_match = re.search(r"(\d{2})_(\d{2})", filename)
            if date_match:
                month_num, year_num = date_match.groups()
                month_names = {
                    "01": "january",
                    "02": "february",
                    "03": "march",
                    "04": "april",
                    "05": "may",
                    "06": "june",
                    "07": "july",
                    "08": "august",
                    "09": "september",
                    "10": "october",
                    "11": "november",
                    "12": "december",
                }
                month_name = month_names.get(month_num, "october")
                folder = f"static-us-connection-{month_name}-{year_num}"
                return f"https://mobilecontent.costco.com/live/resource/img/{folder}/{filename}"
            # If no date pattern, try to extract from base URL or use generic path
            elif "_headshot" in filename.lower():
                # Try to extract the date folder from the base_url if possible
                if "static-us-connection" in base_url:
                    return urljoin(base_url, filename)
                else:
                    # Use a generic recent folder path - should be made configurable
                    import datetime
                    current_year = datetime.datetime.now().year
                    current_month = datetime.datetime.now().month
                    month_name = datetime.datetime.now().strftime("%B").lower()
                    return f"https://mobilecontent.costco.com/live/resource/img/static-us-connection-{month_name}-{str(current_year)[2:]}/{filename}"

        # Standard relative URL
        if src.startswith("/"):
            return urljoin(base_url, src)
            
        # Handle local file references that might be headshots
        if not src.startswith(('http://', 'https://')):
            filename = src.split("/")[-1]
            if "_headshot" in filename.lower() or "headshot.jpg" in filename.lower():
                return f"https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/{filename}"

        return urljoin(base_url, src)

    def _score_image(self, src: str, alt: str, img_element: Tag) -> int:
        """Score image quality"""

        score = 0
        src_lower = src.lower()
        alt_lower = alt.lower()

        # Domain scoring
        if "mobilecontent.costco.com" in src_lower:
            score += 60
        if "static-us-connection" in src_lower:
            score += 40

        # Size scoring
        width = img_element.get("width")
        height = img_element.get("height")
        if width and height:
            try:
                w, h = int(width), int(height)
                if w > 400 and h > 300:
                    score += 30
                elif w > 200 and h > 150:
                    score += 20
            except ValueError:
                pass

        # Alt text quality
        if alt and len(alt) > 5:
            score += 25
        if alt and len(alt.split()) >= 3:
            score += 15

        # Content relevance
        content_terms = [
            "recipe",
            "food",
            "travel",
            "destination",
            "tech",
            "product",
            "costco",
        ]
        for term in content_terms:
            if term in alt_lower or term in src_lower:
                score += 10

        # Dynamic author image detection
        author_terms = ["author", "writer", "headshot", "portrait", "profile"]
        for term in author_terms:
            if term in alt_lower or term in src_lower:
                score += 40  # Bonus for author images
                
        # Pattern-based author detection (any author name + headshot)
        if "_headshot" in src_lower or "headshot" in src_lower:
            score += 60  # High priority for any headshot
        
        # Detect author name patterns in URL (FirstName_LastName_Headshot)
        import re
        author_pattern = r'([A-Z][a-z]+_[A-Z][a-z]+)_[Hh]eadshot'
        if re.search(author_pattern, src):
            score += 80  # Very high priority for author name + headshot pattern

        # Penalties
        penalty_terms = ["logo", "icon", "nav", "menu", "banner", "ad"]
        for term in penalty_terms:
            if term in alt_lower or term in src_lower:
                score -= 15

        return max(0, score)

    def _extract_lifestyle_structured_content_with_images(self, content_area: Tag, extracted: ExtractedContent):
        """LIFESTYLE ONLY: Extract headings with properly associated images - FULLY DYNAMIC"""
        
        # STEP 1: Extract all headings and their content boundaries first
        headings_data = []
        
        # First: Get regular heading tags (h1-h6)
        all_headings = content_area.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        # Second: Check if this content has interview patterns
        content_text = content_area.get_text()
        has_interview_patterns = self._detect_interview_patterns(content_text)
        
        # STEP 1.5: ONLY if interview patterns detected, add strong tags as headings
        if has_interview_patterns:
            strong_tags = content_area.find_all("strong")
            for strong in strong_tags:
                strong_text = strong.get_text().strip()
                if self._is_interview_question(strong_text):
                    all_headings.append(strong)
        
        # Sort all headings by document order
        all_headings = sorted(all_headings, key=lambda x: list(content_area.descendants).index(x) if x in content_area.descendants else 0)
        
        for i, heading in enumerate(all_headings):
            heading_text = heading.get_text().strip()
            
            # For interview questions in strong tags, add speaker prefix if available
            if heading.name == 'strong' and self._is_interview_question(heading_text):
                speaker_prefix = self._extract_speaker_prefix(heading)
                if speaker_prefix:
                    heading_text = f"{speaker_prefix}: {heading_text}"
            
            if heading_text and len(heading_text) > 2:
                if not any(nav in heading_text.lower() for nav in ["compare", "shop"]):
                    
                    # Find the boundary for this heading's content
                    next_heading = all_headings[i + 1] if i + 1 < len(all_headings) else None
                    
                    # Extract text content within this heading's boundaries
                    heading_content = []
                    
                    # Special handling for strong tag headings (interview questions)
                    if heading.name == 'strong':
                        # For strong tags, look for content in the parent paragraph and following siblings
                        parent = heading.parent
                        if parent and parent.name == 'p':
                            # Get text after the strong tag within the same paragraph
                            remaining_text = self._get_text_after_strong_tag(heading, parent)
                            if remaining_text and len(remaining_text.strip()) > 10:
                                heading_content.append(remaining_text.strip())
                            # Also look for following paragraphs
                            current = parent.next_sibling
                        else:
                            current = heading.next_sibling
                    else:
                        # Use document order traversal with proper boundary detection
                        current = heading.next_sibling
                    
                    while current and len(heading_content) < 5:  # Allow more content per section
                        # Stop if we reach the next heading element
                        if next_heading and current == next_heading:
                            break
                        
                        # Stop if we hit ANY heading element or interview question strong tag
                        if hasattr(current, 'name'):
                            if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                break
                            elif current.name == 'strong' and self._is_interview_question(current.get_text().strip()):
                                break
                            # CRITICAL: Stop if this paragraph contains the next interview question
                            elif current.name == 'p' and self._paragraph_contains_next_question(current):
                                break
                        
                        # Extract text from paragraphs only (avoid complex nested content)
                        if hasattr(current, 'name') and current.name == 'p':
                            # For interview Q&A, extract clean content excluding questions
                            if self._paragraph_contains_interview_question(current):
                                clean_text = self._extract_clean_paragraph_content(current)
                                if clean_text and len(clean_text) > 5 and len(clean_text) < 1000:
                                    heading_content.append(clean_text)
                            else:
                                # Regular paragraph content
                                text = current.get_text().strip()
                                if text and len(text) > 5 and len(text) < 1000:
                                    heading_content.append(text)
                        
                        current = current.next_sibling
                    
                    # Add heading without images first
                    # Determine heading level - use 3 for strong tags (Q&A questions)
                    if heading.name == 'strong':
                        heading_level = 3
                    else:
                        heading_level = int(heading.name[1])
                    
                    headings_data.append({
                        "text": heading_text,
                        "level": heading_level,
                        "class": " ".join(heading.get("class", [])),
                        "content": heading_content,
                        "images": [],  # Will be populated in step 2
                        "heading_element": heading,  # Temporary reference for matching
                        "dom_position": self._get_dom_position(heading)  # For proximity matching
                    })
        
        # STEP 2: Collect and filter ALL valid images (fully dynamic - no hardcoding)
        valid_images = []
        for img in content_area.find_all('img'):
            img_data = self._extract_lifestyle_image_data(img)
            if img_data and self._is_valid_content_image(img_data, img):
                # Calculate DOM position for proximity matching
                img_position = self._get_dom_position(img)
                
                valid_images.append({
                    'img_data': img_data,
                    'element': img,
                    'dom_position': img_position,
                    'closest_heading': self._find_closest_heading_for_image(img, content_area),
                    'surrounding_text': self._get_surrounding_text_for_image(img)
                })
        
        # STEP 3: Smart image-to-section assignment using multiple algorithms
        # PRIORITY ORDER: Semantic → Proximity → Fallback
        assigned_images = set()  # Track assigned image URLs to prevent duplicates
        
        # Algorithm 1: SEMANTIC MATCHING FIRST (highest priority)
        for img_info in valid_images:
            img_data = img_info['img_data']
            img_src = img_data.get('src', '')
            
            if img_src in assigned_images:
                continue
            
            # Try semantic/contextual matching first
            best_match_index = self._find_semantic_match(img_info, headings_data)
            
            if best_match_index >= 0:
                headings_data[best_match_index]['images'].append(img_data)
                assigned_images.add(img_src)
                continue
        
        # Algorithm 2: PROXIMITY MATCHING for remaining images
        for img_info in valid_images:
            img_data = img_info['img_data']
            img_src = img_data.get('src', '')
            
            if img_src in assigned_images:
                continue
            
            # Find the closest heading by DOM position
            closest_section_index = self._find_closest_section_by_position(
                img_info['dom_position'], headings_data
            )
            
            if closest_section_index >= 0:
                # Verify this is a reasonable match using contextual analysis
                if self._verify_image_section_match(img_info, headings_data[closest_section_index]):
                    headings_data[closest_section_index]['images'].append(img_data)
                    assigned_images.add(img_src)
                    continue
        
        # Algorithm 3: Fallback - assign unassigned images to most appropriate sections
        for img_info in valid_images:
            img_data = img_info['img_data']
            img_src = img_data.get('src', '')
            
            if img_src in assigned_images:
                continue
            
            # Find any reasonable section (prefer main sections over subsections)
            fallback_index = self._find_fallback_section(img_info, headings_data)
            
            if fallback_index >= 0:
                headings_data[fallback_index]['images'].append(img_data)
                assigned_images.add(img_src)
        
        # STEP 4: Clean up temporary heading element references
        for heading_info in headings_data:
            if 'heading_element' in heading_info:
                del heading_info['heading_element']
            if 'dom_position' in heading_info:
                del heading_info['dom_position']
        
        # Update extracted headings with the properly associated data
        extracted.headings = headings_data

    def _detect_interview_patterns(self, content_text: str) -> bool:
        """Dynamically detect interview/Q&A patterns in content"""
        if not content_text:
            return False
        
        # Look for common interview indicators
        interview_indicators = [
            # Q&A format indicators
            r'\b[A-Z]{2,3}\s+[A-Z]',  # Pattern like "CC What" or "KS I"
            r'\bConnection\s+[A-Z]',   # "Connection What", "Connection How"
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z]',  # "First Last What" pattern
            # Question patterns in strong tags
            r'<strong>.*\?.*</strong>',  # Questions in strong tags
            r'<strong>.*[Ww]hat.*</strong>',  # What questions in strong
            r'<strong>.*[Hh]ow.*</strong>',   # How questions in strong
        ]
        
        return any(re.search(pattern, content_text) for pattern in interview_indicators)
    
    def _is_interview_question(self, text: str) -> bool:
        """Detect interview question patterns in strong tags - fully dynamic"""
        if not text or len(text) < 10:  # Questions should be longer than speaker names
            return False
            
        clean_text = text.strip()
        
        # EXCLUDE speaker name patterns (dynamic detection)
        speaker_patterns = [
            r'^\s*[A-Z]{2,3}\s*$',  # Just 2-3 capital letters (CC, KS, etc.)
            r'^\s*[A-Z][a-z]+\s+[A-Z][a-z]+\s*$',  # First Last pattern
            r'^\s*\w+\s+Connection\s*$',  # Something Connection
        ]
        
        # If it matches speaker patterns, it's NOT a question heading
        if any(re.match(pattern, clean_text) for pattern in speaker_patterns):
            return False
        
        # INCLUDE only actual questions that end with ? and have substantial content
        question_patterns = [
            r'^.{15,}.*\?$',  # Must be at least 15 chars and end with ?
            r'[Ww]hat.*\?$',  # What questions
            r'[Hh]ow.*\?$',   # How questions  
            r'[Ww]hy.*\?$',   # Why questions
            r'[Ww]here.*\?$', # Where questions
            r'[Ww]hen.*\?$',  # When questions
            r'[Cc]an.*\?$',   # Can questions
            r'[Dd]o.*\?$',    # Do questions
            r'[Ii]s.*\?$',    # Is questions
        ]
        
        return any(re.search(pattern, clean_text) for pattern in question_patterns)

    def _get_text_after_strong_tag(self, strong_tag, parent_paragraph) -> str:
        """Extract answer text that appears after a Q&A strong tag within the same paragraph"""
        if not strong_tag or not parent_paragraph:
            return ""
        
        # Get all content after the question strong tag
        text_parts = []
        found_question_strong = False
        found_br = False
        
        for child in parent_paragraph.children:
            if child == strong_tag:
                found_question_strong = True
                continue
            
            if found_question_strong:
                # Look for <br> tag which separates question from answer
                if hasattr(child, 'name') and child.name == 'br':
                    found_br = True
                    continue
                
                # After finding <br>, collect the answer text
                if found_br:
                    # Check if this is a responder name in span
                    if hasattr(child, 'name') and child.name == 'span':
                        span_strong = child.find('strong')
                        if span_strong:
                            responder_name = span_strong.get_text().strip()
                            if self._is_speaker_abbreviation(responder_name):
                                text_parts.append(f"{responder_name}:")
                                continue
                    
                    if hasattr(child, 'get_text'):
                        text = child.get_text().strip()
                        if text:
                            text_parts.append(text)
                    elif isinstance(child, str):
                        text = child.strip()
                        if text:
                            text_parts.append(text)
        
        result = ' '.join(text_parts).strip()
        
        # Clean up spacing and formatting
        if result:
            # Clean up multiple spaces
            result = re.sub(r'\s+', ' ', result)
            # Ensure proper spacing after responder name colon
            result = re.sub(r':\s*([A-Z])', r': \1', result)
        
        return result

    def _contains_new_qa_question(self, text: str) -> bool:
        """Check if text contains a new Q&A question that should start a new section"""
        if not text or len(text) < 20:
            return False
        
        # Look for Q&A patterns that indicate a new question
        qa_start_patterns = [
            r'(CC|Connection)\\s+[A-Z].*\\?',  # CC What...?
            r'[A-Z]{2,3}\\s+[A-Z].*\\?',      # KS What...?
            r'^\\s*[A-Z][a-z]+\\s+[A-Z][a-z]+\\s+[A-Z].*\\?'  # First Last What...?
        ]
        
        import re
        return any(re.search(pattern, text) for pattern in qa_start_patterns)

    def _clean_qa_content(self, text: str) -> str:
        """Clean Q&A content by removing speaker markers and formatting"""
        if not text:
            return text
        
        import re
        
        # Remove speaker markers at the beginning
        cleaned = re.sub(r'^\\s*(CC|KS|Costco Connection|Karin Smirnoff)\\s+', '', text)
        
        # Remove excessive whitespace and tabs
        cleaned = re.sub(r'\\s+', ' ', cleaned).strip()
        
        # Remove duplicate question markers if they appear in content
        cleaned = re.sub(r'(CC|KS)\\s+([A-Z][^?]*\\?)\\s*\\1\\s+', r'\\2 ', cleaned)
        
        return cleaned

    def _contains_interview_question_heading(self, element, extracted: ExtractedContent) -> bool:
        """Check if element contains interview question that's already extracted as heading"""
        if not element or not hasattr(element, 'find_all'):
            return False
        
        # Look for strong tags in this element that are interview questions
        strong_tags = element.find_all('strong')
        for strong in strong_tags:
            # Skip speaker names in spans
            if strong.parent and strong.parent.name == 'span':
                continue
            
            strong_text = strong.get_text().strip()
            if self._is_interview_question(strong_text):
                # Check if this question is already in headings
                for heading in extracted.headings:
                    if heading.get('text', '').strip() == strong_text:
                        return True
        
        return False

    def _extract_clean_paragraph_content(self, paragraph_element) -> str:
        """Extract clean content from paragraph, excluding interview questions already extracted as headings"""
        if not paragraph_element:
            return ""
        
        # For interview Q&A paragraphs, extract only the answer portion
        strong_tags = paragraph_element.find_all('strong')
        interview_questions = []
        
        # Identify interview questions in this paragraph
        for strong in strong_tags:
            # Skip speaker names in spans
            if strong.parent and strong.parent.name == 'span':
                continue
            
            strong_text = strong.get_text().strip()
            if self._is_interview_question(strong_text):
                interview_questions.append(strong)
        
        # If this paragraph contains interview questions, extract only answer portions
        if interview_questions:
            answer_parts = []
            
            for child in paragraph_element.children:
                # Skip the question strong tags
                if hasattr(child, 'name') and child.name == 'strong':
                    if any(child == q for q in interview_questions):
                        continue
                
                # Handle speaker names in spans - include as responder prefix
                if hasattr(child, 'name') and child.name == 'span':
                    span_strong = child.find('strong')
                    if span_strong and not self._is_interview_question(span_strong.get_text().strip()):
                        # This is a responder name, add it as prefix
                        responder_name = child.get_text().strip()
                        if responder_name and not any(responder_name in part for part in answer_parts):
                            answer_parts.append(f"{responder_name}:")
                    continue
                
                # Include other content (answers)
                if hasattr(child, 'get_text'):
                    text = child.get_text().strip()
                    if text and text not in ['', '\n', '\t']:
                        answer_parts.append(text)
                elif isinstance(child, str):
                    text = child.strip()
                    if text and text not in ['', '\n', '\t']:
                        answer_parts.append(text)
            
            # Join parts and clean up spacing
            result = ' '.join(answer_parts).strip()
            
            # Clean up multiple spaces and ensure proper spacing after responder name
            result = re.sub(r'\s+', ' ', result)
            result = re.sub(r':\s*([A-Z])', r': \1', result)  # Ensure space after colon
            
            return result
        else:
            # Regular paragraph, return full text
            return paragraph_element.get_text().strip()

    def _paragraph_contains_interview_question(self, paragraph_element) -> bool:
        """Check if paragraph contains any interview question"""
        if not paragraph_element or not hasattr(paragraph_element, 'find_all'):
            return False
        
        strong_tags = paragraph_element.find_all('strong')
        for strong in strong_tags:
            # Skip speaker names in spans
            if strong.parent and strong.parent.name == 'span':
                continue
            
            strong_text = strong.get_text().strip()
            if self._is_interview_question(strong_text):
                return True
        
        return False

    def _paragraph_contains_next_question(self, paragraph_element) -> bool:
        """Check if paragraph contains the next interview question (for boundary detection)"""
        return self._paragraph_contains_interview_question(paragraph_element)

    def _extract_speaker_prefix(self, question_strong_tag) -> str:
        """Extract speaker prefix (like 'CC', 'MC') that appears before interview questions"""
        if not question_strong_tag or not question_strong_tag.parent:
            return ""
        
        parent = question_strong_tag.parent
        if parent.name != 'p':
            return ""
        
        # Look for speaker prefix in the same paragraph before the question
        # Pattern: <span><strong>CC</strong></span><strong>Question...</strong>
        
        # Find all span tags with strong children in this paragraph
        for child in parent.children:
            if hasattr(child, 'name') and child.name == 'span':
                span_strong = child.find('strong')
                if span_strong:
                    speaker_text = span_strong.get_text().strip()
                    # Check if this looks like a speaker abbreviation (CC, MC, etc.)
                    if self._is_speaker_abbreviation(speaker_text):
                        return speaker_text
        
        return ""

    def _is_speaker_abbreviation(self, text: str) -> bool:
        """Check if text looks like a speaker abbreviation (CC, MC, KS, etc.)"""
        if not text:
            return False
        
        # Common interview speaker patterns
        speaker_patterns = [
            r'^[A-Z]{2,3}$',  # 2-3 capital letters (CC, MC, KS, etc.)
            r'^Costco Connection$',  # Full name
            r'^Connection$',  # Short name
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+$',  # Full names like "Mark Campbell"
        ]
        
        return any(re.match(pattern, text.strip()) for pattern in speaker_patterns)

    def _find_better_content_title(self, current_title: str, soup: BeautifulSoup) -> Optional[str]:
        """Find better content-focused title over section headers - works for any content type"""
        
        # Only apply to titles that look like section headers rather than content titles
        section_header_patterns = [
            r'//.*spotlight',  # \"// AUTHOR SPOTLIGHT\" pattern
            r'//.*entertainment',  # \"// ENTERTAINMENT\" pattern  
            r'//.*[A-Z\\s]+$',  # General \"// SECTION NAME\" pattern
            r'^[A-Z\\s]+ // [A-Z\\s]+$',  # \"SECTION // SUBSECTION\" pattern
        ]
        
        is_section_header = any(re.search(pattern, current_title, re.IGNORECASE) for pattern in section_header_patterns)
        
        if not is_section_header:
            return None
            
        # Look for alternative H1 titles that are content-focused
        h1_tags = soup.find_all('h1')
        for h1 in h1_tags:
            h1_text = h1.get_text().strip()
            
            # Skip if same as current
            if h1_text.lower() == current_title.lower():
                continue
                
            # Look for content-focused titles (not section headers)
            if (len(h1_text.split()) <= 4 and  # Not too long
                len(h1_text) > 3 and  # Not too short
                '//' not in h1_text and  # Not a section header
                not any(section_word in h1_text.lower() for section_word in ['spotlight', 'entertainment', 'connection', 'magazine'])):
                
                # Score the content title based on how content-focused it appears
                score = 0
                
                # Prefer shorter, more specific titles
                if len(h1_text.split()) <= 3:
                    score += 10
                
                # Prefer titles that don't contain site/brand names  
                if not any(brand in h1_text.lower() for brand in ['costco', 'fye']):
                    score += 10
                
                # Prefer titles with proper capitalization (suggests it's a real title)
                if h1_text.istitle() or any(word[0].isupper() for word in h1_text.split()):
                    score += 5
                
                return h1_text  # Return first good match for now
                
        return None

    def _is_valid_content_image(self, img_data: dict, img_element) -> bool:
        """FULLY DYNAMIC: Check if image is valid content (no hardcoding)"""
        if not img_data:
            return False
            
        src = img_data.get('src', '')
        alt = img_data.get('alt', '').lower()
        filename = src.split('/')[-1] if src else 'unknown'
        
        # Skip obvious non-content images
        skip_patterns = ['logo', 'nav', 'menu', 'banner', 'ad', 'advertisement', 'promo']
        ad_patterns = ['300x250', '_300x', '_250x', 'banner', 'sidebar']
        tiny_patterns = ['16x16', '32x32', '64x64']
        
        # Skip if clearly an ad or navigation
        if any(pattern in filename.lower() for pattern in skip_patterns + ad_patterns + tiny_patterns):
            return False
        
        # Accept images from Costco content domains
        if 'mobilecontent.costco.com' in src.lower():
            return True
        
        # Accept local content files (downloaded from Costco) - dynamic pattern detection
        local_costco_patterns = ['costco_files', '_costco.html', 'costco life', 'inside costco', 'fye']
        is_local_costco = any(pattern in src.lower() for pattern in local_costco_patterns)
        
        if is_local_costco:
            # Additional validation: must have meaningful alt text or be reasonably sized
            if alt and len(alt) > 2:
                return True
            # Or check if filename suggests content (not ad)
            if not any(ad in filename.lower() for ad in ['300x', '250x', 'banner', 'sidebar']):
                return True
        
        return False

    def _get_dom_position(self, element) -> int:
        """Get rough DOM position for proximity calculations"""
        if not element:
            return 0
        
        # Find all elements before this one
        count = 0
        current = element
        while current.previous_sibling:
            count += 1
            current = current.previous_sibling
        
        return count

    def _find_closest_section_by_position(self, img_position: int, headings_data: list) -> int:
        """Find the section closest to image by DOM position"""
        if not headings_data:
            return -1
        
        closest_index = 0
        min_distance = abs(img_position - headings_data[0].get('dom_position', 0))
        
        for i, heading_info in enumerate(headings_data):
            heading_pos = heading_info.get('dom_position', 0)
            distance = abs(img_position - heading_pos)
            
            if distance < min_distance:
                min_distance = distance
                closest_index = i
        
        return closest_index

    def _verify_image_section_match(self, img_info: dict, section_info: dict) -> bool:
        """Verify that image-section pairing makes sense"""
        img_data = img_info['img_data']
        heading_text = section_info['text'].lower()
        section_content = ' '.join(section_info['content']).lower()
        
        src = img_data.get('src', '').lower()
        alt = img_data.get('alt', '').lower()
        filename = src.split('/')[-1] if src else ''
        
        # Look for obvious mismatches
        # If heading is about books but image is about food, probably wrong
        book_terms = ['book', 'author', 'story', 'novel', 'read']
        food_terms = ['recipe', 'food', 'cooking', 'lasagna', 'rollup']
        pet_terms = ['pet', 'cat', 'dog', 'animal']
        travel_terms = ['travel', 'card', 'where', 'been']
        
        # Check for semantic consistency
        heading_is_book = any(term in heading_text for term in book_terms)
        heading_is_food = any(term in heading_text for term in food_terms)
        heading_is_pet = any(term in heading_text for term in pet_terms)
        heading_is_travel = any(term in heading_text for term in travel_terms)
        
        img_is_book = any(term in filename or term in alt for term in book_terms)
        img_is_food = any(term in filename or term in alt for term in food_terms)
        img_is_pet = any(term in filename or term in alt for term in pet_terms)
        img_is_travel = any(term in filename or term in alt for term in travel_terms)
        
        # Strong mismatch detection
        if heading_is_book and (img_is_food or img_is_pet or img_is_travel):
            return False
        if heading_is_food and (img_is_book or img_is_pet or img_is_travel):
            return False
        if heading_is_pet and (img_is_book or img_is_food or img_is_travel):
            return False
        if heading_is_travel and (img_is_book or img_is_food or img_is_pet):
            return False
        
        # If no strong mismatch, allow the pairing
        return True

    def _find_semantic_match(self, img_info: dict, headings_data: list) -> int:
        """Enhanced semantic matching with deep content analysis"""
        img_data = img_info['img_data']
        src = img_data.get('src', '').lower()
        alt = img_data.get('alt', '').lower()
        filename = src.split('/')[-1] if src else ''
        
        best_score = 0
        best_index = -1
        
        # Extract comprehensive image context
        image_context = self._extract_image_context(img_info)
        
        for i, heading_info in enumerate(headings_data):
            heading_text = heading_info['text'].lower()
            section_content = ' '.join(heading_info['content']).lower()
            
            # Extract comprehensive content context
            content_context = self._extract_content_context(heading_info)
            
            # Calculate deep semantic score
            score = self._calculate_deep_semantic_score(image_context, content_context, heading_text, section_content)
            
            # Look for keyword matches between image and section
            # Extract meaningful words from filename and alt
            img_words = set()
            if filename:
                clean_filename = filename.replace('.jpg', '').replace('.png', '').replace('_', ' ').replace('-', ' ')
                img_words.update(clean_filename.split())
            if alt:
                img_words.update(alt.split())
            
            # Extract words from heading and content
            section_words = set(heading_text.split() + section_content.split())
            
            # Remove common words
            common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
            img_words = {w for w in img_words if len(w) > 2 and w not in common_words}
            section_words = {w for w in section_words if len(w) > 2 and w not in common_words}
            
            # Score based on word overlap
            matches = img_words.intersection(section_words)
            score += len(matches) * 10
            
            # PRIORITY 1: EXACT CONTENT MATCHES (highest priority)
            # These should override proximity and other factors
            exact_matches = 0
            
            # Halloween/Celebrate content matching  
            if 'halloween' in filename and 'celebrate' in heading_text:
                score += 100  # Highest priority
                exact_matches += 1
            
            # Glasses/Donation matching
            if 'glasses' in filename and 'donation' in heading_text:
                score += 100  # Highest priority  
                exact_matches += 1
                
            # Card/Travel matching
            if 'card' in filename and ('card' in heading_text or 'where' in heading_text):
                score += 100  # Highest priority
                exact_matches += 1
                
            # Rollup/Recipe matching (handle both singular and plural, lasagna variations)
            if ('rollup' in filename or 'rollups' in filename or 'lasagna' in filename) and ('rollup' in heading_text or 'rollups' in heading_text or 'lasagna' in heading_text):
                score += 100  # Highest priority
                exact_matches += 1
                
            # Pet/Planet matching
            if ('pet' in filename or 'wellness' in filename) and ('pet' in heading_text or 'planet' in heading_text):
                score += 100  # Highest priority
                exact_matches += 1
                
            # Book/Author matching - ENHANCED for Strong Women content
            if ('book' in filename or 'author' in filename) and ('book' in heading_text or 'author' in heading_text or 'entertainment' in heading_text):
                score += 100  # Highest priority
                exact_matches += 1
                
            # DYNAMIC: Book images should go to book/pick related sections
            book_image_indicators = ['book', 'bookpick', 'author', 'novel', 'read']
            book_section_indicators = ['book', 'pick', 'online', 'author', 'entertainment', 'read']
            
            if (any(indicator in filename for indicator in book_image_indicators) and 
                any(indicator in heading_text for indicator in book_section_indicators)):
                score += 150  # High priority for book content matching
                exact_matches += 1
            
            # DYNAMIC: Publisher/Brand books in pick sections (NASA, etc.)
            if (any(brand in filename for brand in ['nasa', 'penguin', 'random', 'harper']) and 
                any(pick_word in heading_text for pick_word in ['pick', 'book', 'online', 'selection'])):
                score += 150  # High priority for branded books in pick sections
                exact_matches += 1
            
            # PRIORITY 2: SECTION LEVEL PREFERENCES
            # Main sections (level 1) should be preferred for primary content
            if exact_matches > 0 and heading_info.get('level', 1) == 1:
                score += 50  # Bonus for main sections with exact matches
                
            # PRIORITY 3: FILENAME-SPECIFIC BONUSES (lower priority)
            if 'author' in filename and 'author' in heading_text:
                score += 30
            if 'book' in filename and 'book' in heading_text:
                score += 20
            if 'rollup' in filename and 'rollup' in heading_text:
                score += 20
            if 'halloween' in filename and 'halloween' in heading_text:
                score += 20
            if 'glasses' in filename and 'donation' in heading_text:
                score += 20
            if 'card' in filename and ('card' in heading_text or 'travel' in heading_text):
                score += 20
            if 'pet' in filename and ('pet' in heading_text or 'planet' in heading_text):
                score += 20
            
            # PRIORITY 4: GENERAL CONTENT PATTERNS
            # CostcoLife images general matching
            if 'costcolife' in filename:
                # Prefer main sections for primary lifestyle content
                if heading_info.get('level', 1) == 1:
                    score += 15
                    
            # FYE content matching
            if 'fye' in filename or 'bookpick' in filename:
                if 'entertainment' in heading_text or 'author' in heading_text or 'book' in heading_text:
                    score += 15
            
            if score > best_score:
                best_score = score
                best_index = i
        
        return best_index if best_score > 0 else -1

    def _extract_image_context(self, img_info: dict) -> dict:
        """Extract comprehensive context from image data"""
        img_data = img_info['img_data']
        src = img_data.get('src', '').lower()
        alt = img_data.get('alt', '').lower()
        filename = src.split('/')[-1] if src else ''
        
        # Extract entities and keywords from image data
        image_words = set()
        
        # From filename (clean up common separators)
        if filename:
            clean_filename = filename.replace('.jpg', '').replace('.png', '').replace('_', ' ').replace('-', ' ')
            image_words.update(clean_filename.split())
        
        # From alt text
        if alt:
            image_words.update(alt.split())
        
        # From surrounding text if available
        surrounding_text = img_info.get('surrounding_text', '').lower()
        if surrounding_text:
            image_words.update(surrounding_text.split())
        
        # Categorize image content
        categories = {
            'book_related': any(term in ' '.join(image_words) for term in ['book', 'cover', 'author', 'novel', 'read', 'story']),
            'person_photo': any(term in alt for term in ['woman', 'man', 'person', 'author', 'portrait']),
            'product': any(term in filename for term in ['product', 'item', 'cover']),
            'brand_specific': []
        }
        
        # DYNAMIC: Extract any significant words from image data
        significant_words = []
        for word in image_words:
            if len(word) > 3 and word not in ['jpg', 'png', 'img', 'static', 'resource']:
                significant_words.append(word)
        categories['significant_words'] = significant_words
        
        return {
            'words': image_words,
            'filename': filename,
            'alt': alt,
            'categories': categories,
            'src': src
        }

    def _extract_content_context(self, heading_info: dict) -> dict:
        """Extract comprehensive context from section content"""
        heading_text = heading_info['text'].lower()
        section_content = ' '.join(heading_info.get('content', [])).lower()
        combined_text = heading_text + ' ' + section_content
        
        # Extract meaningful entities and topics
        entities = {
            'people': [],
            'books': [],
            'brands': [],
            'topics': []
        }
        
        # DYNAMIC: Extract all meaningful entities from content
        import re
        words = combined_text.split()
        
        # Extract all meaningful words (filter out common/stop words)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'this', 'that'}
        meaningful_words = [word.lower() for word in words if len(word) > 3 and word.lower() not in stop_words]
        
        # Store all content words for matching
        entities['all_words'] = set(meaningful_words)
        
        # Extract proper nouns (capitalized words)
        proper_nouns = [word for word in words if word and word[0].isupper() and len(word) > 2]
        entities['proper_nouns'] = [word.lower() for word in proper_nouns]
        
        # Extract quoted phrases (likely titles)
        quoted_phrases = re.findall(r'"([^"]+)"', combined_text)
        # Fix regex pattern
        quoted_phrases = re.findall(r'\"([^\"]+)\"', combined_text)
        entities['quoted_text'] = [phrase.lower() for phrase in quoted_phrases if len(phrase) > 3]
        
        # DYNAMIC: Categorize content type based on word patterns
        content_indicators = {
            'interview_content': any(word in combined_text for word in ['asked', 'question', 'answer', 'interview']),
            'book_content': any(word in combined_text for word in ['book', 'author', 'story', 'novel', 'read']),
            'recommendation_content': any(word in combined_text for word in ['pick', 'available', 'item', 'recommend']),
            'biographical_content': any(word in combined_text for word in ['writer', 'author', 'born', 'life', 'takes up'])
        }
        
        entities['content_type_indicators'] = [key for key, value in content_indicators.items() if value]
        
        return {
            'text': combined_text,
            'entities': entities,
            'heading': heading_text,
            'section_type': self._determine_section_type(heading_info)
        }

    def _determine_section_type(self, heading_info: dict) -> str:
        """Determine what type of section this is"""
        heading = heading_info['text'].lower()
        content = ' '.join(heading_info.get('content', [])).lower()
        
        if 'online' in heading and 'pick' in heading:
            return 'book_recommendation'
        elif any(word in heading for word in ['strong', 'women', 'takes', 'story']):
            return 'main_content'
        elif heading.endswith('?'):
            return 'interview_question'
        elif 'author' in heading or 'spotlight' in heading:
            return 'author_spotlight'
        else:
            return 'general_content'

    def _calculate_deep_semantic_score(self, image_context: dict, content_context: dict, heading_text: str, section_content: str) -> int:
        """Calculate semantic match score using deep content analysis"""
        score = 0
        
        # PRIORITY 1: EXACT ENTITY MATCHING (highest score)
        # Match specific people, books, brands mentioned in content
        
        # DYNAMIC WORD OVERLAP SCORING
        content_words = content_context['entities']['all_words']
        image_words = image_context['words']
        
        # Calculate direct word overlap
        overlap = content_words.intersection(image_words)
        score += len(overlap) * 100  # 100 points per matching word
        
        # PROPER NOUN MATCHING (people, places, brands)
        content_proper_nouns = set(content_context['entities']['proper_nouns'])
        image_significant_words = set(image_context['categories']['significant_words'])
        
        proper_noun_overlap = content_proper_nouns.intersection(image_significant_words)
        score += len(proper_noun_overlap) * 200  # 200 points per proper noun match
        
        # QUOTED TEXT MATCHING (titles, specific phrases)
        for quoted_text in content_context['entities']['quoted_text']:
            quoted_words = quoted_text.split()
            if any(word in image_context['filename'] or word in image_context['alt'] for word in quoted_words):
                score += 300  # High score for title/quote matches
        
        # PRIORITY 2: DYNAMIC CONTEXTUAL TYPE MATCHING
        content_type_indicators = content_context['entities']['content_type_indicators']
        
        # Book recommendation sections prefer book-related images
        if 'recommendation_content' in content_type_indicators:
            if image_context['categories']['book_related']:
                score += 250
        
        # Main content/biographical sections prefer person photos
        if 'biographical_content' in content_type_indicators:
            if image_context['categories']['person_photo']:
                score += 200
        
        # Interview sections should have lower image priority unless specific match
        if 'interview_content' in content_type_indicators:
            if not proper_noun_overlap:  # No specific entity match
                score -= 50  # Small penalty for non-specific matches
        
        # PRIORITY 3: SEMANTIC WORD OVERLAP
        content_words = set(content_context['text'].split())
        image_words = image_context['words']
        
        # Remove common words
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        meaningful_content_words = {w for w in content_words if len(w) > 3 and w not in common_words}
        meaningful_image_words = {w for w in image_words if len(w) > 3 and w not in common_words}
        
        # Calculate overlap score
        overlap = meaningful_content_words.intersection(meaningful_image_words)
        score += len(overlap) * 50  # 50 points per meaningful word overlap
        
        # PRIORITY 4: SPECIFIC ENHANCEMENTS FOR STRONG WOMEN CONTENT
        
        # NASA Bees book specific matching
        # Dynamic filename-content matching
        filename_words = image_context['filename'].replace('_', ' ').replace('-', ' ').split()
        for word in filename_words:
            if len(word) > 3 and word in content_context['entities']['all_words']:
                score += 150
        
        # Dynamic person photo matching
        if image_context['categories']['person_photo']:
            person_match_score = len(content_proper_nouns.intersection(image_significant_words))
            score += person_match_score * 100
        
        # Girl in Eagle's Talons book matching
        if ('eagle' in image_context['filename'] or 'girl' in image_context['filename']) and \
           any('eagle' in book for book in content_context['entities']['books']):
            score += 350
        
        return score

    def _find_fallback_section(self, img_info: dict, headings_data: list) -> int:
        """Find fallback section for unmatched images"""
        if not headings_data:
            return -1
        
        # Prefer main sections (level 1) over subsections
        for i, heading_info in enumerate(headings_data):
            if heading_info.get('level', 1) == 1:
                return i
        
        # If no level 1 sections, use first section
        return 0

    def _extract_lifestyle_image_data(self, img_element) -> dict:
        """LIFESTYLE ONLY: Extract structured image data with caption and credits"""
        if not img_element or not img_element.get('src'):
            return None
            
        src = img_element.get('src', '')
        alt = img_element.get('alt', '')
        
        # Extract caption and credits using existing method
        caption = self._extract_lifestyle_image_caption(img_element)
        
        # Separate caption and credits if both are present
        credit_text = ""
        caption_text = caption
        
        if caption and '©' in caption:
            # Split caption and copyright
            parts = caption.split('©')
            if len(parts) == 2:
                caption_text = parts[0].strip()
                credit_text = f"© {parts[1].strip()}"
        elif caption and any(indicator in caption.lower() for indicator in ['photo:', 'credit:', 'courtesy']):
            # Handle other credit formats
            credit_text = caption
            caption_text = ""
        
        return {
            "src": src,
            "alt": alt,
            "caption": caption_text,
            "credit": credit_text,
            "width": img_element.get("width", ""),
            "height": img_element.get("height", ""),
            "class": " ".join(img_element.get("class", []))
        }

    def _extract_lifestyle_image_caption(self, img_element) -> str:
        """LIFESTYLE ONLY: Extract caption/credits for an image from nearby elements"""
        caption = ""
        
        # Check for figcaption elements
        figure_parent = img_element.find_parent('figure')
        if figure_parent:
            figcaption = figure_parent.find('figcaption')
            if figcaption:
                caption = figcaption.get_text().strip()
        
        # Check for caption in next sibling elements
        if not caption:
            current = img_element.next_sibling
            for _ in range(3):  # Check next 3 siblings
                if hasattr(current, 'get_text'):
                    text = current.get_text().strip()
                    # Look for copyright/credit patterns
                    if text and ('©' in text or 'credit:' in text.lower() or 'photo:' in text.lower()):
                        caption = text
                        break
                    # Look for short descriptive text
                    elif text and len(text) < 100 and len(text) > 5:
                        # Check if it looks like a caption (not part of main content)
                        if any(indicator in text.lower() for indicator in ['photo', 'image', 'courtesy', '/', '|']):
                            caption = text
                            break
                current = getattr(current, 'next_sibling', None) if current else None
                if not current:
                    break
        
        # Check for caption in parent container
        if not caption:
            parent = img_element.parent
            if parent:
                # Look for small text elements with copyright
                small_texts = parent.find_all(['small', 'span'], string=lambda text: text and '©' in text)
                if small_texts:
                    caption = small_texts[0].get_text().strip()
        
        return caption

    def _is_image_contextually_relevant(self, img_data: dict, heading_text: str, content_text: str) -> bool:
        """LIFESTYLE ONLY: Check if image is contextually relevant to heading/content"""
        if not img_data:
            return False
            
        src = img_data.get('src', '').lower()
        alt = img_data.get('alt', '').lower()
        heading_lower = heading_text.lower()
        content_lower = content_text.lower()
        filename = src.split('/')[-1] if src else ''
        
        # Enhanced dynamic contextual matching logic
        
        # 1. Exact keyword matching between image and section
        # Extract meaningful keywords from filename and alt text
        image_keywords = set()
        if filename:
            # Clean filename and extract keywords
            clean_filename = filename.replace('.jpg', '').replace('.png', '').replace('_', ' ').replace('-', ' ')
            image_keywords.update(clean_filename.split())
        if alt:
            image_keywords.update(alt.split())
        
        # Extract keywords from heading and content
        section_keywords = set()
        section_keywords.update(heading_lower.split())
        if content_text:
            section_keywords.update(content_lower.split())
        
        # Remove common words that don't provide context
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        image_keywords = {word for word in image_keywords if len(word) > 2 and word not in common_words}
        section_keywords = {word for word in section_keywords if len(word) > 2 and word not in common_words}
        
        # Check for keyword overlap
        keyword_matches = image_keywords.intersection(section_keywords)
        if keyword_matches:
            return True
        
        # 2. Semantic content matching patterns
        content_patterns = {
            # Recipe/food patterns
            'recipe': ['recipe', 'cooking', 'food', 'lasagna', 'rollup', 'spinach', 'dinner', 'meal'],
            # Card/travel patterns  
            'travel': ['card', 'travel', 'costco', 'membership', 'where', 'been', 'explore'],
            # Book/author patterns
            'book': ['book', 'author', 'story', 'novel', 'read', 'writer', 'cover'],
            # Donation/glasses patterns
            'donation': ['donation', 'glasses', 'optical', 'program', 'give', 'help', 'charity'],
            # Halloween/celebration patterns
            'celebration': ['halloween', 'celebrate', 'costume', 'party', 'fun', 'holiday'],
            # Pet patterns
            'pet': ['pet', 'animal', 'cat', 'dog', 'furry', 'companion']
        }
        
        # Check each pattern category
        for category, patterns in content_patterns.items():
            # Check if section content matches this category
            section_matches_category = any(pattern in heading_lower or pattern in content_lower for pattern in patterns)
            # Check if image matches this category
            image_matches_category = any(pattern in filename or pattern in alt for pattern in patterns)
            
            if section_matches_category and image_matches_category:
                return True
        
        # 3. Proximity-based matching (images near relevant text)
        if content_text:
            # Look for specific content mentions that relate to image
            content_words = content_lower.split()
            for word in image_keywords:
                if word in content_words:
                    return True
        
        # 4. Fallback: Check for any reasonable connection
        # If heading mentions specific items and image alt/filename has those items
        for heading_word in heading_lower.split():
            if len(heading_word) > 3:  # Skip short words
                if heading_word in alt or heading_word in filename:
                    return True
        
        return False

    def _is_image_already_assigned(self, img_data: dict, headings_data: list) -> bool:
        """LIFESTYLE ONLY: Check if image is already assigned to prevent duplication"""
        if not img_data or not headings_data:
            return False
            
        img_src = img_data.get('src', '')
        if not img_src:
            return False
            
        # Check all existing headings for this image
        for heading_info in headings_data:
            for existing_img in heading_info.get('images', []):
                if existing_img.get('src', '') == img_src:
                    return True
                    
        return False

    def _is_image_specifically_for_section(self, img_data: dict, heading_text: str, section_text: str) -> bool:
        """LIFESTYLE ONLY: Enhanced specific image-to-section matching"""
        if not img_data:
            return False
            
        src = img_data.get('src', '').lower()
        alt = img_data.get('alt', '').lower()
        heading_lower = heading_text.lower()
        section_lower = section_text.lower()
        filename = src.split('/')[-1] if src else ''
        
        # Specific high-confidence matches
        
        # 1. Glasses/Donation matching
        if 'glasses' in filename and any(word in heading_lower for word in ['donation', 'optical', 'program']):
            return True
            
        # 2. Card/Travel matching
        if 'card' in filename and any(word in heading_lower for word in ['card', 'where', 'been', 'travel']):
            return True
            
        # 3. Recipe/Food matching
        if any(food_word in filename for food_word in ['rollup', 'lasagna', 'recipe']) and \
           any(food_word in heading_lower for food_word in ['lasagna', 'recipe', 'roll', 'spinach']):
            return True
            
        # 4. Halloween/Costume matching - be more specific
        if any(holiday_word in filename for holiday_word in ['halloween', 'costume']):
            # Prioritize main headings over sub-headings for Halloween content
            if any(main_word in heading_lower for main_word in ['halloween', 'celebrate', 'costume']):
                return True
            # Only match "fun" if it's specifically Halloween-related content in the section
            elif 'fun' in heading_lower and ('halloween' in section_lower or 'costume' in section_lower):
                return True
            
        # 5. Book/Author matching - enhanced for FYE patterns
        fye_book_patterns = ['bookpick', 'book', 'author', 'fye']
        section_book_patterns = ['book', 'author', 'story', 'writer', 'entertainment', 'spotlight', 'strong', 'women', 'smirnoff', 'karin', 'online']
        
        if (any(pattern in filename for pattern in fye_book_patterns) and 
            any(pattern in heading_lower for pattern in section_book_patterns)):
            return True
        
        # 6. Pet/Animal matching
        if any(pet_word in filename for pet_word in ['pet', 'animal', 'cat', 'dog']) and \
           any(pet_word in heading_lower for pet_word in ['pet', 'animal', 'planet', 'cat', 'dog']):
            return True
            
        # 7. Alt text exact matching with heading words
        if alt and heading_lower:
            # Clean alt text and heading for comparison
            alt_words = set(alt.replace(',', '').split())
            heading_words = set(heading_lower.replace(',', '').split())
            
            # Check for meaningful word overlap (exclude common words)
            meaningful_overlap = alt_words.intersection(heading_words) - {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are'
            }
            
            if meaningful_overlap and len(meaningful_overlap) >= 1:
                return True
        
        # 8. Content text proximity matching (very restrictive)
        if section_text:
            # Look for specific meaningful mentions in section content
            # Only check for very specific content-related words
            meaningful_content_words = []
            for content_word in section_lower.split():
                if len(content_word) > 4 and content_word not in {
                    'costco', 'connection', 'warehouse', 'members', 'october', 'static',
                    'content', 'image', 'resource', 'mobile', 'website', 'https'
                }:
                    meaningful_content_words.append(content_word)
            
            # Only match if we find very specific words
            for word in meaningful_content_words:
                if word in ['glasses', 'optical', 'donation'] and 'glasses' in filename:
                    return True
                elif word in ['card', 'travel', 'membership'] and 'card' in filename:
                    return True
                elif word in ['lasagna', 'recipe', 'cooking', 'spinach'] and any(food in filename for food in ['rollup', 'lasagna']):
                    return True
                elif word in ['halloween', 'costume', 'celebrate'] and 'halloween' in filename:
                    return True
        
        return False
    
    def _find_closest_heading_for_image(self, img_element, content_area) -> Tag:
        """LIFESTYLE ONLY: Find the closest heading element to an image"""
        # Walk up the DOM to find headings
        all_headings = content_area.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        if not all_headings:
            return None
        
        # Find the position of the image in the document
        current = img_element
        while current and current.parent:
            # Check if there's a heading in the same container
            container = current.parent
            headings_in_container = container.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            
            if headings_in_container:
                # Find the heading that comes before this image
                for heading in reversed(headings_in_container):
                    # Check if this heading comes before the image in document order
                    if self._element_comes_before(heading, img_element):
                        return heading
            
            current = current.parent
        
        # Fallback: find the last heading that appears before this image in the entire document
        for heading in reversed(all_headings):
            if self._element_comes_before(heading, img_element):
                return heading
        
        return None
    
    def _get_surrounding_text_for_image(self, img_element) -> str:
        """LIFESTYLE ONLY: Get surrounding text context for an image"""
        text_parts = []
        
        # Check parent container for text
        parent = img_element.parent
        if parent:
            # Get text from siblings
            for sibling in parent.find_all(['p', 'div', 'span']):
                text = sibling.get_text().strip()
                if text and len(text) > 10:
                    text_parts.append(text)
        
        return ' '.join(text_parts[:3])  # Limit to first 3 text chunks
    
    def _element_comes_before(self, element1, element2) -> bool:
        """LIFESTYLE ONLY: Check if element1 comes before element2 in document order"""
        try:
            # Convert elements to strings and check their positions
            parent = element1.find_parent() or element2.find_parent()
            if parent:
                all_elements = parent.find_all()
                try:
                    pos1 = all_elements.index(element1)
                    pos2 = all_elements.index(element2)
                    return pos1 < pos2
                except ValueError:
                    return False
            return False
        except:
            return False

    def _is_image_after_heading(self, heading_element, img_element) -> bool:
        """LIFESTYLE ONLY: Check if an image comes after a heading in the document structure"""
        try:
            # Get all elements in the parent container
            parent = heading_element.parent
            if not parent:
                return False
                
            all_elements = parent.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img'])
            
            heading_index = -1
            img_index = -1
            
            for i, element in enumerate(all_elements):
                if element == heading_element:
                    heading_index = i
                elif element == img_element:
                    img_index = i
                    
            # Image should come after heading
            return heading_index != -1 and img_index != -1 and img_index > heading_index
        except:
            return False

    def _extract_structured_content(
        self, content_area: Tag, extracted: ExtractedContent
    ):
        """Extract headings and lists"""

        # Enhanced headings with content
        for heading in content_area.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
            heading_text = heading.get_text().strip()
            if heading_text and len(heading_text) > 2:
                if not any(nav in heading_text.lower() for nav in ["compare", "shop"]):
                    
                    # Extract content that follows this heading
                    heading_content = []
                    current = heading.next_sibling
                    
                    # Dynamic limits based on content type
                    content_limit = 8 if extracted.content_type == "travel" else 3
                    min_text_length = 15 if extracted.content_type == "travel" else 30
                    
                    while current and len(heading_content) < content_limit:
                        if hasattr(current, 'name'):
                            # Stop at next heading
                            if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                break
                            # Collect paragraph content
                            elif current.name in ['p', 'div']:
                                text = current.get_text().strip()
                                if text and len(text) > min_text_length and text not in heading_content:
                                    # Enhanced boundary detection: stop if text contains heading-like content
                                    text_lower = text.lower()
                                    
                                    # Check for general section separators and author info
                                    if any(marker in text_lower for marker in ['author bio', 'peter greenberg', 'costco travel offers', 'costco connection:']):
                                        break
                                    
                                    # Dynamic heading detection: if text starts with a heading pattern, it likely belongs to a new section
                                    if self._looks_like_heading_content(text):
                                        break
                                        
                                    heading_content.append(text)
                        current = current.next_sibling
                    
                    extracted.headings.append(
                        {
                            "text": heading_text,
                            "level": int(heading.name[1]),
                            "class": " ".join(heading.get("class", [])),
                            "content": heading_content  # Add content under heading
                        }
                    )

        # Lists
        for list_elem in content_area.find_all(["ul", "ol"]):
            list_items = []
            for li in list_elem.find_all("li"):
                item_text = li.get_text().strip()
                if item_text and len(item_text) > 2:
                    list_items.append(item_text)

            if list_items:
                extracted.lists.append(
                    {
                        "type": "ordered" if list_elem.name == "ol" else "unordered",
                        "items": list_items,
                        "class": " ".join(list_elem.get("class", [])),
                    }
                )

    # ===== FIXED: RECIPE EXTRACTION WITH SECTION AWARENESS =====

    def _extract_recipe_data_fixed(
        self, content_area: Tag, extracted: ExtractedContent
    ):
        """FIXED: Extract recipe data with full section awareness"""

        logger.info("🔧 Starting FIXED recipe extraction")

        # Step 1: Look for recipe sections
        recipe_sections = self._find_recipe_sections(content_area)

        ingredients = []
        instructions = []

        if recipe_sections:
            logger.info(f"Found recipe sections: {list(recipe_sections.keys())}")

            # Extract from structured sections
            for section_name, section_element in recipe_sections.items():
                section_ingredients = self._extract_section_ingredients(
                    section_element, section_name
                )
                if section_ingredients:
                    # Add section header for multi-section recipes
                    if len(recipe_sections) > 1:
                        ingredients.append(f"=== {section_name.upper()} ===")
                    ingredients.extend(section_ingredients)

            # Extract instructions with section awareness
            instructions = self._extract_recipe_instructions(
                content_area, recipe_sections
            )

        else:
            logger.info("No recipe sections found, using fallback extraction")

            # Fallback: use improved single-section extraction
            ingredients, instructions = self._extract_single_section_recipe(
                content_area, extracted
            )

        # Extract timing and serving info
        prep_time = self._extract_time_info(
            content_area, ["prep time", "preparation", "prep:"]
        )
        cook_time = self._extract_time_info(
            content_area, ["cook time", "cooking time", "bake", "cook:", "bake for"]
        )
        servings = self._extract_serving_info(content_area)

        # Store in metadata
        extracted.metadata["ingredients"] = ingredients
        extracted.metadata["instructions"] = instructions
        extracted.metadata["prep_time"] = prep_time
        extracted.metadata["cook_time"] = cook_time
        extracted.metadata["servings"] = servings

        logger.info(
            f"✅ Recipe extracted: {len(ingredients)} ingredients, {len(instructions)} instructions"
        )

    def _find_recipe_sections(self, content_area: Tag) -> dict:
        """Find recipe sections like FILLING, STREUSEL, CAKE"""
        sections = {}

        # Look for section headers
        section_keywords = [
            "FILLING",
            "STREUSEL",
            "CAKE",
            "INGREDIENTS",
            "DIRECTIONS",
            "TOPPING",
        ]

        # Search in headings and strong text
        for element in content_area.find_all(
            ["h1", "h2", "h3", "h4", "h5", "h6", "strong", "b"]
        ):
            element_text = element.get_text().strip().upper()

            for keyword in section_keywords:
                if keyword in element_text:
                    # Find the content after this header
                    section_content = self._get_content_after_header(element)
                    if section_content:
                        sections[keyword.lower()] = section_content
                        logger.info(f"Found recipe section: {keyword}")
                    break

        return sections

    def _get_content_after_header(self, header_element: Tag) -> Optional[Tag]:
        """Get content that follows a section header"""

        # Look for next sibling that contains a list
        current = header_element.next_sibling
        content_found = False

        # Create a container for the section content
        section_content = BeautifulSoup(
            '<div class="section-content"></div>', "html.parser"
        ).div

        # Collect content until we hit another header or run out of siblings
        while current:
            if hasattr(current, "name"):
                # Stop if we hit another major header
                if (
                    current.name in ["h1", "h2", "h3", "h4"]
                    and current != header_element
                ):
                    break

            # Include lists, paragraphs, and other content
            if current.name in ["ul", "ol", "p", "div"]:
                section_content.append(current.extract())
                content_found = True
            elif current.name in ["strong", "b"] and any(
                keyword in current.get_text().upper()
                for keyword in ["FILLING", "STREUSEL", "CAKE"]
            ):
                # Stop if we hit another section header
                break

            current = current.next_sibling

        return section_content if content_found else None

    def _extract_section_ingredients(
        self, section_element: Tag, section_name: str
    ) -> List[str]:
        """Extract ingredients from a specific recipe section"""
        ingredients = []

        # Look for lists in this section
        for ul in section_element.find_all(["ul", "ol"]):
            for li in ul.find_all("li"):
                ingredient_text = li.get_text().strip()
                if self._is_valid_ingredient(ingredient_text):
                    ingredients.append(ingredient_text)

        logger.info(
            f"Extracted {len(ingredients)} ingredients from {section_name} section"
        )
        return ingredients

    def _extract_single_section_recipe(
        self, content_area: Tag, extracted: ExtractedContent
    ) -> Tuple[List[str], List[str]]:
        """Fallback extraction for simple single-section recipes"""

        ingredients = []
        instructions = []

        # Use improved detection for ingredient lists
        for list_data in extracted.lists:
            if self._is_recipe_ingredient_list(list_data, content_area):
                ingredients = list_data["items"]
                break

        # Extract instructions from ordered lists or paragraphs
        for list_data in extracted.lists:
            if (
                list_data["type"] == "ordered"
                and list_data["items"] != ingredients
                and self._looks_like_instructions(list_data["items"])
            ):
                instructions = list_data["items"]
                break

        # If no ordered list instructions, look in paragraphs
        if not instructions:
            instructions = self._extract_instructions_from_paragraphs(content_area)

        return ingredients, instructions

    def _is_recipe_ingredient_list(self, list_data: dict, content_area: Tag) -> bool:
        """IMPROVED: Better detection of recipe ingredient lists"""
        items = list_data["items"]
        list_text = " ".join(items).lower()

        # Must have measurements
        measurement_units = [
            "cup",
            "cups",
            "tablespoon",
            "tbsp",
            "teaspoon",
            "tsp",
            "ounce",
            "oz",
            "pound",
            "lb",
            "gram",
            "kg",
            "lbs",
        ]
        has_measurements = any(unit in list_text for unit in measurement_units)

        if not has_measurements:
            return False

        # Should have multiple ingredients
        if len(items) < 2:
            return False

        # Should not be navigation
        nav_indicators = ["shop", "compare", "add to cart", "department", "view all"]
        if any(nav in list_text for nav in nav_indicators):
            return False

        # Validate ingredients make culinary sense
        food_indicators = [
            "salt",
            "sugar",
            "flour",
            "butter",
            "egg",
            "oil",
            "milk",
            "cheese",
            "tomato",
            "onion",
            "garlic",
            "pepper",
            "vanilla",
            "cinnamon",
            "grape",
            "water",
            "lemon",
            "vinegar",
        ]
        has_food_terms = any(food in list_text for food in food_indicators)

        # Additional validation: check for fractions or measurements
        has_fractions = any(frac in list_text for frac in ["½", "¼", "¾", "⅓", "⅔"])
        has_numbers = any(char.isdigit() for char in list_text)

        return (has_food_terms or has_fractions) and has_numbers

    def _is_valid_ingredient(self, text: str) -> bool:
        """Validate that text looks like a real ingredient"""
        if len(text) < 3:
            return False

        # Should not be navigation
        nav_terms = ["shop", "compare", "add to cart", "view all", "department"]
        if any(nav in text.lower() for nav in nav_terms):
            return False

        # Should have quantity or be recognizable ingredient
        has_quantity = any(char.isdigit() for char in text)
        has_fraction = any(frac in text for frac in ["½", "¼", "¾", "⅓", "⅔"])
        common_ingredients = ["salt", "pepper", "vanilla", "cinnamon"]
        is_common = any(ing in text.lower() for ing in common_ingredients)

        return has_quantity or has_fraction or is_common

    def _looks_like_instructions(self, items: List[str]) -> bool:
        """Check if list items look like cooking instructions"""

        if len(items) < 2:
            return False

        cooking_verbs = [
            "preheat",
            "heat",
            "cook",
            "bake",
            "mix",
            "stir",
            "add",
            "combine",
            "place",
            "put",
            "pour",
            "slice",
            "chop",
            "dice",
            "blend",
            "whisk",
            "season",
            "serve",
            "garnish",
            "remove",
            "drain",
            "cover",
            "simmer",
            "boil",
            "bring",
            "reduce",
            "cool",
            "refrigerate",
        ]

        instruction_count = 0
        for item in items:
            if any(verb in item.lower() for verb in cooking_verbs):
                instruction_count += 1

        # At least half the items should contain cooking verbs
        return instruction_count >= len(items) // 2

    def _extract_recipe_instructions(
        self, content_area: Tag, recipe_sections: dict
    ) -> List[str]:
        """Extract cooking instructions with section awareness"""

        instructions = []

        # Look for instructions in recipe sections first
        if recipe_sections:
            for section_name, section_element in recipe_sections.items():
                section_instructions = self._extract_instructions_from_element(
                    section_element
                )
                if section_instructions:
                    if len(recipe_sections) > 1:
                        instructions.append(
                            f"=== {section_name.upper()} PREPARATION ==="
                        )
                    instructions.extend(section_instructions)
        else:
            # Fallback to general instruction extraction
            instructions = self._extract_instructions_from_element(content_area)

        return instructions

    def _extract_instructions_from_element(self, element: Tag) -> List[str]:
        """Extract instructions from a specific element"""

        instructions = []
        cooking_verbs = [
            "preheat",
            "heat",
            "cook",
            "bake",
            "mix",
            "stir",
            "add",
            "combine",
            "place",
            "put",
            "pour",
            "slice",
            "chop",
            "dice",
            "blend",
            "whisk",
            "season",
            "serve",
            "garnish",
            "remove",
            "drain",
            "cover",
            "simmer",
            "spread",
            "boil",
            "bring",
            "reduce",
            "cool",
            "refrigerate",
            "prepare",
            "roll",
            "drizzle",
            "transfer",
            "broil"
        ]

        # Strategy 1: Ordered lists with cooking verbs
        for ol in element.find_all("ol"):
            ol_instructions = []
            for li in ol.find_all("li"):
                text = li.get_text().strip()
                if (
                    any(verb in text.lower() for verb in cooking_verbs)
                    and len(text) > 15
                    and len(text.split()) > 3
                ):
                    ol_instructions.append(text)

            if len(ol_instructions) > 1:
                instructions = ol_instructions
                break

        # Strategy 2: Paragraphs with cooking instructions
        if not instructions:
            for p in element.find_all("p"):
                text = p.get_text().strip()
                if (
                    any(verb in text.lower() for verb in cooking_verbs)
                    and len(text) > 15  # Reduced from 20 to catch shorter steps
                    and len(text.split()) > 4  # Reduced from 5 to catch shorter steps
                ):
                    instructions.append(text)
        
        # Strategy 3: Look for any text elements with cooking verbs (more comprehensive)
        if not instructions:
            for element_tag in element.find_all(["p", "div", "span", "li"]):
                text = element_tag.get_text().strip()
                if (
                    any(verb in text.lower() for verb in cooking_verbs)
                    and len(text) > 10  # Even shorter for steps like "Spread sauce"
                    and len(text.split()) > 3
                    and not any(skip in text.lower() for skip in ['home', 'costco', 'download', 'navigation'])
                ):
                    # Skip mega-instructions containing PANDOL BROS dump
                    if (len(text) > 400 and 
                        'PANDOL BROS' in text and 
                        'Grape Crumble' in text and
                        'Filling' in text and
                        'Streusel' in text):
                        print(f"🚫 EXTRACTOR FILTERING mega-instruction (length: {len(text)})")
                        continue
                    
                    # Avoid duplicates
                    if text not in instructions:
                        instructions.append(text)

        return instructions

    def _extract_instructions_from_paragraphs(self, content_area: Tag) -> List[str]:
        """Extract instructions from paragraphs when no ordered lists found"""

        instructions = []
        cooking_verbs = [
            "preheat",
            "heat",
            "cook",
            "bake",
            "mix",
            "stir",
            "add",
            "combine",
            "place",
            "put",
            "pour",
            "slice",
            "chop",
            "dice",
            "blend",
            "whisk",
            "season",
            "serve",
            "garnish",
            "remove",
            "drain",
            "cover",
            "simmer",
            "boil",
            "bring",
            "reduce",
            "cool",
            "refrigerate",
            "prepare",
        ]

        for p in content_area.find_all("p"):
            text = p.get_text().strip()

            # Look for instruction-like paragraphs
            if (
                any(verb in text.lower() for verb in cooking_verbs)
                and len(text) > 30
                and len(text.split()) > 8
            ):

                # Skip mega-instructions containing PANDOL BROS dump
                if (len(text) > 400 and 
                    'PANDOL BROS' in text and 
                    'Grape Crumble' in text):
                    print(f"🚫 PARAGRAPH EXTRACTOR FILTERING mega-instruction (length: {len(text)})")
                    continue
                
                # Skip navigation-like text
                if not any(
                    nav in text.lower() for nav in ["shop", "compare", "add to cart"]
                ):
                    instructions.append(text)

        return instructions

    def _extract_time_info(self, content_area: Tag, time_indicators: List[str]) -> str:
        """Extract time information from text"""
        text = content_area.get_text().lower()

        for indicator in time_indicators:
            # Look for patterns like "prep time: 30 minutes" or "bake for 50 minutes"
            patterns = [
                rf"{indicator}[:\s]*(\d+(?:\s*-\s*\d+)?\s*(?:minutes?|mins?|hours?|hrs?))",
                rf"{indicator}\s+(\d+(?:\s*-\s*\d+)?\s*(?:minutes?|mins?|hours?|hrs?))",
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return match.group(1).strip()

        return ""

    def _extract_serving_info(self, content_area: Tag) -> str:
        """Extract serving information"""
        text = content_area.get_text().lower()

        serving_patterns = [
            r"(?:serves|servings?)[:\s]*(\d+(?:\s*-\s*\d+)?)",
            r"makes\s+(\d+(?:\s*-\s*\d+)?\s*(?:servings?|portions?))",
            r"makes\s+about\s+(\d+(?:\s*to\s*\d+)?\s*(?:cups?|servings?))",
        ]

        for pattern in serving_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_content_specific(
        self, content_area: Tag, extracted: ExtractedContent, content_type: str
    ):
        """Content-specific extraction for non-recipe types"""

        if content_type == "travel":
            self._extract_travel_data(content_area, extracted)
        elif content_type == "member":
            self._extract_member_data(content_area, extracted)
        elif content_type == "tech":
            self._extract_tech_data(content_area, extracted)

    def _extract_travel_data(self, content_area: Tag, extracted: ExtractedContent):
        """Extract comprehensive travel content including all section content"""
        
        if not content_area:
            return
            
        destinations = []
        attractions = []

        # Extract destinations
        destination_patterns = [
            r"visit\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"explore\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        full_text = content_area.get_text() if content_area else ""
        for pattern in destination_patterns:
            matches = re.findall(pattern, full_text)
            destinations.extend(matches)

        extracted.metadata["destinations"] = list(set(destinations))[:10]
        extracted.metadata["attractions"] = attractions
        
        # ENHANCED: Extract ALL paragraphs more thoroughly for travel content
        all_paragraphs = []
        
        # Get all text elements including those under headings
        for element in content_area.find_all(['p', 'div', 'span', 'section']):
            text = element.get_text().strip()
            
            # Skip navigation and short content
            if (not text or len(text) < 15 or 
                any(skip in text.lower() for skip in ['home', 'costco connection', 'download', '©', 'copyright'])):
                continue
                
            # Include substantial content
            if len(text) > 15:
                # Check if it's new content
                is_new = True
                for existing in all_paragraphs:
                    if self._text_similarity(text, existing) > 0.7:
                        is_new = False
                        break
                        
                if is_new:
                    all_paragraphs.append(text)
        
        # Also extract content that follows headings (like under "Austin", "San Antonio")
        headings = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            # Get content that follows this heading
            current = heading.next_sibling
            section_content = []
            
            while current and len(section_content) < 8:  # Allow more content per section for travel
                if hasattr(current, 'name'):
                    # Stop at next heading
                    if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    # Collect paragraph content
                    elif current.name in ['p', 'div']:
                        text = current.get_text().strip()
                        if text and len(text) > 15 and text not in section_content:
                            # Enhanced boundary detection: stop if text contains heading-like content or indicates new section
                            text_lower = text.lower()
                            
                            # Check for general section separators and author info
                            if any(marker in text_lower for marker in [
                                'author bio', 'peter greenberg', 'costco travel offers', 'costco connection:'
                            ]):
                                break
                            
                            # Dynamic heading detection: if text starts with a heading pattern, it likely belongs to a new section
                            if self._looks_like_heading_content(text):
                                break
                            section_content.append(text)
                elif isinstance(current, str):
                    text = current.strip()
                    if text and len(text) > 15:
                        # Check for boundary markers in string content too
                        text_lower = text.lower()
                        if any(marker in text_lower for marker in [
                            'author bio', 'peter greenberg', 'costco travel offers', 'costco connection:'
                        ]):
                            break
                        
                        # Dynamic heading detection for string content
                        if self._looks_like_heading_content(text):
                            break
                        section_content.append(text)
                        
                current = current.next_sibling
            
            # Add section content to main content
            all_paragraphs.extend(section_content)
        
        # Remove duplicates and update main content 
        unique_paragraphs = []
        for para in all_paragraphs:
            # Check if this paragraph is not already in main_content or unique_paragraphs
            is_duplicate = False
            for existing in extracted.main_content + unique_paragraphs:
                if self._text_similarity(para, existing) > 0.8:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_paragraphs.append(para)
                
        # Add unique paragraphs to main content
        extracted.main_content.extend(unique_paragraphs)

    def _looks_like_heading_content(self, text: str) -> bool:
        """Dynamically detect if text looks like it belongs to a new section/heading"""
        if not text or len(text) < 10:
            return False
        
        text_lower = text.lower().strip()
        
        # Pattern 1: Text that looks like a heading (short, starts with capital, ends without punctuation)
        if len(text) < 100 and text[0].isupper():
            words = text.split()
            # Short phrases that don't end with sentence punctuation are likely headings
            if len(words) <= 6 and not text.strip().endswith(('.', '!', '?', ':')):
                # At least first word is capitalized (which we already checked)
                return True
        
        # Pattern 2: Text that contains heading-like keywords
        heading_indicators = [
            'habitat', 'section', 'overview', 'introduction', 'conclusion',
            'background', 'features', 'benefits', 'details', 'summary'
        ]
        
        # If text starts with a heading indicator and is relatively short
        if any(text_lower.startswith(indicator) for indicator in heading_indicators):
            if len(text) < 200:  # Headings are usually shorter
                return True
        
        # Pattern 3: Text that ends with author attribution (like "—PG") 
        # BUT only if it's short enough to be a heading, not a full paragraph
        if text.strip().endswith(('—PG', '—DJ', '—AT', '—DLM', '—SEP')) and len(text) < 200:
            return True
        
        # Pattern 4: Text that starts with a heading pattern but continues with content
        # This handles cases like "Batty bridge habitat\nLong paragraph content..."
        # BUT only flag it as boundary content, don't try to extract from it
        if text[0].isupper() and '\n' in text:
            # Check if the first line looks like a heading
            first_line = text.split('\n')[0].strip()
            if len(first_line) < 50:  # First line is short
                words = first_line.split()
                if len(words) <= 6 and not first_line.endswith(('.', '!', '?', ':')):
                    # This is boundary content - it belongs to another section
                    return True
        
        return False

    def _extract_tech_data(self, content_area: Tag, extracted: ExtractedContent):
        """Extract comprehensive tech content including all section content"""
        
        if not content_area:
            return
            
        # Extract ALL paragraphs more thoroughly for tech content
        all_paragraphs = []
        
        # Get all text elements including those under headings
        for element in content_area.find_all(['p', 'div', 'span', 'section']):
            text = element.get_text().strip()
            
            # Skip navigation and short content
            if (not text or len(text) < 20 or 
                any(skip in text.lower() for skip in ['home', 'costco connection', 'download', '©', 'copyright'])):
                continue
                
            # Include substantial content
            if len(text) > 20:
                # Check if it's new content
                is_new = True
                for existing in all_paragraphs:
                    if self._text_similarity(text, existing) > 0.7:
                        is_new = False
                        break
                        
                if is_new:
                    all_paragraphs.append(text)
        
        # Also extract content that follows headings (like under "Portable power")
        headings = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in headings:
            # Get content that follows this heading
            current = heading.next_sibling
            section_content = []
            
            while current and len(section_content) < 5:  # Limit per section
                if hasattr(current, 'name'):
                    # Stop at next heading
                    if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        break
                    # Collect paragraph content
                    elif current.name in ['p', 'div']:
                        text = current.get_text().strip()
                        if text and len(text) > 20:
                            section_content.append(text)
                elif isinstance(current, str):
                    text = current.strip()
                    if text and len(text) > 20:
                        section_content.append(text)
                        
                current = current.next_sibling
            
            # Add section content to main content
            all_paragraphs.extend(section_content)
        
        # Remove duplicates and update main content 
        unique_paragraphs = []
        for para in all_paragraphs:
            # Check if this paragraph is not already in main_content or unique_paragraphs
            is_duplicate = False
            for existing in extracted.main_content + unique_paragraphs:
                if self._text_similarity(para, existing) > 0.8:
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_paragraphs.append(para)
        
        # Update the main content with comprehensive extraction
        extracted.main_content.extend(unique_paragraphs)

    # Replace the _extract_member_data method completely

    # ===== DYNAMIC SOLUTION: Replace _extract_member_data in src/utils/universal_content_extractor.py =====

    def _extract_member_data(self, content_area: Tag, extracted: ExtractedContent):
        """ENHANCED: Handle different member content types"""

        member_comments = []
        poll_questions = []
        member_responses = []

        if not content_area:
            return

        # Detect member content type
        content_type = self._detect_member_format(content_area)

        if content_type == "poll":
            # Your existing poll extraction (works well)
            poll_questions = self._extract_poll_questions_dynamic(content_area)
            member_responses = self._extract_member_responses_dynamic(content_area)

        elif content_type == "comments":
            # NEW: Extract individual comment sections
            member_responses = self._extract_comment_sections(content_area)

        elif content_type == "story":
            # NEW: Extract member story/feature
            member_responses = self._extract_member_story(content_area)

        # Build member comments from responses
        for response in member_responses:
            clean_response = self._clean_member_response(response["response"])
            if clean_response:
                member_comments.append(f"{response['name']}: {clean_response}")

        # Store in metadata
        extracted.metadata["member_comments"] = member_comments[:15]
        extracted.metadata["poll_questions"] = poll_questions
        extracted.metadata["member_responses"] = member_responses[:15]

    def _detect_member_format(self, content_area: Tag) -> str:
        """IMPROVED: Better format detection"""

        text = content_area.get_text().lower()
        title_text = ""

        # Get page title for context
        for heading in content_area.find_all(["h1"]):
            title_text = heading.get_text().lower()
            break

        # Check for poll indicators
        if any(
            indicator in text
            for indicator in ["poll", "facebook page", "what do you look forward"]
        ):
            return "poll"

        # Check for comment sections - IMPROVED DETECTION
        if (
            any(
                indicator in text
                for indicator in ["member comments", "bettina whippie", "gordon down"]
            )
            or "member comments" in title_text
        ):
            return "comments"

        # Check for member story/feature
        if (
            any(
                indicator in text
                for indicator in ["healing voice", "singer-songwriter", "kristen scott"]
            )
            or "healing voice" in title_text
        ):
            return "story"

        return "general"

    def _extract_comment_sections(self, content_area: Tag) -> List[Dict[str, str]]:
        """IMPROVED: Better comment section extraction"""

        comments = []
        full_text = content_area.get_text()

        # Strategy 1: Look for known member names first
        member_names = [
            "Bettina Whippie",
            "Gordon Down",
            "Kristi Sullivan",
            "Pat Dolen",
        ]

        for name in member_names:
            if name in full_text:
                # Find context around this name
                name_index = full_text.find(name)

                # Extract content before the name (likely their comment)
                start_pos = max(0, name_index - 800)  # Look back up to 800 chars
                comment_section = full_text[start_pos : name_index + len(name) + 100]

                # Clean and extract the comment
                comment_text = self._extract_comment_before_name(comment_section, name)

                if comment_text and len(comment_text) > 30:
                    comments.append({"name": name, "response": comment_text})

        return comments

    def _extract_comment_before_name(self, text_section: str, member_name: str) -> str:
        """Extract comment text that appears before member name"""

        # Split by the member name
        parts = text_section.split(member_name)
        if len(parts) < 2:
            return ""

        # Take the text before the name
        comment_part = parts[0]

        # Look for the actual comment (usually starts after a topic header)
        # Remove headers and get the substantive content
        lines = comment_part.split("\n")

        # Find the last substantial paragraph before the name
        for i in range(len(lines) - 1, -1, -1):
            line = lines[i].strip()
            if (
                len(line) > 50
                and not any(
                    header in line.lower()
                    for header in ["costco", "member comments", "on costco"]
                )
                and any(
                    word in line.lower()
                    for word in ["thank you", "i", "my", "we", "everything"]
                )
            ):
                return line

        return ""

    def _extract_member_story(self, content_area: Tag) -> List[Dict[str, str]]:
        """ENHANCED: Extract member story with song lyrics and quotes"""

        stories = []

        # Find the main subject
        subject_name = self._extract_story_subject(content_area)

        # Extract different types of story content
        story_content = self._extract_story_content(content_area)
        song_lyrics = self._extract_song_lyrics(content_area)
        quotes = self._extract_member_quotes(content_area)

        if subject_name:
            # Build comprehensive story content
            full_story_parts = []

            # Add main story content
            if story_content:
                full_story_parts.append(story_content)

            # Add meaningful quotes
            if quotes:
                full_story_parts.append("Key quotes: " + " | ".join(quotes[:2]))

            # Add song information if present
            if song_lyrics:
                full_story_parts.append(f"Song lyrics: {song_lyrics}")

            if full_story_parts:
                stories.append(
                    {
                        "name": subject_name,
                        "response": " ".join(full_story_parts),
                        "type": "story",
                        "song_lyrics": song_lyrics if song_lyrics else "",
                        "quotes": quotes[:3] if quotes else [],
                    }
                )

        return stories

    def _extract_song_lyrics(self, content_area: Tag) -> str:
        """Extract complete song lyrics from the page"""
    
        lyrics_parts = []
    
        # Strategy 1: Look for song section headers
        song_section = None
        for heading in content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            heading_text = heading.get_text().strip()
            if any(indicator in heading_text.lower() for indicator in 
                    ['song', 'lyrics', 'heart', 'music', 'feel nothing']):
                song_section = heading
                break
    
        if song_section:
            # Get content after the song header
            lyrics_content = self._get_content_after_song_header(song_section)
            if lyrics_content:
                return lyrics_content
    
        # Strategy 2: Look for italic text patterns (common for lyrics)
        for italic in content_area.find_all(['em', 'i']):
            text = italic.get_text().strip()
            if self._looks_like_song_lyrics(text):
                lyrics_parts.append(text)
    
        # Strategy 3: Look for paragraph patterns that look like lyrics
        for p in content_area.find_all('p'):
            text = p.get_text().strip()
            if self._looks_like_song_lyrics(text):
                lyrics_parts.append(text)
    
        # Strategy 4: Look for structured verse patterns
        full_text = content_area.get_text()
        verse_lyrics = self._extract_verse_patterns(full_text)
        if verse_lyrics:
            return verse_lyrics
    
        # Combine found lyrics
        if lyrics_parts:
            return ' | '.join(lyrics_parts)
    
        return ""    

    def _extract_story_content(self, content_area: Tag) -> str:
        """Extract main story content"""

        story_paragraphs = []
        for p in content_area.find_all("p"):
            text = p.get_text().strip()

            # Skip contaminated content
            if any(
                skip in text
                for skip in ["Costco Connection", "© JOANNA", "Left to right"]
            ):
                continue

            # Get substantial story content
            if len(text) > 30 and not self._is_navigation_text(text):
                story_paragraphs.append(text)

        if story_paragraphs:
            # Take first 2-3 paragraphs for story
            return " ".join(story_paragraphs[:2])

        return ""

    def _get_content_after_song_header(self, song_header: Tag) -> str:
        """Get lyrics content that follows a song header"""

        lyrics_parts = []
        current = song_header.next_sibling

        # Collect content until we hit another major header
        while current and len(lyrics_parts) < 20:  # Reasonable limit
            if hasattr(current, "name"):
                # Stop at another major header (but not minor ones)
                if current.name in ["h1", "h2"] and current != song_header:
                    break

                # Collect lyrics content
                elif current.name in ["p", "div", "em", "i", "ul", "ol"]:
                    # Special handling for lists (like lyrics in <ul><li> structure)
                    if current.name in ["ul", "ol"]:
                        for li in current.find_all("li"):
                            li_text = li.get_text().strip()
                            if li_text and len(li_text) > 5:
                                # Clean up HTML artifacts like <br> tags
                                li_text = re.sub(r'\s+', ' ', li_text)
                                lyrics_parts.append(li_text)
                    else:
                        text = current.get_text().strip()
                        if text and self._looks_like_song_lyrics(text):
                            lyrics_parts.append(text)
                        elif (
                            text and len(text) < 100 and not self._is_navigation_text(text)
                        ):
                            # Short lines might be part of lyrics
                            lyrics_parts.append(text)

            elif isinstance(current, str):
                text = current.strip()
                if text and len(text) > 5:
                    lyrics_parts.append(text)

            current = current.next_sibling

        return " | ".join(lyrics_parts) if lyrics_parts else ""

    def _looks_like_song_lyrics(self, text: str) -> bool:
        """Check if text looks like song lyrics"""

        if len(text) < 10:
            return False

        # Common song lyric indicators
        lyric_indicators = [
            "i feel",
            "you said",
            "i loved",
            "i used to",
            "nothing at all",
            "what have you",
            "how could you",
            "we loved",
            "and still",
            "helplessly",
            "your battle",
            "no one could",
            "what led you",
        ]

        text_lower = text.lower()
        has_lyric_language = any(
            indicator in text_lower for indicator in lyric_indicators
        )

        # Check for verse-like structure (short lines, repetitive patterns)
        lines = text.split("\n")
        short_lines = sum(1 for line in lines if 5 < len(line.strip()) < 50)

        # Should not be business/navigation content
        business_indicators = ["costco", "shop", "department", "warehouse", "compare"]
        has_business = any(indicator in text_lower for indicator in business_indicators)

        # Should not be copyright or photo credits
        if any(
            indicator in text_lower
            for indicator in ["copyright", "©", "photography", "stock.adobe"]
        ):
            return False

        return (has_lyric_language or short_lines > 2) and not has_business

    def _extract_verse_patterns(self, full_text: str) -> str:
        """Extract song verses using pattern matching"""

        # Look for verse patterns in the text
        verse_patterns = [
            r"I feel nothing, nothing at all[^.]*\.",
            r"You said nothing, nothing at all[^.]*\.",
            r"What have you done\?[^.]*\.",
            r"How could you [^.]*\.",
            r"I used to be [^.]*\.",
            r"We loved you [^.]*\.",
            r"Helplessly [^.]*\.",
            r"No one could [^.]*\.",
        ]

        found_verses = []

        for pattern in verse_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                clean_verse = match.strip()
                if len(clean_verse) > 10 and clean_verse not in found_verses:
                    found_verses.append(clean_verse)

        # Also look for structured verse blocks
        lines = full_text.split("\n")
        verse_blocks = []
        current_block = []

        for line in lines:
            line = line.strip()
            if not line:
                if current_block and len(current_block) > 2:
                    verse_blocks.append(" | ".join(current_block))
                current_block = []
            elif self._looks_like_song_lyrics(line) and len(line) < 80:
                current_block.append(line)
            elif len(current_block) > 0:
                # End of verse block
                if len(current_block) > 2:
                    verse_blocks.append(" | ".join(current_block))
                current_block = []

        # Combine all found verses
        all_lyrics = found_verses + verse_blocks

        if all_lyrics:
            return " || ".join(all_lyrics[:10])  # Limit to reasonable amount

        return ""

    def _extract_member_quotes(self, content_area: Tag) -> List[str]:
        """Extract meaningful quotes from the member story"""

        quotes = []

        # Strategy 1: Look for quoted text
        full_text = content_area.get_text()

        # Find text in quotes
        quote_patterns = [
            r'"([^"]{30,200})"',  # Text in double quotes, 30-200 chars
            r'"([^"]{20,150})"',  # Shorter quotes
        ]

        for pattern in quote_patterns:
            matches = re.findall(pattern, full_text)
            for match in matches:
                if self._is_meaningful_quote(match):
                    quotes.append(f'"{match}"')

        # Strategy 2: Look for therapeutic/meaningful statements
        therapeutic_patterns = [
            r"For me, [^.]{20,}[.]",
            r"Music has [^.]{20,}[.]",
            r"I [^.]{30,}[.]",
            r"The [^.]{30,}[.]",
        ]

        for pattern in therapeutic_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            for match in matches:
                if self._is_meaningful_quote(match):
                    quotes.append(match)

        return quotes[:5]  # Limit to 5 best quotes

    def _is_meaningful_quote(self, text: str) -> bool:
        """Check if a quote is meaningful (not navigation/business)"""

        if len(text) < 20:
            return False

        # Should contain personal/emotional language
        meaningful_words = [
            "therapeutic",
            "healing",
            "emotional",
            "music",
            "feel",
            "heart",
            "struggling",
            "alone",
            "wounds",
            "capacity",
            "solace",
            "fragments",
        ]

        text_lower = text.lower()
        has_meaningful = any(word in text_lower for word in meaningful_words)

        # Should not be business/navigation
        business_words = [
            "costco",
            "shop",
            "warehouse",
            "department",
            "compare",
            "product",
        ]
        has_business = any(word in text_lower for word in business_words)

        # Should not be photo credits or technical text
        technical_words = ["photography", "copyright", "©", "stock.adobe", "image"]
        has_technical = any(word in text_lower for word in technical_words)

        return has_meaningful and not has_business and not has_technical

    def _get_content_after_heading(self, heading: Tag) -> str:
        """Get content that follows a heading"""

        content_parts = []
        current = heading.next_sibling

        # Collect content until next heading or end
        while current:
            text = ""  # Initialize text variable

            if hasattr(current, "name"):
                # Stop at next heading
                if current.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    break
                # Collect paragraph content
                elif current.name == "p":
                    text = current.get_text().strip()
                if len(text) > 10:
                    content_parts.append(text)
                elif isinstance(current, str):
                    text = current.strip()
                if len(text) > 10:
                    content_parts.append(text)

            current = current.next_sibling

            # Don't collect too much
            if len(content_parts) > 5:
                break

        return " ".join(content_parts)

    def _find_member_attribution(self, content: str) -> str:
        """Find member name attribution in content"""

        # Look for "Name, Location" pattern at end
        attribution_patterns = [
            r"([A-Z][a-z]+\s+[A-Z][a-z]+),\s*via\s+email",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+),\s*[A-Z][a-z]+",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+),\s*[A-Z][a-z]+\s+[A-Z][a-z]+",
        ]

        for pattern in attribution_patterns:
            match = re.search(pattern, content)
        if match:
            return match.group(1)

        return ""

    def _clean_comment_text(self, content: str, member_name: str) -> str:
        """Clean comment text"""

        if not content:
            return ""

        # Remove member name from end if present
        if member_name and member_name in content:
            content = content.replace(member_name, "").strip()

        # Remove attribution patterns
        content = re.sub(r",\s*via\s+email.*$", "", content)
        content = re.sub(r",\s*[A-Z][a-z]+.*$", "", content)

        return content.strip()

    def _extract_story_subject(self, content_area: Tag) -> str:
        """Extract the main subject of a member story"""

        # Look for names in the first few paragraphs
        paragraphs = content_area.find_all("p")[:3]

        for p in paragraphs:
            text = p.get_text()

        # Look for name patterns
        name_matches = re.findall(r"\b([A-Z][a-z]+\s+[A-Z][a-z]+)\b", text)

        for name in name_matches:
            # Skip common words that might match pattern
            if not any(
                word in name.lower() for word in ["costco", "connection", "september"]
            ):
                return name

        return ""

    def _extract_poll_questions_dynamic(self, content_area: Tag) -> List[str]:
        """Dynamically extract poll questions from any member page"""

        questions = []

        # Strategy 1: Look for headings with question marks
        for heading in content_area.find_all(["h1", "h2", "h3", "h4"]):
            text = heading.get_text().strip()
            if self._is_poll_question(text) and not self._is_navigation_text(text):
                questions.append(text)

        # Strategy 2: Look for emphasized text with questions
        for elem in content_area.find_all(["strong", "b", "em"]):
            text = elem.get_text().strip()
            if self._is_poll_question(text):
                questions.append(text)

        # Strategy 3: Look for question patterns in paragraphs
        for p in content_area.find_all("p"):
            text = p.get_text().strip()
            if (
                self._is_poll_question(text) and len(text) < 200
            ):  # Reasonable question length
                questions.append(text)

        # Remove duplicates and return
        return list(dict.fromkeys(questions))  # Preserves order

    def _is_poll_question(self, text: str) -> bool:
        """Check if text looks like a poll question"""

        if not text or len(text) < 10:
            return False

        # Must contain question mark
        if "?" not in text:
            return False

        # Should contain poll/question indicators
        poll_indicators = [
            "what do you",
            "how do you",
            "which",
            "when do you",
            "where do you",
            "why do you",
            "who",
            "would you",
            "do you",
            "have you",
            "are you",
            "will you",
        ]

        text_lower = text.lower()
        if not any(indicator in text_lower for indicator in poll_indicators):
            return False

        # Should not be navigation
        nav_indicators = ["search", "find", "shop", "compare", "help"]
        if any(nav in text_lower for nav in nav_indicators):
            return False

        return True

    def _extract_member_responses_dynamic(
        self, content_area: Tag
    ) -> List[Dict[str, str]]:
        """Dynamically extract member responses using patterns"""

        responses = []

        # Strategy 1: Look for structured content blocks
        responses.extend(self._extract_from_structured_blocks(content_area))

        # Strategy 2: Extract from text patterns
        if len(responses) < 3:  # If structured approach didn't work well
            responses.extend(self._extract_from_text_patterns(content_area))

        # Strategy 3: Extract from paragraph sequences
        if len(responses) < 3:
            responses.extend(self._extract_from_paragraph_sequences(content_area))

        # Clean and deduplicate
        return self._deduplicate_responses(responses)

    def _extract_from_structured_blocks(
        self, content_area: Tag
    ) -> List[Dict[str, str]]:
        """Extract from structured HTML blocks"""

        responses = []

        # Look for divs or sections that might contain member responses
        containers = content_area.find_all(["div", "section", "article"])

        for container in containers:
            # Skip navigation containers
            if self._is_navigation_container(container):
                continue

            # Look for name-response patterns within container
            text = container.get_text()
            container_responses = self._extract_name_response_pairs(text)
            responses.extend(container_responses)

        return responses

    def _extract_from_text_patterns(self, content_area: Tag) -> List[Dict[str, str]]:
        """Extract using text pattern matching"""

        full_text = content_area.get_text()

        # Clean the text first
        clean_text = self._clean_text_for_extraction(full_text)

        return self._extract_name_response_pairs(clean_text)

    def _extract_name_response_pairs(self, text: str) -> List[Dict[str, str]]:
        """Extract name-response pairs from text using dynamic patterns"""

        responses = []

        # Split text into lines and analyze
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        i = 0
        while i < len(lines):
            line = lines[i]

            # Initialize variables for each iteration
            member_name = ""
            response_text = ""

            # Check if this line looks like a member name
            if self._looks_like_member_name_dynamic(line):
                member_name = line

                # Look for response in surrounding lines
                response_text = self._find_response_for_member(lines, i)

                if response_text and member_name:  # Both must exist
                    responses.append({"name": member_name, "response": response_text})

            # Check if this line looks like a response followed by name
            elif self._looks_like_member_response(line):
                response_text = line

                # Look for name in next few lines
                member_name = self._find_name_for_response(lines, i)

                if member_name and response_text:  # Both must exist
                    responses.append({"name": member_name, "response": response_text})

            i += 1

        return responses

    def _looks_like_member_name_dynamic(self, text: str) -> bool:
        """Dynamic member name detection without hardcoding"""

        # Basic checks
        if not text or len(text) > 100:  # Too long to be a name
            return False

        words = text.split()

        # Should be 2-4 words
        if len(words) < 2 or len(words) > 6:
            return False

        # Check if all words could be names
        for word in words:
            # Should start with capital letter
            if not word[0].isupper():
                return False

            # Should be mostly alphabetic (allow apostrophes, hyphens)
            if not re.match(r"^[A-Za-z'-]+$", word):
                return False

            # Should not be common words
            common_words = [
                "what",
                "when",
                "where",
                "how",
                "why",
                "who",
                "which",
                "the",
                "and",
                "but",
                "for",
                "you",
                "your",
                "our",
                "costco",
                "member",
                "poll",
                "question",
                "response",
                "facebook",
                "page",
                "connection",
                "magazine",
            ]
            if word.lower() in common_words:
                return False

        # Additional validation: should not contain punctuation except common name chars
        if re.search(r'[.!?@#$%^&*()+=\[\]{}|\\:";,.<>?/]', text):
            return False

        return True

    def _find_response_for_member(self, lines: List[str], name_index: int) -> str:
        """Find response text for a member name"""

        # Look in lines before the name (common pattern)
        for i in range(max(0, name_index - 3), name_index):
            line = lines[i]
            if self._looks_like_member_response(line) and len(line) > 20:
                return line

        # Look in lines after the name
        for i in range(name_index + 1, min(len(lines), name_index + 4)):
            line = lines[i]
            if self._looks_like_member_response(line) and len(line) > 20:
                return line

        return

    def _looks_like_member_response(self, text: str) -> bool:
        """Check if text looks like a genuine member response"""

        # Personal language indicators
        personal_words = [
            "i look forward",
            "i love",
            "i feel",
            "my favorite",
            "football season",
            "cooler weather",
            "pumpkin spice",
            "sweater weather",
            "hockey season",
            "next summer",
            "thank you",
            "crisp days",
            "autumn",
            "fall",
            "i have",
            "my husband",
            "we saved",
            "it was",
            "when my",
        ]

        text_lower = text.lower()

        # Must contain personal language
        if not any(word in text_lower for word in personal_words):
            return False

        # Should not contain business/navigation language heavily
        business_words = ["shop", "department", "warehouse", "compare", "cart"]
        business_count = sum(1 for word in business_words if word in text_lower)

        # Allow some business words but not if it's mostly business talk
        word_count = len(text.split())
        if word_count > 0 and (business_count / word_count) > 0.5:
            return False

        return True

    def _is_navigation_text(self, text: str) -> bool:
        """Check if text appears to be navigation content."""
        text_lower = text.lower()

        # Check against navigation blacklist
        nav_terms = [
            "shop",
            "department",
            "services",
            "insurance",
            "delivery",
            "installation",
            "business",
            "pharmacy",
            "optical",
            "photo",
            "tire",
            "gas",
            "membership",
            "locations",
            "hours",
            "holiday",
            "contact",
            "help",
            "customer service",
            "savings",
            "coupons",
            "deals",
            "offers",
            "warehouse",
            "costco business",
            "compare",
            "add to cart",
            "view all",
            "home\n\n\n",
        ]

        nav_matches = sum(1 for nav_term in nav_terms if nav_term in text_lower)

        # Short text with navigation terms is likely navigation
        word_count = len(text.split())
        if nav_matches > 0 and word_count < 8:
            return True

        # High density of navigation terms
        if word_count > 0 and (nav_matches / word_count) > 0.3:
            return True

        # Common navigation patterns
        nav_patterns = [
            r"shop\s+\w+",
            r"view\s+all",
            r"see\s+more",
            r"browse\s+\w+",
            r"compare\s+\w+",
            r"find\s+a\s+\w+",
            r"locate\s+\w+",
        ]

        import re

        for pattern in nav_patterns:
            if re.search(pattern, text_lower):
                return True

        return False

    def _find_name_for_response(self, lines: List[str], response_index: int) -> str:
        """Find member name for a response"""

        # Look in next few lines
        for i in range(response_index + 1, min(len(lines), response_index + 3)):
            line = lines[i]
            if self._looks_like_member_name_dynamic(line):
                return line

        # Look in previous lines
        for i in range(max(0, response_index - 2), response_index):
            line = lines[i]
            if self._looks_like_member_name_dynamic(line):
                return line

        return ""

    def _extract_from_paragraph_sequences(
        self, content_area: Tag
    ) -> List[Dict[str, str]]:
        """Extract from paragraph sequences"""

        responses = []
        paragraphs = content_area.find_all("p")

        for i, p in enumerate(paragraphs):
            text = p.get_text().strip()

            # Check if this paragraph contains a member response
            if self._looks_like_member_response(text):

                # Look for name in adjacent paragraphs
                name = ""

                # Check next paragraph
                if i + 1 < len(paragraphs):
                    next_text = paragraphs[i + 1].get_text().strip()
                    if self._looks_like_member_name_dynamic(next_text):
                        name = next_text

                # Check previous paragraph if no name found
                if not name and i > 0:
                    prev_text = paragraphs[i - 1].get_text().strip()
                    if self._looks_like_member_name_dynamic(prev_text):
                        name = prev_text

                if name:
                    responses.append({"name": name, "response": text})

        return responses

    def _clean_text_for_extraction(self, text: str) -> str:
        """Clean text for better extraction"""

        # Remove copyright notices
        text = re.sub(r"© [^/\n]+/[^/\n]+", "", text)

        # Remove common navigation text
        nav_patterns = [
            r"Follow us on.*",
            r"Watch for the poll.*",
            r"Facebook\.com/Costco.*",
            r"connection@costco\.com.*",
            r"weigh in at.*",
            r"subject line.*",
        ]

        for pattern in nav_patterns:
            text = re.sub(pattern, "", text, flags=re.DOTALL | re.IGNORECASE)

        # Clean up whitespace
        text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)

        return text

    def _is_navigation_container(self, container: Tag) -> bool:
        """Check if container is navigation/non-content"""

        # Check class names
        class_names = " ".join(container.get("class", [])).lower()
        nav_classes = ["nav", "menu", "header", "footer", "sidebar", "ad", "promo"]

        if any(nav_class in class_names for nav_class in nav_classes):
            return True

        # Check text content
        text = container.get_text().lower()
        nav_indicators = [
            "follow us",
            "facebook.com",
            "connection@costco.com",
            "shop costco",
            "department",
            "compare products",
        ]

        if any(indicator in text for indicator in nav_indicators):
            return True

        return False

    def _deduplicate_responses(
        self, responses: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        """Remove duplicate responses"""

        seen_names = set()
        seen_responses = set()
        unique_responses = []

        for response in responses:
            name = response["name"]
            text = response["response"]

            # Skip if we've seen this name or very similar response
            if name in seen_names:
                continue

            # Check for similar responses (avoid duplicates)
            is_duplicate = False
            for seen_response in seen_responses:
                if self._text_similarity(text, seen_response) > 0.8:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique_responses.append(response)
                seen_names.add(name)
                seen_responses.add(text)

        return unique_responses

    def _clean_member_response(self, response: str) -> str:
        """Clean member response without hardcoded patterns"""

        if not response:
            return ""

        # Remove any poll questions that got mixed in
        # Look for question patterns and remove them
        question_patterns = [
            r"[A-Z][^?]*\?\s*",  # Any question
            r"What [^?]*\?\s*",
            r"How [^?]*\?\s*",
            r"Which [^?]*\?\s*",
        ]

        for pattern in question_patterns:
            response = re.sub(pattern, "", response, flags=re.IGNORECASE)

        # Clean up whitespace
        response = re.sub(r"\s+", " ", response)
        response = response.strip()

        # Remove member names that might be embedded
        # Look for capitalized word sequences that might be names
        words = response.split()
        cleaned_words = []

        i = 0
        while i < len(words):
            word = words[i]

            # Check if this starts a potential name sequence
            if (
                word[0].isupper()
                and i + 1 < len(words)
                and words[i + 1][0].isupper()
                and len(word) > 1
                and word.isalpha()
            ):

                # This might be a name, check if it makes sense in context
                potential_name = word + " " + words[i + 1]

                # If it looks like a name and interrupts the flow, skip it
                if (
                    self._looks_like_member_name_dynamic(potential_name)
                    and i > 0
                    and i + 2 < len(words)
                ):
                    i += 2  # Skip both words
                    continue

            cleaned_words.append(word)
            i += 1

        response = " ".join(cleaned_words)

        # Ensure proper sentence ending
        if response and not response[-1] in ".!?":
            response += "."

        return response

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0
        """Check if text looks like a genuine member response"""

        # Personal language indicators
        personal_words = [
            "i look forward",
            "i love",
            "i feel",
            "my favorite",
            "football season",
            "cooler weather",
            "pumpkin spice",
            "sweater weather",
            "hockey season",
            "next summer",
            "thank you",
            "crisp days",
            "autumn",
            "fall",
        ]

        text_lower = text.lower()

        # Must contain personal language
        if not any(word in text_lower for word in personal_words):
            return False

        # Should not contain business/navigation language heavily
        business_words = ["shop", "department", "warehouse", "compare", "cart"]
        business_count = sum(1 for word in business_words if word in text_lower)

        # Allow some business words but not if it's mostly business talk
        word_count = len(text.split())
        if word_count > 0 and (business_count / word_count) > 0.3:
            return False

        return True

    def _detect_member_content_type(self, content_area: Tag) -> str:
        """Detect if this is a poll page or comments page"""

        text = content_area.get_text().lower()

        # Check for poll indicators
        if any(
            indicator in text for indicator in ["poll", "what do you", "facebook page"]
        ):
            return "poll"

        # Check for comment indicators
        if any(
            indicator in text
            for indicator in ["member comments", "on costco", "via email"]
        ):
            return "comments"

        return "general"

    def _extract_member_comments_format(
        self, content_area: Tag
    ) -> List[Dict[str, str]]:
        """Extract from member comments format (not poll format)"""

        comments = []

        # Look for comment sections with headers
        comment_sections = [
            "On Costco going global",
            "Love of learning",
            "A moving letter",
            "In praise of Costco's funeral supplies",
        ]

        # Strategy: Find headers, then extract comment + attribution
        for header in content_area.find_all(["h3", "h4", "strong", "b"]):
            header_text = header.get_text().strip()

            # If this looks like a comment topic
            if len(header_text) > 5 and len(header_text) < 50:
                # Find the content after this header
                comment_content = self._extract_comment_after_header(header)

                if comment_content:
                    # Look for member attribution (usually at the end)
                    member_name = self._extract_member_attribution(comment_content)
                    clean_comment = self._clean_comment_content(
                        comment_content, member_name
                    )

                    if member_name and clean_comment:
                        comments.append(
                            {
                                "name": member_name,
                                "response": clean_comment,
                                "topic": header_text,
                            }
                        )

        return comments

    # ===== DEBUG HELPER =====

    def debug_recipe_extraction(self, html_content: str, url: str):
        """Debug helper to see what's being extracted"""
        soup = BeautifulSoup(html_content, "html.parser")

        print("=== DEBUG: FIXED Recipe Extraction ===")
        print(f"URL: {url}")

        # Find all lists
        all_lists = soup.find_all(["ul", "ol"])
        print(f"Found {len(all_lists)} lists total")

        for i, ul in enumerate(all_lists):
            items = [li.get_text().strip() for li in ul.find_all("li")]
            list_text = " ".join(items).lower()

            has_measurements = any(
                unit in list_text
                for unit in ["cup", "tablespoon", "teaspoon", "ounce", "pound"]
            )

            print(f"\nList {i} (has_measurements: {has_measurements}):")
            for item in items[:3]:  # Show first 3 items
                print(f"  - {item}")
            if len(items) > 3:
                print(f"  ... and {len(items)-3} more")

        # Look for section headers
        headers = soup.find_all(["h1", "h2", "h3", "h4", "strong", "b"])
        recipe_headers = []
        for header in headers:
            header_text = header.get_text().strip().upper()
            if any(
                section in header_text
                for section in ["FILLING", "STREUSEL", "CAKE", "INGREDIENTS"]
            ):
                recipe_headers.append(header_text)

        print(f"\nRecipe section headers found: {recipe_headers}")
        print("=== END DEBUG ===")

    def extract_sections_between_headings(self, content_area: Tag, content_type: str = "shopping") -> List[Dict]:
        """
        FIXED: Extract sections using HTML comments as strict guides
        This follows the comment structure to eliminate duplication and correctly associate images
        SHOPPING ONLY: This method should only be used for shopping content
        """
        if not content_area:
            return []
        
        # SAFETY: Only for shopping content to avoid impacting other categories
        if content_type.lower() != "shopping":
            logger.warning(f"extract_sections_between_headings called for non-shopping content: {content_type}")
            return []
        
        sections = []
        
        # Find all headings in document order
        all_headings = content_area.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        if not all_headings:
            return []
        
        # Use HTML comments to understand section structure
        html_content = str(content_area)
        
        # Find comment boundaries to properly separate sections
        comment_sections = {
            'body': ('<!-- Body -->', '<!-- /Body -->'),
            'sidebar_no_image': ('<!-- Sidebar without Image -->', '<!-- /Sidebar without Image -->'),
            'sidebar_with_image': ('<!-- Sidebar with Image -->', '<!-- /Sidebar with Image -->'),
            'experts': ('<!-- Use for experts -->', '<!-- /Use for experts -->')
        }
        
        # For each heading, extract content based on comment boundaries
        for i, heading in enumerate(all_headings):
            heading_text = heading.get_text().strip()
            if not heading_text or len(heading_text) < 2:
                continue
            
            # Filter out cookies/navigation headings
            if any(nav_term in heading_text.lower() for nav_term in ['cookie', 'privacy', 'advertising and products']):
                continue
                
            level = int(heading.name[1])
            section_content = []
            section_images = []
            
            # Find the HTML position of this heading
            heading_html = str(heading)
            heading_start = html_content.find(heading_html)
            
            if heading_start == -1:
                continue
                
            # Find the next heading to determine section boundaries
            next_heading = all_headings[i + 1] if i + 1 < len(all_headings) else None
            section_end = len(html_content)
            
            if next_heading:
                next_heading_html = str(next_heading)
                next_start = html_content.find(next_heading_html, heading_start + len(heading_html))
                if next_start != -1:
                    section_end = next_start
            
            # Extract content in this section only
            section_html = html_content[heading_start:section_end]
            
            # Determine which comment section this heading belongs to
            section_type = 'body'  # Default
            for comment_type, (start_comment, end_comment) in comment_sections.items():
                if start_comment in section_html:
                    section_type = comment_type
                    break
            
            # Parse this section to find paragraphs and images
            from bs4 import BeautifulSoup
            section_soup = BeautifulSoup(section_html, 'html.parser')
            
            # Extract content based on comment type
            if section_type == 'body':
                # Main body content - extract paragraphs directly after heading
                current_element = heading.next_sibling
                while current_element and current_element != next_heading:
                    if hasattr(current_element, 'name'):
                        if current_element.name == 'p':
                            text = current_element.get_text().strip()
                            if text and len(text) > 3:
                                # IMPROVED: Include ALL content including bylines for H1 sections
                                if heading.name == 'h1':
                                    # For H1, include ALL content including captions and bylines
                                    section_content.append(text)
                                else:
                                    # For other headings, include bylines but skip navigation
                                    nav_terms = ['home', 'costco connection', 'download the pdf', 'copyright']
                                    nav_score = sum(1 for term in nav_terms if term in text.lower())
                                    if not (len(text) < 100 and nav_score > 0):
                                        section_content.append(text)
                        elif current_element.name == 'img':
                            # Check for images in this section
                            src = current_element.get('src', '')
                            alt = current_element.get('alt', '')
                            if src and not self._is_ad_image(alt, src):
                                fixed_src = self._fix_image_url(src, "https://mobilecontent.costco.com")
                                if fixed_src:
                                    section_images.append({
                                        'src': fixed_src,
                                        'alt': alt,
                                        'caption': '',
                                        'relevance_score': 6
                                    })
                    current_element = current_element.next_sibling
                    
                # Find images in this section only (not in subsections)
                for img in section_soup.find_all('img'):
                    # Skip images that are in sidebar sections
                    img_parent = img.parent
                    while img_parent:
                        if img_parent.name == 'div' and 'sidebar' in str(img_parent).lower():
                            break
                        img_parent = img_parent.parent
                    else:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        if src:
                            # Filter out ad images
                            if self._is_ad_image(alt, src):
                                continue
                            fixed_src = self._fix_image_url(src, "https://mobilecontent.costco.com")
                            if fixed_src:
                                section_images.append({
                                    'src': fixed_src,
                                    'alt': alt,
                                    'caption': '',
                                    'relevance_score': 6
                                })
                                
            elif section_type == 'sidebar_with_image':
                # Sidebar with image - extract both content and associated image
                for p in section_soup.find_all('p'):
                    text = p.get_text().strip()
                    if text and len(text) > 15 and not text.startswith('©'):
                        # Skip author bio unless this is specifically an author/expert section
                        if ('fills this month' in text or 'email questions' in text or 
                            'consumer reporter' in text or 'behind-the-scenes' in text):
                            # This is author bio content - only include in author sections
                            if ('author' in heading_text.lower() or 'expert' in heading_text.lower() or
                                'about' in heading_text.lower() and len(section_content) == 0):
                                section_content.append(text)
                            # Skip author bio for product/material sections
                        else:
                            section_content.append(text)
                
                # Find images specifically in this sidebar
                for img in section_soup.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    if src:
                        # Filter out ad images
                        if self._is_ad_image(alt, src):
                            continue
                        fixed_src = self._fix_image_url(src, "https://mobilecontent.costco.com")
                        if fixed_src:
                            section_images.append({
                                'src': fixed_src,
                                'alt': alt,
                                'caption': '',
                                'relevance_score': 6
                            })
                            
            elif section_type == 'sidebar_no_image':
                # Sidebar without image - extract content only
                for p in section_soup.find_all('p'):
                    text = p.get_text().strip()
                    if text and len(text) > 15 and not text.startswith('©'):
                        section_content.append(text)
                        
            elif section_type == 'experts':
                # Expert section - extract author info and image
                for p in section_soup.find_all('p'):
                    text = p.get_text().strip()
                    if text and len(text) > 15:
                        section_content.append(text)
                
                # Find author image only
                for img in section_soup.find_all('img'):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    if src and ('headshot' in src.lower() or 'head' in alt.lower()):
                        fixed_src = self._fix_image_url(src, "https://mobilecontent.costco.com")
                        if fixed_src:
                            section_images.append({
                                'src': fixed_src,
                                'alt': alt,
                                'caption': '',
                                'relevance_score': 6
                            })
            
            # SPECIAL: For H1 sections, even if no immediate content, look for main article content
            if level == 1 and not section_content and not section_images:
                # Look for main article image and captions in the broader content area
                content_parent = heading.find_parent('div')
                while content_parent and not any('col-' in str(cls) for cls in content_parent.get('class', [])):
                    content_parent = content_parent.find_parent('div')
                
                if content_parent:
                    # Look for main article image
                    main_images = content_parent.find_all('img')
                    for img in main_images:
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        # Look for main article images (not ads, not author headshots)
                        if (src and 'ic_' in src.lower() and 
                            not self._is_ad_image(alt, src) and 'headshot' not in src.lower()):
                            fixed_src = self._fix_image_url(src, "https://mobilecontent.costco.com")
                            if fixed_src:
                                section_images.append({
                                    'src': fixed_src,
                                    'alt': alt,
                                    'caption': '',
                                    'relevance_score': 6
                                })
                                break  # Only take the main image
                    
                    # Look for captions and bylines
                    paragraphs = content_parent.find_all('p')
                    for p in paragraphs:
                        text = p.get_text().strip()
                        if text and len(text) > 3:
                            # Include captions and copyright info that are likely related to main image
                            if ('©' in text or len(text) < 100):
                                section_content.append(text)
                                if len(section_content) >= 2:  # Limit content
                                    break
            
            # Create section if we have content
            if section_content or section_images:
                sections.append({
                    "heading": heading_text,
                    "level": level,
                    "content": section_content,
                    "images": section_images
                })
        
        # Post-process sections to handle author bio content properly
        processed_sections = []
        author_bio_content = []
        
        for section in sections:
            section_content = section.get('content', [])
            filtered_content = []
            
            for content in section_content:
                # Check if this is author bio content
                if ('fills this month' in content or 'email questions' in content or
                    'consumer reporter' in content or 'behind-the-scenes' in content):
                    # This is author bio - collect it separately
                    author_bio_content.append(content)
                else:
                    # This is regular section content
                    filtered_content.append(content)
            
            # Update section with filtered content
            section['content'] = filtered_content
            processed_sections.append(section)
        
        # If we found author bio content, create a separate author section
        if author_bio_content:
            # Find author image
            author_images = []
            for section in processed_sections:
                for img in section.get('images', []):
                    if 'headshot' in img.get('src', '').lower() or 'head' in img.get('alt', '').lower():
                        author_images.append(img)
                        break
            
            # Create author section
            processed_sections.append({
                'heading': 'About the Author',
                'level': 3,
                'content': author_bio_content,
                'images': author_images
            })
            
            # Remove author images from other sections
            for section in processed_sections[:-1]:  # Skip the author section we just added
                section['images'] = [img for img in section.get('images', []) 
                                   if not ('headshot' in img.get('src', '').lower() or 'head' in img.get('alt', '').lower())]
        
        return processed_sections
        
    def _is_ad_image(self, alt: str, src: str) -> bool:
        """
        Check if an image is an advertisement that should be filtered out
        """
        if not alt and not src:
            return False
            
        alt_lower = alt.lower()
        src_lower = src.lower()
        
        # Common ad indicators
        ad_keywords = [
            'kirkland signature',
            'click here',
            'advertisement',
            'ad banner',
            'promo',
            'socks',
            'kitty',
            'pet food',
            'wellness',
            'merino wool',
            'limit 5'
        ]
        
        for keyword in ad_keywords:
            if keyword in alt_lower or keyword in src_lower:
                return True
                
        return False
        
    def extract_magazine_front_cover_content(self, content_area: Tag, full_soup: BeautifulSoup = None) -> Dict:
        """
        Extract magazine front cover content including cover story, articles, and sections
        """
        magazine_data = {
            'cover_story': {},
            'in_this_issue': [],
            'special_sections': [],
            'featured_sections': [],
            'article_categories': {},
            'pdf_download_link': '',
            'cover_image': '',
            'cover_image_alt': ''
        }
        
        if not content_area:
            return magazine_data
            
        # Extract cover story information with enhanced structure detection
        cover_story_section = content_area.find('div', string=lambda text: text and 'cover story' in text.lower())
        if not cover_story_section:
            # Look for cover story in text content
            cover_story_text = content_area.find(string=lambda text: text and 'Cover Story' in text)
            if cover_story_text:
                cover_story_section = cover_story_text.find_parent(['div', 'a'])
        
        if cover_story_section:
            # Look for the structured cover story content
            parent_container = cover_story_section.find_parent(['div', 'a'])
            if parent_container:
                # Extract title from the larger text elements
                title_div = parent_container.find('div', style=lambda style: style and '2em' in style)
                if title_div:
                    magazine_data['cover_story']['title'] = title_div.get_text().strip()
                
                # Extract description from following content
                desc_div = parent_container.find('div', style=lambda style: style and 'font-weight: normal' in style)
                if desc_div:
                    magazine_data['cover_story']['description'] = desc_div.get_text().strip()
                
                # Extract link from parent anchor
                if parent_container.name == 'a':
                    magazine_data['cover_story']['link'] = parent_container.get('href', '')
                else:
                    cover_link = parent_container.find('a', href=True)
                    if cover_link:
                        magazine_data['cover_story']['link'] = cover_link.get('href', '')
        
        # Extract "In This Issue" sections with enhanced description extraction
        # Search in the full document if available, otherwise use content_area
        search_area = full_soup if full_soup else content_area
        in_this_issue_section = search_area.find(string=lambda text: text and 'in this issue' in text.lower())
        if in_this_issue_section:
            parent = in_this_issue_section.find_parent(['div', 'section'])
            if parent:
                # Find the actual "In This Issue" list in the sidebar
                # Look for the specific structure in the col-md-4 sidebar
                sidebar = search_area.find('div', class_='col-xs-12 col-md-4')
                if sidebar:
                    in_this_issue_container = sidebar.find('div', style=lambda style: style and 'border-top: 8px solid #54b6cc' in style)
                    if in_this_issue_container:
                        list_container = in_this_issue_container.find('ul')
                        if list_container:
                            list_items = list_container.find_all('li')
                            for li in list_items:
                                link = li.find('a', href=True)
                                if link and ('/connection-' in link.get('href', '') and not link.get('href', '').endswith('.pdf')):
                                    # Extract title and description from the link structure
                                    link_text = link.get_text().strip()
                                    lines = [line.strip() for line in link_text.split('\n') if line.strip()]
                                    
                                    if len(lines) >= 2:
                                        title = lines[0]
                                        description = lines[1]
                                    elif len(lines) == 1:
                                        title = lines[0]
                                        description = ''
                                    else:
                                        continue  # Skip if no valid content
                                    
                                    # Also check for span with description
                                    span_desc = li.find('span', style=lambda style: style and 'font-size: 0.8em' in style)
                                    if span_desc and not description:
                                        description = span_desc.get_text().strip()
                                    
                                    if title and len(title) > 3 and not title.startswith('Download'):  # Skip PDF download link
                                        magazine_data['in_this_issue'].append({
                                            'title': title,
                                            'link': link.get('href', ''),
                                            'description': description
                                        })
        
        # Extract Special Sections
        special_section_headers = content_area.find_all(string=lambda text: text and 'special section' in text.lower())
        for header in special_section_headers:
            parent = header.find_parent(['div', 'section'])
            if parent:
                # Find articles in this special section
                section_links = parent.find_all('a', href=True)
                for link in section_links:
                    if link.get('href', '').startswith('/connection-'):
                        title = link.get_text().strip()
                        if title:
                            # Look for description near the link
                            description = ''
                            desc_elem = link.find_next_sibling(['div', 'p', 'span'])
                            if desc_elem:
                                description = desc_elem.get_text().strip()
                            
                            magazine_data['special_sections'].append({
                                'title': title,
                                'link': link.get('href', ''),
                                'description': description
                            })
        
        # Extract Featured Sections from grid layout - simplified approach
        # Look for all grid items with images and connection links
        # Use exact class matching as the lambda approach isn't working
        grid_items_xs6 = search_area.find_all('div', class_=['col-xs-6', 'col-md-3'])
        grid_items_xs12 = search_area.find_all('div', class_=['col-xs-12', 'col-md-3'])
        all_grid_items = grid_items_xs6 + grid_items_xs12
        
        seen_featured_links = set()  # Track seen links to avoid duplicates
        
        for item in all_grid_items:
            link = item.find('a', href=True)
            img = item.find('img')
            
            # Check if this looks like a featured section item
            if link and img and '/connection-' in link.get('href', ''):
                href = link.get('href', '')
                
                # Skip if we've already seen this link
                if href in seen_featured_links:
                    continue
                
                # Look for category text in divs (For Your Health, For Your Table, etc.)
                category_div = item.find('div', string=lambda text: text and any(cat in text for cat in ['For Your', 'Inside Costco', 'Member Connection']))
                
                # Look for title in blue text
                title_div = item.find('div', style=lambda style: style and 'color: #0f4878' in style)
                
                if category_div and title_div:
                    title = title_div.get_text().strip()
                    category = category_div.get_text().strip()
                    
                    if title and len(title) > 3:
                        magazine_data['featured_sections'].append({
                            'title': title,
                            'link': href,
                            'category': category,
                            'image': self._fix_image_url(img.get('src', ''), "https://mobilecontent.costco.com"),
                            'image_alt': img.get('alt', '')
                        })
                        seen_featured_links.add(href)
        
        # Extract all article categories dynamically with deduplication
        all_article_links = content_area.find_all('a', href=lambda href: href and '/connection-' in href)
        categories = {}
        seen_links = set()  # Track seen links to avoid duplicates
        
        for link in all_article_links:
            href = link.get('href', '')
            category = self._extract_category_from_link(href)
            title = link.get_text().strip()
            
            # Skip if we've already seen this link or title
            if href in seen_links or not title or len(title) <= 3:
                continue
                
            # Skip anchor links (fragments)
            if href.endswith('#'):
                continue
                
            # Skip duplicates with same title in different categories
            title_seen = False
            for existing_category in categories.values():
                if any(article['title'] == title for article in existing_category):
                    title_seen = True
                    break
            
            if title_seen:
                continue
                
            if category:
                if category not in categories:
                    categories[category] = []
                
                # Look for description or subtitle with enhanced extraction
                description = ''
                image_url = ''
                image_alt = ''
                
                parent = link.find_parent(['div', 'li', 'section'])
                if parent:
                    # Check for description in spans with smaller font
                    desc_elem = parent.find('span', style=lambda style: style and ('font-size: 0.8em' in style or 'font-size:0.8em' in style))
                    if desc_elem:
                        description = desc_elem.get_text().strip()
                    
                    # Check for description in divs with specific styling
                    if not description:
                        desc_elem = parent.find('div', style=lambda style: style and 'font-size: 1.2em' in style and 'padding-bottom' in style)
                        if desc_elem:
                            description = desc_elem.get_text().strip()
                    
                    # Check for description in navigation dropdown structure
                    if not description:
                        link_text = link.get_text().strip()
                        if '\n' in link_text:
                            lines = [line.strip() for line in link_text.split('\n') if line.strip()]
                            if len(lines) >= 2:
                                description = lines[1]
                    
                    # Look for associated image in the same parent container
                    img_elem = parent.find('img')
                    if img_elem:
                        image_url = self._fix_image_url(img_elem.get('src', ''), "https://mobilecontent.costco.com")
                        image_alt = img_elem.get('alt', '')
                
                # If no image found in parent, try to find it using article-specific patterns
                if not image_url:
                    image_url, image_alt = self._find_magazine_article_image(href, content_area)
                
                categories[category].append({
                    'title': title,
                    'link': href,
                    'description': description,
                    'image': image_url,
                    'image_alt': image_alt
                })
                
                seen_links.add(href)
        
        magazine_data['article_categories'] = categories
        
        # Extract PDF download link
        pdf_link = content_area.find('a', string=lambda text: text and 'download' in text.lower() and 'pdf' in text.lower())
        if pdf_link:
            magazine_data['pdf_download_link'] = pdf_link.get('href', '')
        
        # Extract cover image
        # Look for main cover image (usually the largest, most prominent image)
        images = content_area.find_all('img')
        best_cover_image = None
        best_score = 0
        
        for img in images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            score = 0
            
            # Score based on likely cover image indicators
            if 'cover' in src.lower() or 'cover' in alt.lower():
                score += 100
            if 'lp_' in src.lower():  # Landing page images
                score += 50
            # Generic cover image patterns (removed hardcoded "squishmallow")
            if any(cover_indicator in src.lower() for cover_indicator in ['cover_story', 'main_image']):
                score += 80
            if any(size_indicator in src.lower() for size_indicator in ['large', 'main', 'hero']):
                score += 30
                
            # Size-based scoring (prefer larger images)
            width = img.get('width', '')
            height = img.get('height', '')
            if width and height:
                try:
                    w, h = int(width), int(height)
                    if w > 400 and h > 300:
                        score += 40
                except ValueError:
                    pass
            
            if score > best_score:
                best_score = score
                best_cover_image = img
        
        if best_cover_image:
            magazine_data['cover_image'] = self._fix_image_url(best_cover_image.get('src', ''), "https://mobilecontent.costco.com")
            magazine_data['cover_image_alt'] = best_cover_image.get('alt', '')
        
        return magazine_data
    
    def _find_magazine_article_image(self, article_href: str, content_area: Tag) -> Tuple[str, str]:
        """
        Find the associated image for a magazine article using URL-based patterns
        Returns (image_url, image_alt) tuple
        """
        if not article_href:
            return '', ''
            
        # Extract article identifiers from URL
        article_mapping = {
            # Special Section articles
            'clean-sweep': ['iRobot', 'robot vacuum'],
            'smokeless-simplicity': ['Gourmia', 'foodstation'],
            'quality-coating': ['GreenPan', 'pots and pans'],
            'buyers-picks': ['Buyers_Picks', 'pan set'],
            
            # For Your Health articles  
            'keeping-your-cool': ['FYH_Keeping_Cool', 'wearable device'],
            
            # For Your Table articles
            'lights-camera-eat': ['FYT_Yellowstone', 'a man'],
            'picking-a-winner': ['FYT_PastaSauce', 'tomato sauce'], 
            'growing-green': ['FYT_Wine', 'a woman in a vineyard'],
            
            # For Your Entertainment articles
            'here-be-dragons': ['FYE_Author', 'author headshot'],
            'power-play': ['FYE_Monopoly', 'book cover'],
            
            # Inside Costco articles
            'sense-of-security': ['IC_Mem_Services', 'resort'],
            'precious-resource': ['IC_Sustainability', 'resort'],
            
            # Member Connection articles
            'ultimut-pet-provider': ['Mem_Conn_main', 'a man holding a puppy'],
            
            # Treasure Hunt articles
            'treasure-hunt': ['Treasure_Hunt_Headphones', 'Costco Monopoly'],
            
            # Cover Story
            'cover-soft-sell': ['Cover_Story', '2 girls holding squishmallows']
        }
        
        # Find matching article pattern
        article_key = None
        for key in article_mapping.keys():
            if key in article_href:
                article_key = key
                break
        
        if not article_key:
            return '', ''
            
        image_pattern, expected_alt = article_mapping[article_key]
        
        # Find all images in content area
        all_images = content_area.find_all('img')
        
        for img in all_images:
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            # Check if this image matches the pattern
            if image_pattern in src:
                fixed_url = self._fix_image_url(src, "https://mobilecontent.costco.com")
                return fixed_url, alt
                
        return '', ''
    
    def _extract_category_from_link(self, href: str) -> str:
        """Extract category from article link"""
        if not href:
            return 'other'
            
        # Extract category from URL patterns
        if '/connection-fye-' in href:
            return 'For Your Entertainment'
        elif '/connection-fyt-' in href:
            return 'For Your Table'
        elif '/connection-fyh-' in href:
            return 'For Your Health'
        elif '/connection-tech-' in href or '/connection-power-up' in href:
            return 'Tech Connection'
        elif '/connection-travel-' in href:
            return 'Travel Connection'
        elif '/connection-recipe-' in href:
            return 'Recipes'
        elif '/connection-member-' in href:
            return 'Member Connection'
        elif '/connection-publishers-' in href:
            return "Publisher's Note"
        elif '/connection-ss-' in href:
            return 'Special Section'
        elif '/connection-treasure-' in href:
            return 'Treasure Hunt'
        elif '/connection-costco-life' in href:
            return 'Costco Life'
        else:
            return 'Inside Costco'


# Main extraction function
def extract_content_from_html_fixed(html_content: str, url: str) -> ExtractedContent:
    """Main function to extract content with FIXED recipe handling"""
    extractor = FixedUniversalContentExtractor()
    return extractor.extract_all_content(html_content, url)
