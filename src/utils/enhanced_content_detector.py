"""
FIXED: Enhanced content type detection for Costco Connection articles.
Improved to avoid extracting cookie popups, navigation content and focus on actual recipe/article content.
"""

import re
import logging
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup

from ..models.content_schemas import (
    ContentType, BaseContent, RecipeContent, TravelContent, TechContent,
    LifestyleContent, EditorialContent, ShoppingContent, MemberContent
)

logger = logging.getLogger(__name__)


class EnhancedContentDetector:
    """Enhanced content type detection with schema-aware extraction."""
    
    def __init__(self):
        self.content_patterns = {
            ContentType.RECIPE: {
                'url_patterns': ['recipe', 'food', 'cooking', 'kitchen'],
                'keywords': ['ingredients', 'directions', 'recipe', 'cooking', 'prep time', 'servings', 'cook', 'bake', 'tablespoon', 'cup', 'ounces'],
                'selectors': ['ingredients', 'recipe-instructions', 'directions', 'nutrition'],
                'byline': 'By Costco Kitchen Team'
            },
            ContentType.TRAVEL: {
                'url_patterns': ['travel', 'destination', 'vacation', 'cities'],
                'keywords': ['travel', 'destination', 'vacation', 'city', 'attractions', 'hotel', 'restaurant', 'sightseeing', 'culture', 'visit'],
                'selectors': ['travel-info', 'destination', 'attractions'],
                'byline': 'By Costco Travel'
            },
            ContentType.TECH: {
                'url_patterns': ['tech', 'power-up', 'technology', 'gadget', 'electronics'],
                'keywords': ['technology', 'tech', 'gadget', 'electronics', 'digital', 'smart', 'device', 'features', 'specifications'],
                'selectors': ['tech-specs', 'features', 'product-info'],
                'byline': 'By Tech Connection'
            },
            ContentType.LIFESTYLE: {
                'url_patterns': ['costco-life', 'lifestyle', 'family', 'wellness', 'pets', 'home'],
                'keywords': ['family', 'lifestyle', 'wellness', 'health', 'home', 'pets', 'life', 'celebrate', 'living'],
                'selectors': ['lifestyle-content', 'family-info'],
                'byline': 'By Costco Connection'
            },
            ContentType.EDITORIAL: {
                'url_patterns': ['publishers-note', 'editorial', 'opinion', 'note', 'front-cover'],
                'keywords': ['publisher', 'editorial', 'opinion', 'note', 'message', 'costco values', 'members'],
                'selectors': ['editorial', 'publishers-note'],
                'byline': 'By Costco Connection Editorial'
            },
            ContentType.SHOPPING: {
                'url_patterns': ['buying-smart', 'treasure-hunt', 'product', 'deals', 'shopping'],
                'keywords': ['product', 'buying', 'shopping', 'deals', 'kirkland', 'warehouse', 'merchandise'],
                'selectors': ['product-info', 'buying-guide'],
                'byline': 'By Costco Buying Team'
            },
            ContentType.MEMBER: {
                'url_patterns': ['member', 'poll', 'comments', 'community'],
                'keywords': ['member', 'poll', 'survey', 'comments', 'community', 'members respond'],
                'selectors': ['member-content', 'poll-results'],
                'byline': 'By Member Services'
            }
        }
        
        # Navigation terms to avoid
        self.navigation_blacklist = [
            'shop', 'department', 'services', 'insurance', 'delivery', 'installation',
            'business', 'pharmacy', 'optical', 'photo', 'tire', 'gas', 'membership',
            'locations', 'hours', 'holiday', 'contact', 'help', 'customer service',
            'savings', 'coupons', 'deals', 'offers', 'warehouse', 'costco business',
            'emergency kits', 'health & personal care', 'kirkland signature grocery',
            'laundry detergent', 'paper & plastic', 'wine, champagne',
            'clothing, luggage', 'floral & gift', 'jewelry, watches',
            'commercial appliances', 'prescription drugs', 'auto & home insurance',
            'bottled water delivery', 'personalized photo', 'parts & service',
            'blinds, shades', 'custom closet', 'custom countertops',
            'flooring & carpet', 'garage door', 'generator installation',
            'hvac installation', 'replacement windows', 'water treatment'
        ]

    def detect_content_type(self, html_content: str, url: str, filename: str) -> Tuple[ContentType, Dict]:
        """
        Detect content type with enhanced accuracy.
        
        Returns:
            Tuple of (ContentType, detection_metadata)
        """
        text_content = html_content.lower()
        url_lower = url.lower()
        filename_lower = filename.lower()
        
        scores = {}
        
        for content_type, patterns in self.content_patterns.items():
            score = self._calculate_enhanced_score(
                content_type, patterns, text_content, url_lower, filename_lower
            )
            scores[content_type] = score
            
        # Find best match
        best_type = max(scores, key=scores.get)
        best_score = scores[best_type]
        
        logger.info(f"Content type detected: {best_type.value} (score: {best_score})")
        
        detection_metadata = {
            'detected_type': best_type,
            'confidence_score': best_score,
            'all_scores': {ct.value: score for ct, score in scores.items()},
            'byline': self.content_patterns[best_type]['byline']
        }
        
        return best_type, detection_metadata

    def _calculate_enhanced_score(self, content_type: ContentType, patterns: Dict, 
                                text_content: str, url_lower: str, filename_lower: str) -> int:
        """Calculate enhanced scoring with weighted factors."""
        score = 0
        
        # URL pattern matching (highest weight - 20 points each)
        for pattern in patterns['url_patterns']:
            if pattern in url_lower or pattern in filename_lower:
                score += 20
                
        # Keyword density analysis (medium weight)
        keyword_count = sum(1 for keyword in patterns['keywords'] if keyword in text_content)
        score += keyword_count * 3
        
        # Special pattern bonuses
        if content_type == ContentType.RECIPE:
            # Look for recipe-specific patterns
            if re.search(r'\d+\s+(cup|tablespoon|teaspoon|ounce)', text_content):
                score += 15
            if 'ingredients:' in text_content or 'directions:' in text_content:
                score += 10
                
        elif content_type == ContentType.TRAVEL:
            # Look for travel-specific patterns
            if re.search(r'(visit|explore|discover|destination)', text_content):
                score += 10
            if 'costco travel' in text_content:
                score += 15
                
        elif content_type == ContentType.TECH:
            # Look for tech-specific patterns
            if re.search(r'(features|specifications|review|product)', text_content):
                score += 10
                
        return score

    def extract_content_schema(self, content_type: ContentType, soup: BeautifulSoup, 
                             url: str, detection_metadata: Dict) -> BaseContent:
        """
        Extract content into appropriate schema based on detected type.
        """
        # First, find the actual article content (not navigation or cookie popups)
        article_content = self._find_article_content(soup)
        
        # Base extraction from article content
        base_data = self._extract_base_content(article_content or soup, detection_metadata)
        
        # Type-specific extraction
        if content_type == ContentType.RECIPE:
            return self._extract_recipe_content(article_content or soup, base_data)
        elif content_type == ContentType.TRAVEL:
            return self._extract_travel_content(article_content or soup, base_data)
        elif content_type == ContentType.TECH:
            return self._extract_tech_content(article_content or soup, base_data)
        elif content_type == ContentType.LIFESTYLE:
            return self._extract_lifestyle_content(article_content or soup, base_data)
        elif content_type == ContentType.EDITORIAL:
            return self._extract_editorial_content(article_content or soup, base_data)
        elif content_type == ContentType.SHOPPING:
            return self._extract_shopping_content(article_content or soup, base_data)
        elif content_type == ContentType.MEMBER:
            return self._extract_member_content(article_content or soup, base_data)
        else:
            return BaseContent(**base_data, content_type=content_type)

    def _find_article_content(self, soup: BeautifulSoup):
        """Find the actual article content, avoiding cookie popups and navigation."""
        
        # FIRST: Remove cookie consent popups and overlays
        self._remove_cookie_popups(soup)
        
        # SECOND: Remove navigation and promotional areas
        self._remove_navigation_areas(soup)
        
        # THIRD: Try specific Costco Connection content selectors
        costco_selectors = [
            '.article-content', '.post-content', '.entry-content',
            '.recipe-content', '.main-content', '.content-area',
            '.connection-content', '.magazine-content',
            'article', '[role="main"]', '.article-body',
            # Costco-specific selectors
            '.costco-article', '.connection-article',
            'div[class*="article"]', 'div[class*="content"]'
        ]
        
        for selector in costco_selectors:
            elements = soup.select(selector)
            for element in elements:
                if self._is_valid_costco_content(element):
                    logger.info(f"Found Costco article content using selector: {selector}")
                    return element
        
        # FOURTH: Find content by analyzing all containers
        all_containers = soup.find_all(['div', 'section', 'main', 'article'])
        best_element = None
        best_score = 0
        
        for element in all_containers:
            score = self._score_costco_content_area(element)
            if score > best_score:
                best_score = score
                best_element = element
        
        if best_element and best_score > 100:  # Higher threshold
            logger.info(f"Found Costco content by scoring (score: {best_score})")
            return best_element
        
        logger.warning("Could not find valid Costco article content")
        return None

    def _remove_cookie_popups(self, soup: BeautifulSoup):
        """Remove cookie consent popups and overlays."""
        
        # Cookie popup selectors
        cookie_selectors = [
            # Common cookie popup patterns
            '[class*="cookie"]', '[id*="cookie"]',
            '[class*="consent"]', '[id*="consent"]',
            '[class*="gdpr"]', '[id*="gdpr"]',
            '[class*="privacy"]', '[id*="privacy"]',
            # Overlay and modal patterns
            '[class*="overlay"]', '[class*="modal"]',
            '[class*="popup"]', '[class*="banner"]',
            # Specific Costco patterns
            '[class*="cookie-banner"]', '[class*="privacy-banner"]',
            '.onetrust-consent-sdk', '#onetrust-consent-sdk',
            '.ot-sdk-container', '#ot-sdk-container'
        ]
        
        for selector in cookie_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Double-check it's actually cookie content
                text = element.get_text().lower()
                cookie_indicators = ['cookie', 'consent', 'privacy', 'gdpr', 'strictly necessary']
                if any(indicator in text for indicator in cookie_indicators):
                    logger.info(f"Removing cookie popup: {selector}")
                    element.decompose()

    def _remove_navigation_areas(self, soup: BeautifulSoup):
        """Remove navigation menus and promotional areas."""
        
        # Navigation selectors
        nav_selectors = [
            'nav', 'header', 'footer',
            '[class*="nav"]', '[id*="nav"]',
            '[class*="menu"]', '[id*="menu"]',
            '[class*="header"]', '[class*="footer"]',
            # Costco-specific navigation
            '[class*="department"]', '[class*="shop"]',
            '[class*="business-center"]', '[class*="services"]'
        ]
        
        for selector in nav_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Check if it's really navigation
                text = element.get_text().lower()
                nav_indicators = ['shop', 'department', 'services', 'business center', 'lenses']
                if any(indicator in text for indicator in nav_indicators):
                    logger.info(f"Removing navigation area: {selector}")
                    element.decompose()

    def _is_valid_costco_content(self, element) -> bool:
        """Check if element contains valid Costco Connection article content."""
        text = element.get_text().strip()
        
        # Must have substantial content
        if len(text) < 300:  # Increased threshold
            return False
        
        # Check for cookie popup content
        cookie_indicators = ['cookie settings', 'strictly necessary', 'functional cookies', 
                            'targeting cookies', 'privacy preferences', 'gdpr']
        if any(indicator in text.lower() for indicator in cookie_indicators):
            logger.info("Rejected element: Contains cookie popup content")
            return False
        
        # Check for navigation content
        nav_density = sum(1 for nav_term in self.navigation_blacklist if nav_term in text.lower())
        total_words = len(text.split())
        
        if total_words > 0 and (nav_density / total_words * 100) > 5:  # Stricter threshold
            logger.info("Rejected element: High navigation content density")
            return False
        
        # Look for positive content indicators
        positive_indicators = [
            # Recipe indicators
            'ingredients', 'tablespoon', 'teaspoon', 'ounce', 'cup', 'recipe',
            # Travel indicators  
            'destination', 'visit', 'explore', 'attractions', 'travel',
            # Tech indicators
            'features', 'technology', 'device', 'product',
            # General article indicators
            'costco connection', 'by costco', 'article', 'story'
        ]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in text.lower())
        
        if positive_count < 2:  # Need at least 2 positive indicators
            logger.info("Rejected element: Insufficient positive content indicators")
            return False
        
        return True

    def _score_costco_content_area(self, element) -> int:
        """Enhanced scoring for Costco Connection content."""
        score = 0
        text = element.get_text().strip()
        text_lower = text.lower()
        
        # Content length scoring (higher threshold)
        text_length = len(text)
        if text_length > 1000:
            score += 50
        elif text_length > 500:
            score += 30
        elif text_length > 300:
            score += 15
        
        # Paragraph count
        paragraphs = len(element.find_all('p'))
        score += paragraphs * 8  # Higher weight for paragraphs
        
        # Headings
        headings = len(element.find_all(['h1', 'h2', 'h3', 'h4']))
        score += headings * 5
        
        # Lists (might be ingredients/instructions)
        lists = len(element.find_all(['ul', 'ol']))
        score += lists * 10  # Higher weight for lists
        
        # Positive content indicators
        positive_indicators = [
            'ingredients', 'recipe', 'directions', 'tablespoon', 'teaspoon',
            'destination', 'travel', 'visit', 'attractions',
            'features', 'technology', 'product', 'review',
            'costco connection', 'by costco'
        ]
        positive_count = sum(1 for indicator in positive_indicators if indicator in text_lower)
        score += positive_count * 15
        
        # MAJOR PENALTIES for unwanted content
        
        # Cookie popup penalty
        cookie_indicators = ['cookie settings', 'strictly necessary', 'functional cookies', 
                            'targeting cookies', 'privacy preferences']
        cookie_count = sum(1 for indicator in cookie_indicators if indicator in text_lower)
        score -= cookie_count * 100  # Massive penalty
        
        # Navigation penalty
        nav_count = sum(1 for nav_term in self.navigation_blacklist if nav_term in text_lower)
        score -= nav_count * 20  # Higher penalty
        
        # Too many links penalty (navigation characteristic)
        links = len(element.find_all('a'))
        if links > 15:
            score -= 30
        
        # Class name penalties
        class_names = ' '.join(element.get('class', [])).lower()
        penalty_classes = ['nav', 'menu', 'header', 'footer', 'cookie', 'consent', 'popup']
        for penalty_class in penalty_classes:
            if penalty_class in class_names:
                score -= 50
        
        return max(0, score)

    def _extract_base_content(self, soup: BeautifulSoup, detection_metadata: Dict) -> Dict:
        """Enhanced base content extraction avoiding cookie popups."""
        
        # Find title/headline with cookie popup avoidance
        title = ""
        headline = ""
        
        # Try multiple selectors for title, avoiding popups
        title_candidates = []
        title_selectors = ['h1', '.title', '.headline', '.article-title', '.recipe-title']
        
        for selector in title_selectors:
            title_elements = soup.select(selector)
            for title_elem in title_elements:
                title_text = title_elem.get_text().strip()
                
                # Skip cookie popup titles
                if 'cookie' in title_text.lower() or 'privacy' in title_text.lower():
                    continue
                    
                if (title_text and len(title_text) > 5 and len(title_text) < 200 and 
                    not self._is_navigation_text(title_text)):
                    title_candidates.append((title_text, len(title_text)))
        
        # Choose the longest reasonable title
        if title_candidates:
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            title = title_candidates[0][0]
            
        # Try to find main headline (different from title)
        headline_candidates = []
        headline_selectors = ['.main-headline', '.article-headline', 'h2', '.subtitle']
        
        for selector in headline_selectors:
            headline_elements = soup.select(selector)
            for headline_elem in headline_elements:
                headline_text = headline_elem.get_text().strip()
                
                # Skip cookie popup headlines
                if 'cookie' in headline_text.lower() or 'privacy' in headline_text.lower():
                    continue
                    
                if (headline_text and len(headline_text) > 5 and len(headline_text) < 200 and 
                    not self._is_navigation_text(headline_text) and headline_text != title):
                    headline_candidates.append((headline_text, len(headline_text)))
        
        if headline_candidates:
            headline_candidates.sort(key=lambda x: x[1], reverse=True)
            headline = headline_candidates[0][0]
            
        # Extract description from first substantial paragraph (avoiding cookie text)
        description = ""
        description_candidates = []
        
        for p in soup.find_all('p'):
            p_text = p.get_text().strip()
            
            # Skip cookie popup descriptions
            if ('cookie' in p_text.lower() or 'privacy' in p_text.lower() or 
                'consent' in p_text.lower() or 'gdpr' in p_text.lower()):
                continue
                
            if (len(p_text) > 50 and len(p_text) < 500 and
                not self._is_navigation_text(p_text) and
                len(p_text.split()) > 8):
                description_candidates.append((p_text, len(p_text)))
        
        if description_candidates:
            description_candidates.sort(key=lambda x: x[1], reverse=True)
            description = description_candidates[0][0][:200]
            
        logger.info(f"Extracted base content - Title: '{title}', Headline: '{headline}', Description length: {len(description)}")
            
        return {
            'title': title,
            'headline': headline or title,
            'byline': detection_metadata.get('byline', ''),
            'description': description
        }

    def _is_navigation_text(self, text: str) -> bool:
        """Check if text appears to be navigation content."""
        text_lower = text.lower()
        
        # Check against navigation blacklist
        nav_matches = sum(1 for nav_term in self.navigation_blacklist if nav_term in text_lower)
        
        # Short text with navigation terms is likely navigation
        word_count = len(text.split())
        if nav_matches > 0 and word_count < 8:
            return True
        
        # High density of navigation terms
        if word_count > 0 and (nav_matches / word_count) > 0.3:
            return True
        
        # Common navigation patterns
        nav_patterns = [
            r'shop\s+\w+', r'view\s+all', r'see\s+more', r'browse\s+\w+',
            r'compare\s+\w+', r'find\s+a\s+\w+', r'locate\s+\w+',
            r'\w+\s+&\s+\w+\s+\w+',  # "Health & Personal Care" pattern
        ]
        
        for pattern in nav_patterns:
            if re.search(pattern, text_lower):
                return True
        
        return False

    def _extract_recipe_content(self, soup: BeautifulSoup, base_data: Dict) -> RecipeContent:
        """Extract recipe-specific content with improved navigation filtering."""
        ingredients = []
        instructions = []
        
        # Extract ingredients with multiple strategies
        ingredients = self._extract_ingredients_smart(soup)
        
        # Extract instructions with navigation filtering
        instructions = self._extract_instructions_smart(soup)
        
        # Extract timing and serving info
        prep_time = self._extract_time_info(soup, ['prep time', 'preparation', 'prep:'])
        cook_time = self._extract_time_info(soup, ['cook time', 'cooking time', 'bake', 'cook:'])
        servings = self._extract_serving_info(soup)
        
        logger.info(f"Recipe extraction: {len(ingredients)} ingredients, {len(instructions)} instructions")
        
        return RecipeContent(
            **base_data,
            ingredients=ingredients,
            instructions=instructions,
            prep_time=prep_time,
            cook_time=cook_time,
            servings=servings
        )

    def _extract_ingredients_smart(self, soup: BeautifulSoup) -> List[str]:
        """Smart ingredient extraction avoiding navigation."""
        ingredients = []
        
        # Strategy 1: Look for elements with measurement units
        measurement_units = ['cup', 'cups', 'tablespoon', 'tablespoons', 'tbsp', 'teaspoon', 'teaspoons', 'tsp', 
                           'ounce', 'ounces', 'oz', 'pound', 'pounds', 'lb', 'lbs', 'gram', 'grams', 'g']
        
        for element in soup.find_all(['li', 'p', 'div', 'span']):
            text = element.get_text().strip()
            
            # Skip navigation text
            if self._is_navigation_text(text):
                continue
            
            # Must contain measurement units and numbers
            if (any(unit in text.lower() for unit in measurement_units) and 
                re.search(r'\d+', text) and 
                len(text) > 5 and len(text) < 200):
                ingredients.append(text)
        
        # Strategy 2: Look for fraction symbols (common in recipes)
        if len(ingredients) < 3:
            for element in soup.find_all(['li', 'p', 'div']):
                text = element.get_text().strip()
                
                if (re.search(r'[¼½¾⅓⅔⅛⅜⅝⅞]', text) and
                    not self._is_navigation_text(text) and
                    len(text) > 5 and len(text) < 150):
                    if text not in ingredients:
                        ingredients.append(text)
        
        # Strategy 3: Look for ingredients lists in specific containers
        if len(ingredients) < 3:
            ingredient_containers = soup.select('.ingredients, .recipe-ingredients, [class*="ingredient"]')
            for container in ingredient_containers:
                for li in container.find_all('li'):
                    text = li.get_text().strip()
                    if (text and not self._is_navigation_text(text) and 
                        len(text) > 5 and text not in ingredients):
                        ingredients.append(text)
        
        return ingredients[:20]  # Limit to reasonable number

    def _extract_instructions_smart(self, soup: BeautifulSoup) -> List[str]:
        """Smart instruction extraction avoiding navigation."""
        instructions = []
        
        # Cooking action words
        cooking_verbs = ['preheat', 'heat', 'cook', 'bake', 'mix', 'stir', 'add', 'combine', 
                        'place', 'put', 'pour', 'slice', 'chop', 'dice', 'blend', 'whisk',
                        'season', 'serve', 'garnish', 'remove', 'drain', 'cover', 'simmer']
        
        # Strategy 1: Look for ordered lists with cooking verbs
        for ol in soup.find_all('ol'):
            ol_instructions = []
            for li in ol.find_all('li'):
                text = li.get_text().strip()
                
                # Skip navigation text
                if self._is_navigation_text(text):
                    continue
                
                # Must contain cooking verbs and be substantial
                if (any(verb in text.lower() for verb in cooking_verbs) and 
                    len(text) > 15 and len(text.split()) > 3):
                    ol_instructions.append(text)
            
            if len(ol_instructions) > 2:  # Good instruction list
                instructions = ol_instructions
                break
        
        # Strategy 2: Look for unordered lists with cooking content
        if len(instructions) < 3:
            for ul in soup.find_all('ul'):
                ul_instructions = []
                for li in ul.find_all('li'):
                    text = li.get_text().strip()
                    
                    if (not self._is_navigation_text(text) and
                        any(verb in text.lower() for verb in cooking_verbs) and
                        len(text) > 20):
                        ul_instructions.append(text)
                
                if len(ul_instructions) > len(instructions):
                    instructions = ul_instructions
        
        # Strategy 3: Look for paragraphs with step indicators
        if len(instructions) < 3:
            step_pattern = r'^\s*(\d+\.|\d+\)|step\s+\d+)'
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                
                if (re.match(step_pattern, text.lower()) and
                    not self._is_navigation_text(text) and
                    len(text) > 20):
                    instructions.append(text)
        
        return instructions[:15]  # Limit to reasonable number

    def _extract_travel_content(self, soup: BeautifulSoup, base_data: Dict) -> TravelContent:
        """Extract travel-specific content."""
        destinations = []
        attractions = []
        restaurants = []
        activities = []
        
        # Extract destinations from text (avoiding navigation)
        text = soup.get_text()
        
        # Look for common destination patterns
        dest_patterns = [
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:is|offers|features|boasts)',
            r'visit\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'explore\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in dest_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if not self._is_navigation_text(match) and len(match.split()) <= 3:
                    destinations.append(match)
        
        # Extract travel tips and cultural notes from paragraphs
        travel_tips = []
        cultural_notes = []
        
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if self._is_navigation_text(text):
                continue
                
            if any(tip_word in text.lower() for tip_word in ['tip:', 'advice', 'recommend', 'best time']):
                travel_tips.append(text)
            elif any(culture_word in text.lower() for culture_word in ['culture', 'history', 'tradition', 'heritage']):
                cultural_notes.append(text)
        
        return TravelContent(
            **base_data,
            destinations=list(set(destinations))[:10],
            attractions=attractions,
            restaurants=restaurants,
            activities=activities,
            travel_tips=travel_tips[:5],
            cultural_notes=cultural_notes[:5]
        )

    def _extract_tech_content(self, soup: BeautifulSoup, base_data: Dict) -> TechContent:
        """Extract tech-specific content."""
        products = []
        brands = []
        features = []
        
        # Extract product names and brands (avoiding navigation)
        text = soup.get_text()
        
        # Common tech brand patterns
        brand_patterns = ['Apple', 'Samsung', 'Google', 'Microsoft', 'Sony', 'LG', 'HP', 'Dell', 'iRobot', 'Dyson']
        for brand in brand_patterns:
            if brand.lower() in text.lower() and brand not in brands:
                brands.append(brand)
        
        # Extract features from lists or bullet points
        for element in soup.find_all(['li', '.feature', '.spec']):
            text = element.get_text().strip()
            if (text and not self._is_navigation_text(text) and 
                any(tech_word in text.lower() for tech_word in ['feature', 'capability', 'function', 'technology'])):
                features.append(text)
        
        return TechContent(
            **base_data,
            products=products[:10],
            brands=list(set(brands)),
            features=features[:10]
        )

    def _extract_lifestyle_content(self, soup: BeautifulSoup, base_data: Dict) -> LifestyleContent:
        """Extract lifestyle-specific content."""
        topics = []
        wellness_tips = []
        family_activities = []
        
        # Extract lifestyle topics from headings (avoiding navigation)
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            text = heading.get_text().strip()
            if text and not self._is_navigation_text(text):
                topics.append(text)
        
        # Extract wellness and family content
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if self._is_navigation_text(text):
                continue
                
            if any(wellness_word in text.lower() for wellness_word in ['health', 'wellness', 'exercise', 'nutrition']):
                wellness_tips.append(text)
            elif any(family_word in text.lower() for family_word in ['family', 'kids', 'children', 'activity']):
                family_activities.append(text)
        
        return LifestyleContent(
            **base_data,
            topics=topics[:10],
            wellness_tips=wellness_tips[:5],
            family_activities=family_activities[:5]
        )

    def _extract_editorial_content(self, soup: BeautifulSoup, base_data: Dict) -> EditorialContent:
        """Extract editorial-specific content."""
        key_messages = []
        costco_values = []
        
        # Extract key editorial messages from paragraphs (avoiding navigation)
        for p in soup.find_all('p'):
            text = p.get_text().strip()
            if self._is_navigation_text(text):
                continue
                
            if len(text) > 50:  # Substantial content
                if any(value_word in text.lower() for value_word in ['value', 'member', 'quality', 'service']):
                    costco_values.append(text)
                else:
                    key_messages.append(text)
        
        return EditorialContent(
            **base_data,
            key_messages=key_messages[:3],  # Limit to top 3
            costco_values=costco_values[:3]
        )

    def _extract_shopping_content(self, soup: BeautifulSoup, base_data: Dict) -> ShoppingContent:
        """Extract shopping-specific content."""
        featured_products = []
        kirkland_signature = []
        
        text = soup.get_text()
        
        # Look for Kirkland Signature mentions (avoiding navigation)
        if 'kirkland signature' in text.lower():
            kirkland_matches = re.findall(r'Kirkland Signature ([^.]+)', text, re.IGNORECASE)
            for match in kirkland_matches:
                if not self._is_navigation_text(match):
                    kirkland_signature.append(match.strip())
        
        return ShoppingContent(
            **base_data,
            featured_products=featured_products,
            kirkland_signature=kirkland_signature[:5]
        )

    def _extract_member_content(self, soup: BeautifulSoup, base_data: Dict) -> MemberContent:
        """Extract member-specific content."""
        poll_questions = []
        member_comments = []
        
        # Extract poll questions (avoiding navigation)
        for elem in soup.find_all(['h3', 'h4', '.question']):
            text = elem.get_text().strip()
            if '?' in text and not self._is_navigation_text(text):
                poll_questions.append(text)
        
        return MemberContent(
            **base_data,
            poll_questions=poll_questions[:5],
            member_comments=member_comments
        )

    def _extract_time_info(self, soup: BeautifulSoup, time_indicators: List[str]) -> str:
        """Extract time information from text."""
        text = soup.get_text().lower()
        for indicator in time_indicators:
            pattern = rf'{indicator}[:\s]*(\d+(?:\s*-\s*\d+)?\s*(?:minutes?|mins?|hours?|hrs?))'
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return ""

    def _extract_serving_info(self, soup: BeautifulSoup) -> str:
        """Extract serving information."""
        text = soup.get_text().lower()
        serving_pattern = r'(?:serves|servings?)[:\s]*(\d+(?:\s*-\s*\d+)?)'
        match = re.search(serving_pattern, text)
        if match:
            return match.group(1)
        return ""