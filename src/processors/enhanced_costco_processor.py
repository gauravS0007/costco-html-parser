"""
Enhanced Costco content processor with rich schema support.
"""

import json
import re
import logging
import boto3
from bs4 import BeautifulSoup
from typing import Optional, Dict, Union
from dataclasses import asdict

from ..config.settings import AWS_REGION, BEDROCK_MODEL_ID, AI_CONFIG, ARTICLE_SELECTORS, NAVIGATION_TERMS
from ..utils.image_utils import fix_image_urls, get_scored_images, format_images_for_ai
from ..utils.enhanced_content_detector import EnhancedContentDetector
from ..models.content_schemas import (
    ContentType, EnhancedPageStructure, RecipeContent, TravelContent, 
    TechContent, LifestyleContent, EditorialContent, ShoppingContent, MemberContent
)

logger = logging.getLogger(__name__)


class EnhancedCostcoProcessor:
    """Enhanced Costco processor with schema-aware content extraction."""

    def __init__(self):
        """Initialize processor with AWS Bedrock and content detector."""
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=AWS_REGION
            )
            self.model_id = BEDROCK_MODEL_ID
            self.content_detector = EnhancedContentDetector()
            logger.info("Enhanced Costco processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize processor: {e}")
            self.bedrock = None

    def process_content(self, html_content: str, url: str, filename: str) -> Optional[EnhancedPageStructure]:
        """
        Process content with enhanced schema-aware extraction.
        
        Args:
            html_content: HTML content to process
            url: Page URL
            filename: Source filename
            
        Returns:
            EnhancedPageStructure or None if processing fails
        """
        try:
            # Fix images and parse HTML
            fixed_html = fix_image_urls(html_content, url)
            soup = BeautifulSoup(fixed_html, 'html.parser')
            article_area = self.find_article_area(soup)

            # Detect content type with enhanced detection
            content_type, detection_metadata = self.content_detector.detect_content_type(
                html_content, url, filename
            )

            # Extract schema-aware content
            content_schema = self.content_detector.extract_content_schema(
                content_type, soup, url, detection_metadata
            )

            # Enhance with AI if available
            if self.bedrock:
                ai_enhanced_content = self._enhance_with_ai(
                    content_schema, soup, article_area, content_type, url, filename
                )
                if ai_enhanced_content:
                    content_schema = ai_enhanced_content

            # Build enhanced page structure
            page_structure = self._build_enhanced_structure(
                url, content_schema, detection_metadata, soup
            )

            logger.info(f"✅ Enhanced processing complete for {content_type.value} content")
            return page_structure

        except Exception as e:
            logger.error(f"Enhanced processing failed: {e}")
            return None

    def find_article_area(self, soup: BeautifulSoup):
        """Find the main article content area."""
        # Try specific article selectors first
        for selector in ARTICLE_SELECTORS:
            containers = soup.select(selector)
            for container in containers:
                text_length = len(container.get_text().strip())
                if text_length > 500:
                    logger.info(f"Found article area: {selector} ({text_length} chars)")
                    return container

        # Fallback: find container with most relevant content
        return self._find_best_content_container(soup)

    def _find_best_content_container(self, soup: BeautifulSoup):
        """Find the best content container using enhanced scoring."""
        all_divs = soup.find_all(['div', 'section', 'main', 'article'])
        best_container = None
        best_score = 0

        for div in all_divs:
            # Skip navigation areas
            class_names = ' '.join(div.get('class', [])).lower()
            if any(skip in class_names for skip in NAVIGATION_TERMS):
                continue

            # Enhanced content quality scoring
            paragraphs = len(div.find_all('p'))
            headings = len(div.find_all(['h1', 'h2', 'h3']))
            lists = len(div.find_all(['ul', 'ol']))
            text_length = len(div.get_text().strip())

            # Enhanced scoring algorithm
            score = (paragraphs * 5 + 
                    headings * 10 + 
                    lists * 3 + 
                    min(text_length // 100, 50))

            if score > best_score and text_length > 200:
                best_score = score
                best_container = div

        if best_container:
            logger.info(f"Found best content area (enhanced score: {best_score})")
            return best_container

        return soup.find('body')

    def _enhance_with_ai(self, content_schema, soup: BeautifulSoup, article_area, 
                        content_type: ContentType, url: str, filename: str):
        """Enhance content schema with AI extraction."""
        try:
            # Create content-type specific AI prompt
            prompt = self._create_enhanced_ai_prompt(
                content_schema, soup, article_area, content_type, url, filename
            )
            
            # Call AI
            ai_result = self.call_ai(prompt)
            if not ai_result:
                return None

            # Merge AI results with existing schema
            enhanced_schema = self._merge_ai_results(content_schema, ai_result, content_type)
            return enhanced_schema

        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return None

    def _create_enhanced_ai_prompt(self, content_schema, soup: BeautifulSoup, 
                                 article_area, content_type: ContentType, 
                                 url: str, filename: str) -> str:
        """Create content-type specific AI prompts."""
        
        # Get and score images
        scored_images = get_scored_images(soup, article_area, content_type.value)
        images_text = format_images_for_ai(scored_images, AI_CONFIG['max_images_to_analyze'])

        # Base content for analysis
        content_to_analyze = (
            str(article_area)[:AI_CONFIG['max_content_length']] 
            if article_area 
            else str(soup)[:AI_CONFIG['max_content_length']]
        )

        if content_type == ContentType.RECIPE:
            return self._create_recipe_prompt(content_schema, images_text, content_to_analyze, url, filename)
        elif content_type == ContentType.TRAVEL:
            return self._create_travel_prompt(content_schema, images_text, content_to_analyze, url, filename)
        elif content_type == ContentType.TECH:
            return self._create_tech_prompt(content_schema, images_text, content_to_analyze, url, filename)
        elif content_type == ContentType.LIFESTYLE:
            return self._create_lifestyle_prompt(content_schema, images_text, content_to_analyze, url, filename)
        elif content_type == ContentType.EDITORIAL:
            return self._create_editorial_prompt(content_schema, images_text, content_to_analyze, url, filename)
        elif content_type == ContentType.SHOPPING:
            return self._create_shopping_prompt(content_schema, images_text, content_to_analyze, url, filename)
        elif content_type == ContentType.MEMBER:
            return self._create_member_prompt(content_schema, images_text, content_to_analyze, url, filename)
        else:
            return self._create_generic_prompt(content_schema, images_text, content_to_analyze, url, filename)

    def _create_recipe_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create recipe-specific AI prompt."""
        return f"""Extract RECIPE content from this Costco Connection article.

**RECIPE INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**EXTRACT RECIPE DATA:**
1. Complete ingredients list with exact quantities
2. Step-by-step cooking instructions
3. Prep time, cook time, servings
4. Recipe source/author attribution
5. Any nutritional information
6. Equipment needed

**OUTPUT JSON:**
{{
  "title": "Recipe name from content",
  "featured_image": "BEST SCORED IMAGE URL",
  "image_alt": "Image description",
  "byline": "Recipe attribution",
  "description": "Brief recipe description",
  "ingredients": ["ingredient with quantity", "..."],
  "instructions": ["step 1", "step 2", "..."],
  "prep_time": "X minutes",
  "cook_time": "X minutes", 
  "servings": "X servings",
  "recipe_source": "Source attribution",
  "equipment_needed": ["equipment1", "equipment2"]
}}

**CONTENT:**
{content}

Extract ONLY actual recipe content, ignore navigation/promotional material."""

    def _create_travel_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create travel-specific AI prompt."""
        return f"""Extract TRAVEL content from this Costco Connection article.

**TRAVEL INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**EXTRACT TRAVEL DATA:**
1. Destinations mentioned
2. Attractions and landmarks
3. Restaurants and dining
4. Activities and experiences
5. Travel tips and advice
6. Cultural information
7. Best time to visit
8. Costco Travel package mentions

**OUTPUT JSON:**
{{
  "title": "Travel article title",
  "featured_image": "BEST SCORED IMAGE URL",
  "image_alt": "Image description",
  "byline": "By Costco Travel",
  "description": "Travel article summary",
  "destinations": ["city1", "city2"],
  "attractions": ["attraction1", "attraction2"],
  "restaurants": ["restaurant1", "restaurant2"],
  "activities": ["activity1", "activity2"],
  "travel_tips": ["tip1", "tip2"],
  "cultural_notes": ["note1", "note2"],
  "best_time_to_visit": "season/timeframe",
  "costco_travel_packages": ["package links or mentions"]
}}

**CONTENT:**
{content}

Focus on destination information and travel advice."""

    def _create_tech_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create tech-specific AI prompt."""
        return f"""Extract TECH/PRODUCT content from this Costco Connection article.

**TECH INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**EXTRACT TECH DATA:**
1. Products and brands mentioned
2. Key features and specifications
3. Pros and cons
4. Price ranges
5. Buying recommendations
6. Technical specifications

**OUTPUT JSON:**
{{
  "title": "Tech article title",
  "featured_image": "BEST SCORED IMAGE URL", 
  "image_alt": "Image description",
  "byline": "By Tech Connection",
  "description": "Tech article summary",
  "products": ["product1", "product2"],
  "brands": ["brand1", "brand2"],
  "features": ["feature1", "feature2"],
  "pros_and_cons": {{"pros": ["pro1"], "cons": ["con1"]}},
  "price_range": "price information",
  "specifications": {{"spec1": "value1", "spec2": "value2"}},
  "buying_guide": ["tip1", "tip2"]
}}

**CONTENT:**
{content}

Focus on product information and technical details."""

    def _create_lifestyle_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create lifestyle-specific AI prompt."""
        return f"""Extract LIFESTYLE content from this Costco Connection article.

**LIFESTYLE INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**EXTRACT LIFESTYLE DATA:**
1. Main lifestyle topics
2. Family activities mentioned
3. Wellness and health tips
4. Home improvement advice
5. Seasonal content
6. Life stage relevance

**OUTPUT JSON:**
{{
  "title": "Lifestyle article title",
  "featured_image": "BEST SCORED IMAGE URL",
  "image_alt": "Image description", 
  "byline": "By Costco Connection",
  "description": "Lifestyle article summary",
  "topics": ["topic1", "topic2"],
  "family_activities": ["activity1", "activity2"],
  "wellness_tips": ["tip1", "tip2"],
  "home_improvement": ["tip1", "tip2"],
  "seasonal_content": ["seasonal item1"],
  "life_stage": "target demographic"
}}

**CONTENT:**
{content}

Focus on lifestyle advice and family content."""

    def _create_editorial_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create editorial-specific AI prompt."""
        return f"""Extract EDITORIAL content from this Costco Connection article.

**EDITORIAL INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**EXTRACT EDITORIAL DATA:**
1. Key editorial messages
2. Costco values mentioned
3. Member benefits highlighted
4. Call to action
5. Editorial type (publisher note, opinion, etc.)

**OUTPUT JSON:**
{{
  "title": "Editorial title",
  "featured_image": "BEST SCORED IMAGE URL",
  "image_alt": "Image description",
  "byline": "By Costco Connection Editorial",
  "description": "Editorial summary",
  "key_messages": ["message1", "message2"],
  "costco_values": ["value1", "value2"],
  "member_benefits": ["benefit1", "benefit2"],
  "call_to_action": "main CTA",
  "editorial_type": "publishers-note/opinion/commentary"
}}

**CONTENT:**
{content}

Focus on editorial messaging and Costco values."""

    def _create_shopping_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create shopping-specific AI prompt."""
        return f"""Extract SHOPPING/PRODUCT content from this Costco Connection article.

**SHOPPING INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**EXTRACT SHOPPING DATA:**
1. Featured products
2. Product categories
3. Kirkland Signature items
4. Buying tips and advice
5. Seasonal items
6. Member deals mentioned

**OUTPUT JSON:**
{{
  "title": "Shopping article title",
  "featured_image": "BEST SCORED IMAGE URL",
  "image_alt": "Image description",
  "byline": "By Costco Buying Team",
  "description": "Shopping article summary",
  "featured_products": ["product1", "product2"],
  "product_categories": ["category1", "category2"],
  "kirkland_signature": ["KS product1", "KS product2"],
  "buying_tips": ["tip1", "tip2"],
  "seasonal_items": ["seasonal1", "seasonal2"],
  "member_deals": ["deal1", "deal2"]
}}

**CONTENT:**
{content}

Focus on product information and shopping advice."""

    def _create_member_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create member-specific AI prompt."""
        return f"""Extract MEMBER content from this Costco Connection article.

**MEMBER INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**EXTRACT MEMBER DATA:**
1. Poll questions and results
2. Member stories
3. Member comments
4. Community events
5. Member spotlights

**OUTPUT JSON:**
{{
  "title": "Member article title", 
  "featured_image": "BEST SCORED IMAGE URL",
  "image_alt": "Image description",
  "byline": "By Member Services",
  "description": "Member article summary",
  "poll_questions": ["question1?", "question2?"],
  "poll_results": {{"option1": "percentage", "option2": "percentage"}},
  "member_stories": ["story1", "story2"],
  "member_comments": ["comment1", "comment2"],
  "community_events": ["event1", "event2"]
}}

**CONTENT:**
{content}

Focus on member engagement and community content."""

    def _create_generic_prompt(self, content_schema, images_text: str, content: str, url: str, filename: str) -> str:
        """Create generic AI prompt for unspecified content types."""
        return f"""Extract content from this Costco Connection article.

**ARTICLE INFO:**
URL: {url}
Filename: {filename}
Current Title: {content_schema.title}

**AVAILABLE IMAGES:**
{images_text}

**OUTPUT JSON:**
{{
  "title": "Article title",
  "featured_image": "BEST SCORED IMAGE URL",
  "image_alt": "Image description", 
  "byline": "By Costco Connection",
  "description": "Article summary",
  "main_content": ["paragraph1", "paragraph2"],
  "key_topics": ["topic1", "topic2"]
}}

**CONTENT:**
{content}

Extract the main article content and key topics."""

    def call_ai(self, prompt: str) -> Optional[Dict]:
        """Call Claude AI via AWS Bedrock."""
        if not self.bedrock:
            return None

        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": AI_CONFIG['max_tokens'],
                "messages": [{"role": "user", "content": prompt}],
                "temperature": AI_CONFIG['temperature']
            })

            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                contentType="application/json",
                accept="application/json", 
                body=body
            )

            response_body = json.loads(response.get('body').read())
            ai_text = response_body.get('content')[0].get('text')

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', ai_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            logger.warning("No valid JSON found in AI response")
            return None
            
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            return None

    def _merge_ai_results(self, content_schema, ai_result: Dict, content_type: ContentType):
        """Merge AI results with existing schema."""
        try:
            # Update basic fields
            if 'title' in ai_result:
                content_schema.title = ai_result['title']
            if 'featured_image' in ai_result:
                content_schema.featured_image = ai_result['featured_image']
            if 'image_alt' in ai_result:
                content_schema.image_alt = ai_result['image_alt']
            if 'description' in ai_result:
                content_schema.description = ai_result['description']

            # Update content-type specific fields
            if content_type == ContentType.RECIPE and isinstance(content_schema, RecipeContent):
                if 'ingredients' in ai_result:
                    content_schema.ingredients = ai_result['ingredients']
                if 'instructions' in ai_result:
                    content_schema.instructions = ai_result['instructions']
                if 'prep_time' in ai_result:
                    content_schema.prep_time = ai_result['prep_time']
                if 'cook_time' in ai_result:
                    content_schema.cook_time = ai_result['cook_time']
                if 'servings' in ai_result:
                    content_schema.servings = ai_result['servings']

            elif content_type == ContentType.TRAVEL and isinstance(content_schema, TravelContent):
                if 'destinations' in ai_result:
                    content_schema.destinations = ai_result['destinations']
                if 'attractions' in ai_result:
                    content_schema.attractions = ai_result['attractions']
                if 'travel_tips' in ai_result:
                    content_schema.travel_tips = ai_result['travel_tips']

            # Similar for other content types...

            return content_schema

        except Exception as e:
            logger.error(f"Error merging AI results: {e}")
            return content_schema

    def _build_enhanced_structure(self, url: str, content_schema, detection_metadata: Dict, 
                                soup: BeautifulSoup) -> EnhancedPageStructure:
        """Build enhanced page structure."""
        
        # Extract sections from content
        sections = []
        for heading in soup.find_all(['h2', 'h3'])[:5]:
            text = heading.get_text().strip()
            if text:
                sections.append({
                    'heading': text,
                    'level': int(heading.name[1])
                })

        # Calculate quality score
        quality_score = self._calculate_enhanced_quality_score(content_schema, detection_metadata)

        # Build extraction metadata
        extraction_metadata = {
            'extraction_timestamp': __import__('time').time(),
            'content_type': content_schema.content_type.value,
            'detection_confidence': detection_metadata.get('confidence_score', 0),
            'ai_enhanced': self.bedrock is not None,
            'extraction_method': 'enhanced_costco_ai'
        }

        return EnhancedPageStructure(
            url=url,
            content=content_schema,
            sections=sections,
            content_quality_score=quality_score,
            extraction_metadata=extraction_metadata
        )

    def _calculate_enhanced_quality_score(self, content_schema, detection_metadata: Dict) -> int:
        """Calculate enhanced quality score."""
        score = 40  # Base score
        
        # Content completeness
        if content_schema.title:
            score += 15
        if content_schema.description:
            score += 10
        if content_schema.featured_image:
            score += 15
            
        # Content-type specific scoring
        if content_schema.content_type == ContentType.RECIPE:
            if hasattr(content_schema, 'ingredients') and content_schema.ingredients:
                score += 10
            if hasattr(content_schema, 'instructions') and content_schema.instructions:
                score += 10
        elif content_schema.content_type == ContentType.TRAVEL:
            if hasattr(content_schema, 'destinations') and content_schema.destinations:
                score += 10
                
        # Detection confidence bonus
        confidence = detection_metadata.get('confidence_score', 0)
        score += min(confidence // 10, 10)
        
        return min(score, 100)