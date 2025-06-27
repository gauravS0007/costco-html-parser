"""
Simple Fixed Universal Content Extractor - No Syntax Errors
Complete working version that addresses all the extraction issues
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
    """Fixed Universal content extractor with proper extraction"""
    
    def __init__(self):
        # Content type detection patterns
        self.content_patterns = {
            'recipe': {
                'url_keywords': ['recipe'],
                'title_keywords': ['recipe', 'roll-ups', 'jam', 'crumble'],
                'content_keywords': ['ingredients', 'directions', 'tablespoon', 'cup', 'cooking'],
                'required_score': 3
            },
            'travel': {
                'url_keywords': ['travel-connection', 'tale-of'],
                'title_keywords': ['travel', 'cities', 'destination'],
                'content_keywords': ['destination', 'attractions', 'visit', 'explore'],
                'required_score': 3
            },
            'tech': {
                'url_keywords': ['tech', 'power-up'],
                'title_keywords': ['tech', 'power', 'technology'],
                'content_keywords': ['technology', 'device', 'features', 'review'],
                'required_score': 3
            },
            'editorial': {
                'url_keywords': ['publisher', 'note', 'front-cover'],
                'title_keywords': ['publisher', 'note', 'editorial'],
                'content_keywords': ['costco', 'members', 'connection', 'sandy torrey'],
                'required_score': 2
            },
            'member': {
                'url_keywords': ['member-poll', 'member-comments'],
                'title_keywords': ['member', 'poll', 'comments'],
                'content_keywords': ['member', 'poll', 'facebook', 'comments'],
                'required_score': 2
            },
            'shopping': {
                'url_keywords': ['treasure-hunt', 'buying-smart'],
                'title_keywords': ['treasure', 'buying', 'smart'],
                'content_keywords': ['product', 'buying', 'costco', 'warehouse'],
                'required_score': 2
            },
            'lifestyle': {
                'url_keywords': ['costco-life', 'fye', 'supplier'],
                'title_keywords': ['celebrate', 'entertainment', 'author'],
                'content_keywords': ['lifestyle', 'entertainment', 'author', 'book'],
                'required_score': 2
            }
        }

    def extract_all_content(self, html_content: str, url: str) -> ExtractedContent:
        """Extract ALL meaningful content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
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
        self._extract_content_specific(main_content_area or cleaned_soup, extracted, content_type)
        
        logger.info(f"✅ Extracted: {content_type} - {len(extracted.main_content)} paragraphs, {len(extracted.images)} images")
        
        return extracted

    def _clean_html(self, soup: BeautifulSoup) -> BeautifulSoup:
        """Clean unwanted elements"""
        
        # Remove script, style, nav, header, footer
        for tag in ['script', 'style', 'nav', 'header', 'footer', 'aside']:
            for element in soup.find_all(tag):
                element.decompose()
        
        # Remove by class patterns
        unwanted_classes = [
            'nav', 'menu', 'header', 'footer', 'cookie', 'consent',
            'promo', 'banner', 'ad', 'advertisement'
        ]
        
        for class_pattern in unwanted_classes:
            for element in soup.find_all(class_=re.compile(class_pattern, re.I)):
                element.decompose()
        
        # Remove by text content
        unwanted_texts = [
            'shop costco.com', 'add to cart', 'compare products',
            'we use cookies', 'accept cookies', 'privacy policy'
        ]
        
        for element in soup.find_all(['div', 'section', 'p']):
            text = element.get_text().lower().strip()
            if any(unwanted in text for unwanted in unwanted_texts):
                if len(text.split()) < 20:
                    element.decompose()
        
        return soup

    def _find_main_content(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Find main content area"""
        
        candidates = []
        
        # Try semantic elements
        for tag in ['main', 'article', '[role="main"]']:
            elements = soup.select(tag)
            for element in elements:
                score = self._score_element(element)
                if score > 30:
                    candidates.append((element, score))
        
        # Try content selectors
        selectors = [
            '.article-content', '.post-content', '.entry-content',
            '.main-content', '.content-area'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                score = self._score_element(element)
                if score > 20:
                    candidates.append((element, score))
        
        # Try divs with good content
        for div in soup.find_all('div'):
            score = self._score_element(div)
            if score > 50:
                candidates.append((div, score))
        
        if candidates:
            candidates.sort(key=lambda x: x[1], reverse=True)
            return candidates[0][0]
        
        return soup.find('body')

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
        score += len(element.find_all('p')) * 5
        score += len(element.find_all(['h1', 'h2', 'h3'])) * 8
        score += len(element.find_all(['ul', 'ol'])) * 5
        
        # Quality indicators
        if 'costco connection' in text.lower():
            score += 20
        if any(word in text.lower() for word in ['recipe', 'travel', 'tech']):
            score += 10
        
        return score

    def _detect_content_type(self, url: str, soup: BeautifulSoup, main_content: Tag) -> str:
        """Enhanced content type detection"""
        
        url_lower = url.lower()
        
        # Get text content
        main_text = main_content.get_text().lower() if main_content else ""
        soup_text = soup.get_text().lower()
        
        # Get title
        title_text = ""
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().lower()
        
        # Score each content type
        type_scores = {}
        
        for content_type, patterns in self.content_patterns.items():
            score = 0
            
            # URL scoring (highest weight)
            for keyword in patterns['url_keywords']:
                if keyword in url_lower:
                    score += 20
            
            # Title scoring
            for keyword in patterns['title_keywords']:
                if keyword in title_text:
                    score += 10
            
            # Content scoring
            for keyword in patterns['content_keywords']:
                if keyword in main_text or keyword in soup_text:
                    score += 5
            
            type_scores[content_type] = score
        
        # Find best match
        if type_scores:
            best_type = max(type_scores, key=type_scores.get)
            best_score = type_scores[best_type]
            required_score = self.content_patterns[best_type]['required_score']
            
            if best_score >= required_score:
                logger.info(f"🎯 Content type: {best_type} (score: {best_score})")
                return best_type
        
        return 'general'

    def _extract_title_and_metadata(self, soup: BeautifulSoup, extracted: ExtractedContent, url: str):
        """Extract title and metadata"""
        
        # Title strategies
        title_candidates = []
        
        # H1 tags (highest priority)
        for h1 in soup.find_all('h1'):
            title_text = h1.get_text().strip()
            if title_text and len(title_text) > 3 and 'costco' not in title_text.lower():
                title_candidates.append((title_text, 20))
        
        # Title tag
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text().strip()
            title_text = re.sub(r'\s*[\|\-]\s*Costco.*', '', title_text)
            if title_text and len(title_text) > 3:
                title_candidates.append((title_text, 15))
        
        # Choose best title
        if title_candidates:
            title_candidates.sort(key=lambda x: x[1], reverse=True)
            extracted.title = title_candidates[0][0]
        
        # Byline extraction
        byline_patterns = [
            r'by\s+([^,\n\.]+)',
            r'recipe\s+(?:and\s+photo\s+)?courtesy\s+of\s+([^,\n\.]+)'
        ]
        
        full_text = soup.get_text()
        for pattern in byline_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                extracted.byline = f"By {match.group(1).strip()}"
                break

    def _extract_text_content(self, content_area: Tag, extracted: ExtractedContent):
        """Extract text content"""
        
        if not content_area:
            return
        
        # Extract paragraphs
        for p in content_area.find_all('p'):
            text = p.get_text().strip()
            if text and len(text) > 15:
                extracted.main_content.append(text)
        
        # Extract div content
        for div in content_area.find_all('div'):
            div_text = div.get_text().strip()
            if div_text and len(div_text) > 30:
                # Check if new content
                is_new = True
                for existing in extracted.main_content:
                    if self._text_similarity(div_text, existing) > 0.8:
                        is_new = False
                        break
                
                if is_new:
                    extracted.main_content.append(div_text)
        
        # Store full text
        extracted.full_text = content_area.get_text()

    def _extract_images(self, soup: BeautifulSoup, extracted: ExtractedContent, url: str):
        """Enhanced image extraction"""
        
        base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        
        for img in soup.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', '')
            
            if not src:
                continue
            
            # Fix URLs
            fixed_src = self._fix_image_url(src, base_url)
            if not fixed_src:
                continue
            
            # Score image
            score = self._score_image(fixed_src, alt, img)
            
            image_data = {
                'src': fixed_src,
                'alt': alt,
                'score': score,
                'width': img.get('width', ''),
                'height': img.get('height', ''),
                'class': ' '.join(img.get('class', []))
            }
            
            extracted.images.append(image_data)
        
        # Sort by score
        extracted.images.sort(key=lambda x: x['score'], reverse=True)

    def _fix_image_url(self, src: str, base_url: str) -> str:
        """Fix image URLs"""
        
        if not src:
            return ""
        
        # Already absolute
        if src.startswith(('http://', 'https://')):
            return src
        
        # Costco CDN paths
        if src.startswith('/live/resource/img/'):
            return f"https://mobilecontent.costco.com{src}"
        
        # Relative paths with date
        if src.startswith('./') or src.startswith('../'):
            filename = src.split('/')[-1]
            date_match = re.search(r'(\d{2})_(\d{2})', filename)
            if date_match:
                month_num, year_num = date_match.groups()
                month_names = {
                    '01': 'january', '02': 'february', '03': 'march', '04': 'april',
                    '05': 'may', '06': 'june', '07': 'july', '08': 'august',
                    '09': 'september', '10': 'october', '11': 'november', '12': 'december'
                }
                month_name = month_names.get(month_num, 'october')
                folder = f"static-us-connection-{month_name}-{year_num}"
                return f"https://mobilecontent.costco.com/live/resource/img/{folder}/{filename}"
        
        # Standard relative URL
        if src.startswith('/'):
            return urljoin(base_url, src)
        
        return urljoin(base_url, src)

    def _score_image(self, src: str, alt: str, img_element: Tag) -> int:
        """Score image quality"""
        
        score = 0
        src_lower = src.lower()
        alt_lower = alt.lower()
        
        # Domain scoring
        if 'mobilecontent.costco.com' in src_lower:
            score += 60
        if 'static-us-connection' in src_lower:
            score += 40
        
        # Size scoring
        width = img_element.get('width')
        height = img_element.get('height')
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
        content_terms = ['recipe', 'food', 'travel', 'destination', 'tech', 'product', 'costco']
        for term in content_terms:
            if term in alt_lower or term in src_lower:
                score += 10
        
        # Penalties
        penalty_terms = ['logo', 'icon', 'nav', 'menu', 'banner', 'ad']
        for term in penalty_terms:
            if term in alt_lower or term in src_lower:
                score -= 15
        
        return max(0, score)

    def _extract_structured_content(self, content_area: Tag, extracted: ExtractedContent):
        """Extract headings and lists"""
        
        # Headings
        for heading in content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            heading_text = heading.get_text().strip()
            if heading_text and len(heading_text) > 2:
                if not any(nav in heading_text.lower() for nav in ['compare', 'shop']):
                    extracted.headings.append({
                        'text': heading_text,
                        'level': int(heading.name[1]),
                        'class': ' '.join(heading.get('class', []))
                    })
        
        # Lists
        for list_elem in content_area.find_all(['ul', 'ol']):
            list_items = []
            for li in list_elem.find_all('li'):
                item_text = li.get_text().strip()
                if item_text and len(item_text) > 2:
                    list_items.append(item_text)
            
            if list_items:
                extracted.lists.append({
                    'type': 'ordered' if list_elem.name == 'ol' else 'unordered',
                    'items': list_items,
                    'class': ' '.join(list_elem.get('class', []))
                })

    def _extract_content_specific(self, content_area: Tag, extracted: ExtractedContent, content_type: str):
        """Content-specific extraction"""
        
        if content_type == 'recipe':
            self._extract_recipe_data(content_area, extracted)
        elif content_type == 'travel':
            self._extract_travel_data(content_area, extracted)
        elif content_type == 'member':
            self._extract_member_data(content_area, extracted)

    def _extract_recipe_data(self, content_area: Tag, extracted: ExtractedContent):
        """Extract recipe-specific data"""
        
        ingredients = []
        instructions = []
        
        # Find ingredients in lists with measurements
        measurement_units = ['cup', 'tablespoon', 'teaspoon', 'ounce', 'pound', 'gram']
        
        for list_data in extracted.lists:
            has_measurements = any(
                any(unit in item.lower() for unit in measurement_units)
                for item in list_data['items']
            )
            
            if has_measurements:
                ingredients = list_data['items']
                break
        
        # Find instructions (ordered lists or numbered content)
        for list_data in extracted.lists:
            if list_data['type'] == 'ordered' and list_data['items'] != ingredients:
                instructions = list_data['items']
                break
        
        # Extract timing info
        full_text = content_area.get_text() if content_area else ""
        
        prep_time_match = re.search(r'prep\s*time[:\s]*(\d+(?:\s*-\s*\d+)?\s*(?:minutes?|mins?))', full_text, re.I)
        cook_time_match = re.search(r'cook\s*time[:\s]*(\d+(?:\s*-\s*\d+)?\s*(?:minutes?|mins?))', full_text, re.I)
        servings_match = re.search(r'(?:serves?|servings?)[:\s]*(\d+(?:\s*-\s*\d+)?)', full_text, re.I)
        
        extracted.metadata['ingredients'] = ingredients
        extracted.metadata['instructions'] = instructions
        extracted.metadata['prep_time'] = prep_time_match.group(1) if prep_time_match else ""
        extracted.metadata['cook_time'] = cook_time_match.group(1) if cook_time_match else ""
        extracted.metadata['servings'] = servings_match.group(1) if servings_match else ""

    def _extract_travel_data(self, content_area: Tag, extracted: ExtractedContent):
        """Extract travel-specific data"""
        
        destinations = []
        attractions = []
        
        # Extract destinations
        destination_patterns = [
            r'visit\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'explore\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        full_text = content_area.get_text() if content_area else ""
        for pattern in destination_patterns:
            matches = re.findall(pattern, full_text)
            destinations.extend(matches)
        
        extracted.metadata['destinations'] = list(set(destinations))[:10]
        extracted.metadata['attractions'] = attractions

    def _extract_member_data(self, content_area: Tag, extracted: ExtractedContent):
        """Extract member-specific data"""
        
        poll_questions = []
        member_comments = []
        
        # Extract poll questions
        for heading in extracted.headings:
            if '?' in heading['text']:
                poll_questions.append(heading['text'])
        
        for content in extracted.main_content:
            if '?' in content and len(content.split()) < 20:
                poll_questions.append(content)
            elif 'member' in content.lower() and len(content) > 50:
                member_comments.append(content)
        
        extracted.metadata['poll_questions'] = poll_questions[:5]
        extracted.metadata['member_comments'] = member_comments[:10]

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0


# Main extraction function
def extract_content_from_html_fixed(html_content: str, url: str) -> ExtractedContent:
    """Main function to extract content"""
    extractor = FixedUniversalContentExtractor()
    return extractor.extract_all_content(html_content, url)