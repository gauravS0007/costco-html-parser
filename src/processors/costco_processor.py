"""
Main Costco content processor with AI intelligence.
"""

import json
import re
import logging
import boto3
from bs4 import BeautifulSoup
from typing import Optional, Dict

from ..config.settings import AWS_REGION, BEDROCK_MODEL_ID, AI_CONFIG, ARTICLE_SELECTORS, NAVIGATION_TERMS
from ..utils.image_utils import fix_image_urls, get_scored_images, format_images_for_ai
from ..utils.content_detector import detect_content_type

logger = logging.getLogger(__name__)


class CostcoProcessor:
    """Clean Costco-specific content processor with AI integration."""

    def __init__(self):
        """Initialize processor with AWS Bedrock client."""
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=AWS_REGION
            )
            self.model_id = BEDROCK_MODEL_ID
            logger.info("AWS Bedrock initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock: {e}")
            self.bedrock = None

    def find_article_area(self, soup: BeautifulSoup):
        """
        Find the main article content area in the HTML.
        
        Args:
            soup: BeautifulSoup object of the page
            
        Returns:
            BeautifulSoup element containing the main content
        """
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
        """Find the best content container using scoring algorithm."""
        all_divs = soup.find_all(['div', 'section', 'main'])
        best_container = None
        best_score = 0

        for div in all_divs:
            # Skip navigation areas
            class_names = ' '.join(div.get('class', [])).lower()
            if any(skip in class_names for skip in NAVIGATION_TERMS):
                continue

            # Score content quality
            paragraphs = len(div.find_all('p'))
            headings = len(div.find_all(['h1', 'h2', 'h3']))
            text_length = len(div.get_text().strip())

            score = paragraphs * 5 + headings * 10 + min(text_length // 100, 50)

            if score > best_score and text_length > 200:
                best_score = score
                best_container = div

        if best_container:
            logger.info(f"Found best content area (score: {best_score})")
            return best_container

        return soup.find('body')

    def extract_headings(self, article_area) -> str:
        """
        Extract headings from article area.
        
        Args:
            article_area: Main article content area
            
        Returns:
            Formatted headings string
        """
        headings_list = []
        
        if article_area:
            for tag in article_area.find_all(['h1', 'h2', 'h3'])[:10]:
                text = tag.get_text().strip()
                if text and len(text) > 3:
                    # Skip navigation headings
                    if not any(nav in text.lower() for nav in NAVIGATION_TERMS):
                        headings_list.append(f"H{tag.name[1]}: {text}")

        return '\n'.join(headings_list) if headings_list else "No headings found"

    def create_ai_prompt(self, html_content: str, url: str, filename: str) -> str:
        """
        Create AI prompt for content extraction.
        
        Args:
            html_content: HTML content to process
            url: Page URL
            filename: Source filename
            
        Returns:
            Formatted AI prompt
        """
        # Fix images and find article area
        fixed_html = fix_image_urls(html_content, url)
        soup = BeautifulSoup(fixed_html, 'html.parser')
        article_area = self.find_article_area(soup)

        # Detect content type
        content_info = detect_content_type(html_content, url, filename)
        content_type = content_info['content_type']
        byline = content_info['byline']

        # Get and score images
        scored_images = get_scored_images(soup, article_area, content_type)
        images_text = format_images_for_ai(scored_images, AI_CONFIG['max_images_to_analyze'])

        # Extract headings
        headings_text = self.extract_headings(article_area)

        # Build prompt
        prompt = self._build_extraction_prompt(
            url, filename, content_type, byline, 
            images_text, headings_text, article_area, fixed_html
        )

        return prompt

    def _build_extraction_prompt(self, url: str, filename: str, content_type: str, 
                                byline: str, images_text: str, headings_text: str,
                                article_area, fixed_html: str) -> str:
        """Build the complete AI extraction prompt."""
        
        content_to_analyze = (
            str(article_area)[:AI_CONFIG['max_content_length']] 
            if article_area 
            else fixed_html[:AI_CONFIG['max_content_length']]
        )

        return f"""Extract content from this Costco Connection {content_type.upper()} article.

**ARTICLE INFO:**
URL: {url}
Filename: {filename}
Content Type: {content_type}

**AVAILABLE IMAGES (🎯/⭐ = use these, ❌ = avoid):**
{images_text}

**ARTICLE HEADINGS:**
{headings_text}

**EXTRACTION RULES:**
1. Use ONLY 🎯 PERFECT or ⭐ EXCELLENT images
2. Never use ❌ POOR images (promotional/nav content)
3. Extract real article headings, not website navigation
4. Title should match actual article content

**OUTPUT (JSON only):**
{{
  "banner": {{
    "title": "Article title from content",
    "url": "BEST SCORED IMAGE URL",
    "alt": "Exact alt text from image",
    "headline": "Main article headline",
    "byline": "{byline}",
    "description": "Brief article description"
  }},
  "headlines": [
    {{"headline_text": "Content headings only", "level": 1}}
  ],
  "teasers": []
}}

**CONTENT TO ANALYZE:**
{content_to_analyze}

Focus on actual article content, ignore promotional material."""

    def call_ai(self, prompt: str) -> Optional[Dict]:
        """
        Call Claude AI via AWS Bedrock.
        
        Args:
            prompt: AI prompt to send
            
        Returns:
            Parsed AI response or None if failed
        """
        if not self.bedrock:
            logger.error("Bedrock client not initialized")
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