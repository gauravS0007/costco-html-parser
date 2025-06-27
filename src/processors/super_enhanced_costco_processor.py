"""
FIXED: Super Enhanced Costco Processor with proper content type detection and image handling
"""

import json
import re
import logging
import boto3
from bs4 import BeautifulSoup
from typing import Optional, Dict, Union
from dataclasses import asdict

from ..config.settings import AWS_REGION, BEDROCK_MODEL_ID, AI_CONFIG
from ..utils.enhanced_content_detector import EnhancedContentDetector
from ..models.content_schemas import (
    ContentType, EnhancedPageStructure, RecipeContent, TravelContent, 
    TechContent, LifestyleContent, EditorialContent, ShoppingContent, MemberContent
)

# Import the FIXED universal extractor
from ..utils.universal_content_extractor import FixedUniversalContentExtractor, ExtractedContent

logger = logging.getLogger(__name__)


class FixedSuperEnhancedCostcoProcessor:
    """FIXED: Super Enhanced Costco processor with proper extraction"""

    def __init__(self):
        """Initialize processor with AWS Bedrock and fixed universal extractor."""
        try:
            self.bedrock = boto3.client(
                service_name='bedrock-runtime',
                region_name=AWS_REGION
            )
            self.model_id = BEDROCK_MODEL_ID
            self.content_detector = EnhancedContentDetector()
            self.universal_extractor = FixedUniversalContentExtractor()
            logger.info("🚀 FIXED Super Enhanced Costco processor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize processor: {e}")
            self.bedrock = None

    def process_content(self, html_content: str, url: str, filename: str) -> Optional[EnhancedPageStructure]:
        """
        FIXED: Process content with proper extraction and content type detection.
        """
        try:
            logger.info(f"🔧 FIXED processing for {filename}")
            
            # Step 1: Use FIXED universal content extraction
            extracted_content = self.universal_extractor.extract_all_content(html_content, url)
            
            # Step 2: Map content type to schema enum with FIXED mapping
            content_type_enum = self._map_content_type_fixed(extracted_content.content_type, filename, url)
            
            # Step 3: Build enhanced content schema from extracted data
            content_schema = self._build_content_schema_fixed(
                extracted_content, content_type_enum, filename, url
            )
            
            # Step 4: Enhance with AI if available
            if self.bedrock:
                ai_enhanced_content = self._enhance_with_ai_fixed(
                    content_schema, extracted_content, content_type_enum, url, filename
                )
                if ai_enhanced_content:
                    content_schema = ai_enhanced_content
            
            # Step 5: Build comprehensive page structure
            page_structure = self._build_enhanced_structure_fixed(
                url, content_schema, extracted_content
            )
            
            logger.info(f"✅ FIXED processing complete: {content_type_enum.value} - "
                       f"Quality: {page_structure.content_quality_score}")
            
            return page_structure

        except Exception as e:
            logger.error(f"❌ FIXED processing failed for {filename}: {e}")
            return None

    def _map_content_type_fixed(self, detected_type: str, filename: str, url: str) -> ContentType:
        """FIXED: Enhanced content type mapping with filename and URL analysis"""
        
        filename_lower = filename.lower()
        url_lower = url.lower()
        
        # Priority 1: URL-based detection (most reliable)
        if 'recipe' in url_lower or 'recipe' in filename_lower:
            return ContentType.RECIPE
        elif 'travel-connection' in url_lower or 'tale-of' in url_lower:
            return ContentType.TRAVEL
        elif 'tech' in url_lower or 'power-up' in url_lower:
            return ContentType.TECH
        elif 'publisher' in url_lower or 'publishers-note' in url_lower:
            return ContentType.EDITORIAL
        elif 'member-poll' in url_lower or 'member-comments' in url_lower or 'member-connection' in url_lower:
            return ContentType.MEMBER
        elif 'treasure-hunt' in url_lower or 'buying-smart' in url_lower:
            return ContentType.SHOPPING
        elif 'costco-life' in url_lower or 'fye' in url_lower or 'strong-women' in url_lower:
            return ContentType.LIFESTYLE
        
        # Priority 2: Detected type mapping
        type_mapping = {
            'recipe': ContentType.RECIPE,
            'travel': ContentType.TRAVEL,
            'tech': ContentType.TECH,
            'editorial': ContentType.EDITORIAL,
            'member': ContentType.MEMBER,
            'shopping': ContentType.SHOPPING,
            'lifestyle': ContentType.LIFESTYLE
        }
        
        if detected_type in type_mapping:
            return type_mapping[detected_type]
        
        # Priority 3: Fallback based on filename patterns
        if 'front-cover' in filename_lower or 'edition' in filename_lower:
            return ContentType.EDITORIAL
        elif 'supplier' in filename_lower or 'spotlight' in filename_lower:
            return ContentType.LIFESTYLE
        
        # Default
        return ContentType.EDITORIAL

    def _build_content_schema_fixed(self, extracted: ExtractedContent, content_type: ContentType, 
                                   filename: str, url: str):
        """FIXED: Build content schema with proper data extraction"""
        
        # Enhanced base data extraction
        base_data = {
            'title': extracted.title or self._extract_title_from_filename(filename),
            'headline': extracted.title or "",
            'byline': extracted.byline or self._get_default_byline(content_type),
            'description': self._create_description_from_content(extracted.main_content),
            'featured_image': self._get_best_image_url(extracted.images),
            'image_alt': self._get_best_image_alt(extracted.images),
            'content_type': content_type,
            'publish_date': self._extract_date_from_filename(filename)
        }
        
        # Create content-specific schema with FIXED extraction
        if content_type == ContentType.RECIPE:
            return self._build_recipe_schema_fixed(extracted, base_data)
        elif content_type == ContentType.TRAVEL:
            return self._build_travel_schema_fixed(extracted, base_data)
        elif content_type == ContentType.TECH:
            return self._build_tech_schema_fixed(extracted, base_data)
        elif content_type == ContentType.LIFESTYLE:
            return self._build_lifestyle_schema_fixed(extracted, base_data)
        elif content_type == ContentType.EDITORIAL:
            return self._build_editorial_schema_fixed(extracted, base_data)
        elif content_type == ContentType.SHOPPING:
            return self._build_shopping_schema_fixed(extracted, base_data)
        elif content_type == ContentType.MEMBER:
            return self._build_member_schema_fixed(extracted, base_data)
        else:
            from ..models.content_schemas import BaseContent
            return BaseContent(**base_data)

    def _build_recipe_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> RecipeContent:
        """FIXED: Recipe content extraction with proper ingredient/instruction separation"""
        
        # Get ingredients and instructions from metadata (properly extracted)
        ingredients = extracted.metadata.get('ingredients', [])
        instructions = extracted.metadata.get('instructions', [])
        
        # Fallback extraction from lists if metadata is empty
        if not ingredients or not instructions:
            for list_data in extracted.lists:
                list_text = ' '.join(list_data['items']).lower()
                
                # Check if this list contains ingredients (has measurements)
                has_measurements = any(unit in list_text for unit in 
                                     ['cup', 'tablespoon', 'teaspoon', 'ounce', 'pound'])
                
                if has_measurements and not ingredients:
                    ingredients = list_data['items']
                elif list_data['type'] == 'ordered' and not instructions and not has_measurements:
                    instructions = list_data['items']
        
        # Extract timing information
        prep_time = extracted.metadata.get('prep_time', '')
        cook_time = extracted.metadata.get('cook_time', '')
        servings = extracted.metadata.get('servings', '')
        
        return RecipeContent(
            **base_data,
            ingredients=ingredients[:15],  # Reasonable limit
            instructions=instructions[:10],
            prep_time=prep_time,
            cook_time=cook_time,
            servings=servings,
            recipe_source=extracted.author_details or base_data['byline']
        )

    def _build_travel_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> TravelContent:
        """FIXED: Travel content extraction"""
        
        destinations = extracted.metadata.get('destinations', [])
        attractions = extracted.metadata.get('attractions', [])
        
        # Extract travel tips from content
        travel_tips = []
        for content in extracted.main_content:
            if any(tip_word in content.lower() for tip_word in ['tip:', 'advice', 'recommend', 'best time']):
                travel_tips.append(content)
        
        # Extract cultural notes
        cultural_notes = []
        for content in extracted.main_content:
            if any(culture_word in content.lower() for culture_word in 
                  ['culture', 'history', 'heritage', 'tradition', 'historic']):
                cultural_notes.append(content)
        
        return TravelContent(
            **base_data,
            destinations=destinations[:5],
            attractions=attractions[:10],
            travel_tips=travel_tips[:3],
            cultural_notes=cultural_notes[:3]
        )

    def _build_tech_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> TechContent:
        """FIXED: Tech content extraction"""
        
        products = extracted.metadata.get('products', [])
        features = extracted.metadata.get('features', [])
        brands = extracted.metadata.get('brands', [])
        
        # Build buying guide from relevant content
        buying_guide = []
        for content in extracted.main_content:
            if any(guide_word in content.lower() for guide_word in 
                  ['recommend', 'choose', 'buy', 'purchase', 'consider']):
                buying_guide.append(content)
        
        return TechContent(
            **base_data,
            products=products[:8],
            brands=brands,
            features=features[:12],
            buying_guide=buying_guide[:3]
        )

    def _build_lifestyle_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> LifestyleContent:
        """FIXED: Lifestyle content extraction"""
        
        topics = [heading['text'] for heading in extracted.headings[:8]]
        
        # Extract family activities
        family_activities = []
        for content in extracted.main_content:
            if any(family_word in content.lower() for family_word in 
                  ['family', 'children', 'kids', 'celebrate', 'activity']):
                family_activities.append(content)
        
        return LifestyleContent(
            **base_data,
            topics=topics,
            family_activities=family_activities[:5]
        )

    def _build_editorial_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> EditorialContent:
        """FIXED: Editorial content extraction"""
        
        key_messages = extracted.main_content[:3]  # First few paragraphs
        
        # Extract Costco values
        costco_values = []
        for content in extracted.main_content:
            if any(value_word in content.lower() for value_word in 
                  ['value', 'member', 'quality', 'service', 'costco']):
                costco_values.append(content)
        
        return EditorialContent(
            **base_data,
            key_messages=key_messages,
            costco_values=costco_values[:3]
        )

    def _build_shopping_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> ShoppingContent:
        """FIXED: Shopping content extraction"""
        
        featured_products = []
        kirkland_signature = []
        
        # Extract product information
        for content in extracted.main_content:
            if 'kirkland signature' in content.lower():
                kirkland_signature.append(content)
            elif any(product_word in content.lower() for product_word in 
                    ['product', 'item', 'brand', 'sofa', 'cookware']):
                featured_products.append(content)
        
        # Extract from headings (often product names)
        for heading in extracted.headings:
            if any(product_indicator in heading['text'].lower() for product_indicator in 
                  ['sofa', 'skillet', 'throw', 'seasoned']):
                featured_products.append(heading['text'])
        
        return ShoppingContent(
            **base_data,
            featured_products=featured_products[:8],
            kirkland_signature=kirkland_signature[:3]
        )

    def _build_member_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> MemberContent:
        """FIXED: Member content extraction"""
        
        poll_questions = extracted.metadata.get('poll_questions', [])
        member_comments = extracted.metadata.get('member_comments', [])
        
        # Extract poll results if available
        poll_results = {}
        for content in extracted.main_content:
            if '%' in content or 'percent' in content.lower():
                poll_results['response'] = content
        
        return MemberContent(
            **base_data,
            poll_questions=poll_questions[:3],
            member_comments=member_comments[:5],
            poll_results=poll_results
        )

    def _enhance_with_ai_fixed(self, content_schema, extracted_content: ExtractedContent, 
                              content_type: ContentType, url: str, filename: str):
        """FIXED: AI enhancement with better prompts"""
        try:
            prompt = self._create_ai_prompt_fixed(
                content_schema, extracted_content, content_type, url, filename
            )
            
            ai_result = self.call_ai(prompt)
            if not ai_result:
                return None

            enhanced_schema = self._merge_ai_results_fixed(content_schema, ai_result, content_type)
            return enhanced_schema

        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return None

    def _create_ai_prompt_fixed(self, content_schema, extracted: ExtractedContent, 
                               content_type: ContentType, url: str, filename: str) -> str:
        """FIXED: Create enhanced AI prompts"""
        
        # Get best images for AI
        best_images = sorted(extracted.images, key=lambda x: x['score'], reverse=True)[:5]
        images_text = self._format_images_for_ai_fixed(best_images)
        
        # Get main content summary
        content_preview = '\n'.join(extracted.main_content[:3])
        
        base_prompt = f"""ENHANCE this {content_type.value.upper()} content from Costco Connection magazine.

**SOURCE INFO:**
URL: {url}
Filename: {filename}
Extracted Title: "{extracted.title}"
Byline: "{extracted.byline}"

**AVAILABLE IMAGES (prioritized by relevance):**
{images_text}

**CONTENT PREVIEW:**
{content_preview}

**TASK:** Enhance and refine the extracted data. Use the BEST scoring image as featured_image.
"""

        # Content-type specific enhancement
        if content_type == ContentType.RECIPE:
            ingredients = getattr(content_schema, 'ingredients', [])
            instructions = getattr(content_schema, 'instructions', [])
            
            base_prompt += f"""
**RECIPE DATA:**
Ingredients Found: {len(ingredients)}
Instructions Found: {len(instructions)}

**OUTPUT (JSON only):**
{{
  "title": "Clear recipe name",
  "featured_image": "HIGHEST SCORING IMAGE URL",
  "image_alt": "Image description",
  "ingredients": ["refined ingredient list with measurements"],
  "instructions": ["step-by-step cooking instructions"],
  "prep_time": "preparation time",
  "cook_time": "cooking time",
  "servings": "number of servings"
}}"""

        elif content_type == ContentType.TRAVEL:
            destinations = getattr(content_schema, 'destinations', [])
            
            base_prompt += f"""
**TRAVEL DATA:**
Destinations Found: {destinations}

**OUTPUT (JSON only):**
{{
  "title": "Travel article title",
  "featured_image": "HIGHEST SCORING IMAGE URL",
  "image_alt": "Image description",
  "destinations": ["city/location names"],
  "attractions": ["tourist attractions mentioned"],
  "cultural_notes": ["cultural information"],
  "travel_tips": ["practical travel advice"]
}}"""

        elif content_type == ContentType.TECH:
            base_prompt += f"""
**OUTPUT (JSON only):**
{{
  "title": "Tech article title",
  "featured_image": "HIGHEST SCORING IMAGE URL",
  "image_alt": "Image description",
  "products": ["technology products mentioned"],
  "features": ["product features"],
  "buying_guide": ["purchasing recommendations"]
}}"""

        else:  # Editorial, Member, Shopping, Lifestyle
            base_prompt += f"""
**OUTPUT (JSON only):**
{{
  "title": "Article title",
  "featured_image": "HIGHEST SCORING IMAGE URL",
  "image_alt": "Image description",
  "description": "Enhanced article description"
}}"""

        base_prompt += "\n\nProvide ONLY valid JSON. Use the highest scoring image as featured_image."
        return base_prompt

    def _format_images_for_ai_fixed(self, images: list) -> str:
        """FIXED: Format images for AI with clear scoring"""
        if not images:
            return "No quality images found"
        
        formatted = []
        for i, img in enumerate(images):
            score = img['score']
            marker = "🥇 BEST" if i == 0 else f"#{i+1}"
            formatted.append(f"{marker} (Score: {score}): {img['src']}")
            if img['alt']:
                formatted.append(f"    Alt: {img['alt']}")
        
        return '\n'.join(formatted)

    def _merge_ai_results_fixed(self, content_schema, ai_result: Dict, content_type: ContentType):
        """FIXED: Merge AI results with validation"""
        try:
            # Always update basic fields if provided
            if 'title' in ai_result and ai_result['title'].strip():
                content_schema.title = ai_result['title'].strip()
            
            if 'featured_image' in ai_result and ai_result['featured_image'].strip():
                content_schema.featured_image = ai_result['featured_image'].strip()
            
            if 'image_alt' in ai_result and ai_result['image_alt'].strip():
                content_schema.image_alt = ai_result['image_alt'].strip()
            
            if 'description' in ai_result and ai_result['description'].strip():
                content_schema.description = ai_result['description'].strip()

            # Content-type specific merging
            if content_type == ContentType.RECIPE:
                for field in ['ingredients', 'instructions']:
                    if field in ai_result and ai_result[field]:
                        setattr(content_schema, field, ai_result[field])
                
                for field in ['prep_time', 'cook_time', 'servings']:
                    if field in ai_result and ai_result[field]:
                        setattr(content_schema, field, ai_result[field])

            elif content_type == ContentType.TRAVEL:
                for field in ['destinations', 'attractions', 'cultural_notes', 'travel_tips']:
                    if field in ai_result and ai_result[field]:
                        setattr(content_schema, field, ai_result[field])

            elif content_type == ContentType.TECH:
                for field in ['products', 'features', 'buying_guide']:
                    if field in ai_result and ai_result[field]:
                        setattr(content_schema, field, ai_result[field])

            return content_schema

        except Exception as e:
            logger.error(f"Error merging AI results: {e}")
            return content_schema

    def _build_enhanced_structure_fixed(self, url: str, content_schema, 
                                       extracted: ExtractedContent) -> EnhancedPageStructure:
        """FIXED: Build comprehensive page structure"""
        
        # Build sections from headings
        sections = []
        for heading in extracted.headings[:15]:
            sections.append({
                'heading': heading['text'],
                'level': heading['level']
            })

        # Calculate comprehensive quality score
        quality_score = self._calculate_quality_score_fixed(content_schema, extracted)

        # Build detailed extraction metadata
        extraction_metadata = {
            'extraction_timestamp': __import__('time').time(),
            'content_type': content_schema.content_type.value,
            'universal_extraction': True,
            'ai_enhanced': self.bedrock is not None,
            'extraction_method': 'fixed_super_enhanced',
            'content_stats': {
                'paragraphs_extracted': len(extracted.main_content),
                'images_found': len(extracted.images),
                'headings_found': len(extracted.headings),
                'lists_found': len(extracted.lists),
                'quotes_found': len(extracted.quotes)
            },
            'best_image_score': max([img['score'] for img in extracted.images]) if extracted.images else 0,
            'author_details_found': bool(extracted.author_details),
            'byline_found': bool(extracted.byline)
        }

        return EnhancedPageStructure(
            url=url,
            content=content_schema,
            sections=sections,
            content_quality_score=quality_score,
            extraction_metadata=extraction_metadata
        )

    def _calculate_quality_score_fixed(self, content_schema, extracted: ExtractedContent) -> int:
        """FIXED: Comprehensive quality scoring"""
        score = 20  # Base score
        
        # Content completeness
        if content_schema.title:
            score += 15
        if content_schema.description and len(content_schema.description) > 50:
            score += 10
        if content_schema.featured_image:
            score += 20  # Higher weight for images
        if content_schema.byline:
            score += 5
            
        # Extracted content richness
        score += min(len(extracted.main_content) * 2, 20)  # Up to 20 for content
        score += min(len(extracted.images) * 3, 15)        # Up to 15 for images
        score += min(len(extracted.headings) * 2, 10)      # Up to 10 for structure
        
        # Best image quality bonus
        if extracted.images:
            best_img_score = max([img['score'] for img in extracted.images])
            if best_img_score > 100:
                score += 15
            elif best_img_score > 50:
                score += 10
            else:
                score += 5
        
        # Content-specific bonuses
        if content_schema.content_type == ContentType.RECIPE:
            if hasattr(content_schema, 'ingredients') and content_schema.ingredients:
                score += 10
            if hasattr(content_schema, 'instructions') and content_schema.instructions:
                score += 10
        elif content_schema.content_type == ContentType.TRAVEL:
            if hasattr(content_schema, 'destinations') and content_schema.destinations:
                score += 10
        
        return min(score, 100)

    def call_ai(self, prompt: str) -> Optional[Dict]:
        """Call Claude AI via AWS Bedrock"""
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

    # Helper methods
    def _extract_title_from_filename(self, filename: str) -> str:
        """Extract title from filename"""
        # Clean up filename
        name = filename.replace('.html', '').replace('connection-', '')
        name = re.sub(r'---.*', '', name)  # Remove trailing parts
        name = name.replace('-', ' ').replace('_', ' ')
        
        # Capitalize words
        words = name.split()
        title_words = []
        for word in words:
            if word.lower() not in ['costco', 'html', 'www', 'com']:
                title_words.append(word.capitalize())
        
        return ' '.join(title_words)

    def _get_default_byline(self, content_type: ContentType) -> str:
        """Get default byline for content type"""
        bylines = {
            ContentType.RECIPE: "By Costco Kitchen Team",
            ContentType.TRAVEL: "By Costco Travel",
            ContentType.TECH: "By Tech Connection",
            ContentType.EDITORIAL: "By Costco Connection Editorial",
            ContentType.SHOPPING: "By Costco Buying Team",
            ContentType.MEMBER: "By Member Services",
            ContentType.LIFESTYLE: "By Costco Connection"
        }
        return bylines.get(content_type, "By Costco Connection")

    def _create_description_from_content(self, main_content: list) -> str:
        """Create description from main content"""
        if not main_content:
            return ""
        
        # Find the best paragraph for description
        for content in main_content:
            # Skip very short or very long paragraphs
            if 50 < len(content) < 300:
                return content
        
        # Fallback to first substantial paragraph
        for content in main_content:
            if len(content) > 100:
                return content[:200] + "..." if len(content) > 200 else content
        
        return main_content[0] if main_content else ""

    def _get_best_image_url(self, images: list) -> str:
        """Get the highest scoring image URL"""
        if not images:
            return ""
        
        # Images are already sorted by score
        best_image = images[0]
        logger.info(f"🖼️ Selected best image (score: {best_image['score']}): {best_image['src']}")
        return best_image['src']

    def _get_best_image_alt(self, images: list) -> str:
        """Get the highest scoring image alt text"""
        if not images:
            return ""
        return images[0]['alt']

    def _extract_date_from_filename(self, filename: str) -> str:
        """Extract date from filename"""
        # Look for month-year patterns
        date_patterns = [
            r'(\w+)-(\d{4})',  # october-2023
            r'(\d{2})_(\d{2})', # 10_23
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, filename.lower())
            if match:
                if len(match.group(1)) > 2:  # Month name
                    return f"{match.group(1).capitalize()} {match.group(2)}"
                else:  # Month number
                    month_names = {
                        '01': 'January', '02': 'February', '03': 'March', '04': 'April',
                        '05': 'May', '06': 'June', '07': 'July', '08': 'August',
                        '09': 'September', '10': 'October', '11': 'November', '12': 'December'
                    }
                    month_name = month_names.get(match.group(1), 'Unknown')
                    year = f"20{match.group(2)}"
                    return f"{month_name} {year}"
        
        return ""


# Integration function for existing codebase
def create_fixed_processor():
    """Factory function to create the fixed processor"""
    return FixedSuperEnhancedCostcoProcessor()


# Example usage
if __name__ == "__main__":
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Test with sample content
    test_html = """
    <html>
        <head><title>Spinach Lasagna Roll Ups | Costco</title></head>
        <body>
            <article>
                <h1>Spinach Lasagna Roll Ups</h1>
                <p>Recipe and photo courtesy of Kylie Lato</p>
                <ul>
                    <li>8 lasagna noodles</li>
                    <li>2 cups ricotta cheese</li>
                </ul>
                <img src="/live/resource/img/10_23_recipe.jpg" alt="Delicious lasagna" />
            </article>
        </body>
    </html>
    """
    
    result = processor.process_content(
        test_html, 
        "https://www.costco.com/recipe-spinach-lasagna-roll-ups", 
        "recipe-spinach-lasagna-roll-ups-october-2023.html"
    )
    
    if result:
        print(f"✅ Title: {result.content.title}")
        print(f"✅ Type: {result.content.content_type}")
        print(f"✅ Image: {result.content.featured_image}")
        print(f"✅ Quality: {result.content_quality_score}")
    else:
        print("❌ Processing failed")