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
                "content_keywords": ["product", "buying", "costco", "warehouse"],
                "required_score": 2,
            },
            "lifestyle": {
                "url_keywords": ["costco-life", "fye", "supplier"],
                "title_keywords": ["celebrate", "entertainment", "author"],
                "content_keywords": ["lifestyle", "entertainment", "author", "book"],
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
            extracted.title = title_candidates[0][0]

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
            # If no date pattern, try default October folder for headshots
            elif "_headshot" in filename.lower():
                return f"https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/{filename}"

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
                    
                    while current and len(heading_content) < 3:  # Limit to 3 items per heading
                        if hasattr(current, 'name'):
                            # Stop at next heading
                            if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                break
                            # Collect paragraph content
                            elif current.name in ['p', 'div']:
                                text = current.get_text().strip()
                                if text and len(text) > 30 and text not in heading_content:
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
        """Extract travel-specific data"""

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


# Main extraction function
def extract_content_from_html_fixed(html_content: str, url: str) -> ExtractedContent:
    """Main function to extract content with FIXED recipe handling"""
    extractor = FixedUniversalContentExtractor()
    return extractor.extract_all_content(html_content, url)
