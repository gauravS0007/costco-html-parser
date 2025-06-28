"""
FIXED: Super Enhanced Costco Processor with Conservative AI Merging
This fixes the AI over-processing issues and improves recipe handling.
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
    """FIXED: Super Enhanced Costco processor with conservative AI merging"""

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
        FIXED: Process content with improved extraction and conservative AI merging.
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
            
            # Step 4: Conservative AI enhancement (only if extraction failed)
            if self.bedrock and self._should_use_ai_enhancement(content_schema, extracted_content):
                ai_enhanced_content = self._enhance_with_ai_conservative(
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

    def _should_use_ai_enhancement(self, content_schema, extracted_content: ExtractedContent) -> bool:
        """Determine if AI enhancement is needed (conservative approach)"""
        
        # Only use AI if extraction failed or is clearly incomplete
        needs_ai = False
        
        # Check if basic fields are missing
        if not content_schema.title or len(content_schema.title) < 5:
            needs_ai = True
            
        # Check content-type specific needs
        if content_schema.content_type == ContentType.RECIPE:
            ingredients = getattr(content_schema, 'ingredients', [])
            instructions = getattr(content_schema, 'instructions', [])
            
            # Only use AI if we have no ingredients or instructions
            if len(ingredients) < 2 or len(instructions) < 1:
                needs_ai = True
                logger.info("AI enhancement needed: recipe missing ingredients/instructions")
        
        if needs_ai:
            logger.info("AI enhancement will be used")
        else:
            logger.info("Skipping AI enhancement - extraction looks good")
            
        return needs_ai

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
        
        # FIXED: Don't use placeholder bylines
        if base_data['byline'] and 'lotions & creams' in base_data['byline'].lower():
            base_data['byline'] = self._get_default_byline(content_type)
        
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
        
        # Extract timing information
        prep_time = extracted.metadata.get('prep_time', '')
        cook_time = extracted.metadata.get('cook_time', '')
        servings = extracted.metadata.get('servings', '')
        
        logger.info(f"Building recipe schema: {len(ingredients)} ingredients, {len(instructions)} instructions")
        
        return RecipeContent(
            **base_data,
            ingredients=ingredients[:20],  # Reasonable limit
            instructions=instructions[:15],
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

    def _enhance_with_ai_conservative(self, content_schema, extracted_content: ExtractedContent, 
                                     content_type: ContentType, url: str, filename: str):
        """FIXED: Conservative AI enhancement - only use when extraction fails"""
        try:
            prompt = self._create_ai_prompt_conservative(
                content_schema, extracted_content, content_type, url, filename
            )
            
            ai_result = self.call_ai(prompt)
            if not ai_result:
                return None

            enhanced_schema = self._merge_ai_results_conservative(content_schema, ai_result, content_type)
            return enhanced_schema

        except Exception as e:
            logger.error(f"AI enhancement failed: {e}")
            return None

    def _create_ai_prompt_conservative(self, content_schema, extracted: ExtractedContent, 
                                      content_type: ContentType, url: str, filename: str) -> str:
        """FIXED: Create conservative AI prompts that don't override good extraction"""
        
        # Get best images for AI
        best_images = sorted(extracted.images, key=lambda x: x['score'], reverse=True)[:5]
        images_text = self._format_images_for_ai_fixed(best_images)
        
        # Get main content summary
        content_preview = '\n'.join(extracted.main_content[:3])
        
        base_prompt = f"""ENHANCE MISSING FIELDS ONLY for this {content_type.value.upper()} content from Costco Connection magazine.

**SOURCE INFO:**
URL: {url}
Filename: {filename}
Current Title: "{content_schema.title}"
Current Byline: "{content_schema.byline}"

**AVAILABLE IMAGES (use HIGHEST scoring):**
{images_text}

**CRITICAL RULES:**
1. ONLY provide fields that are currently missing or empty
2. DO NOT modify existing good data
3. DO NOT generate fake bylines - only use real attribution from content
4. Extract ingredients and instructions EXACTLY as written
5. If you find recipe sections (FILLING, STREUSEL, CAKE), preserve ALL sections

**CONTENT PREVIEW:**
{content_preview}

**TASK:** Fill in missing fields only. Use HIGHEST scoring image as featured_image.
"""

        # Content-type specific enhancement
        if content_type == ContentType.RECIPE:
            current_ingredients = getattr(content_schema, 'ingredients', [])
            current_instructions = getattr(content_schema, 'instructions', [])
            
            base_prompt += f"""
**CURRENT RECIPE DATA:**
Ingredients: {len(current_ingredients)} found
Instructions: {len(current_instructions)} found

**OUTPUT (JSON only) - ONLY provide missing fields:**
{{
  "title": "Only if current title is missing or generic",
  "featured_image": "HIGHEST SCORING IMAGE URL (if image missing)",
  "image_alt": "Only if missing",
  "ingredients": ["Only if current ingredients list is empty", "preserve all sections like FILLING, STREUSEL"],
  "instructions": ["Only if current instructions are empty", "exact steps as written"],
  "prep_time": "Only if missing",
  "cook_time": "Only if missing",
  "servings": "Only if missing"
}}"""

        else:
            base_prompt += f"""
**OUTPUT (JSON only) - ONLY provide missing fields:**
{{
  "title": "Only if current title is missing",
  "featured_image": "HIGHEST SCORING IMAGE URL (if missing)",
  "image_alt": "Only if missing",
  "description": "Only if current description is missing"
}}"""

        base_prompt += "\n\nProvide ONLY missing fields. Do not override existing good data."
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

    def _merge_ai_results_conservative(self, content_schema, ai_result: Dict, content_type: ContentType):
        """FIXED: Conservative merging - prefer extracted data over AI"""
        try:
            # Only update fields if they're currently empty or clearly wrong
            
            # Title: Only if current title is empty or generic
            if ('title' in ai_result and ai_result['title'].strip() and 
                (not content_schema.title or len(content_schema.title) < 5 or 
                 'untitled' in content_schema.title.lower())):
                logger.info(f"AI updating title: {ai_result['title']}")
                content_schema.title = ai_result['title'].strip()
            
            # Featured image: Only if current is empty
            if ('featured_image' in ai_result and ai_result['featured_image'].strip() and 
                not content_schema.featured_image):
                logger.info(f"AI adding featured image")
                content_schema.featured_image = ai_result['featured_image'].strip()
            
            # Byline: Only use AI if it looks real and current is default
            ai_byline = ai_result.get('byline', '').strip()
            if (ai_byline and 
                'lotions & creams' not in ai_byline.lower() and
                ai_byline.startswith('By ') and
                (not content_schema.byline or 'costco' in content_schema.byline.lower())):
                logger.info(f"AI updating byline: {ai_byline}")
                content_schema.byline = ai_byline
            
            # Description: Only if missing
            if ('description' in ai_result and ai_result['description'].strip() and
                (not content_schema.description or len(content_schema.description) < 20)):
                content_schema.description = ai_result['description'].strip()
            
            # Recipe-specific: Only merge if extracted data is empty
            if content_type == ContentType.RECIPE:
                # Ingredients: Prefer extracted, only use AI if empty
                extracted_ingredients = getattr(content_schema, 'ingredients', [])
                if len(extracted_ingredients) < 2 and 'ingredients' in ai_result and ai_result['ingredients']:
                    logger.info(f"AI adding ingredients: {len(ai_result['ingredients'])} items")
                    content_schema.ingredients = ai_result['ingredients']
                
                # Instructions: Same conservative approach
                extracted_instructions = getattr(content_schema, 'instructions', [])
                if len(extracted_instructions) < 1 and 'instructions' in ai_result and ai_result['instructions']:
                    logger.info(f"AI adding instructions: {len(ai_result['instructions'])} steps")
                    content_schema.instructions = ai_result['instructions']
                
                # Timing: Only if not already extracted
                for field in ['prep_time', 'cook_time', 'servings']:
                    current_value = getattr(content_schema, field, '')
                    if (not current_value and field in ai_result and ai_result[field]):
                        setattr(content_schema, field, ai_result[field])

            return content_schema

        except Exception as e:
            logger.error(f"Error in conservative merging: {e}")
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
            'extraction_method': 'fixed_super_enhanced_conservative',
            'content_stats': {
                'paragraphs_extracted': len(extracted.main_content),
                'images_found': len(extracted.images),
                'headings_found': len(extracted.headings),
                'lists_found': len(extracted.lists),
                'quotes_found': len(extracted.quotes)
            },
            'best_image_score': max([img['score'] for img in extracted.images]) if extracted.images else 0,
            'author_details_found': bool(extracted.author_details),
            'byline_found': bool(extracted.byline),
            'recipe_sections_found': len(extracted.metadata.get('ingredients', [])) if content_schema.content_type == ContentType.RECIPE else 0
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
        if content_schema.byline and 'lotions & creams' not in content_schema.byline.lower():
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
                ingredient_count = len([ing for ing in content_schema.ingredients if not ing.startswith('===')])
                score += min(ingredient_count * 2, 20)  # Up to 20 for ingredients
            if hasattr(content_schema, 'instructions') and content_schema.instructions:
                instruction_count = len([inst for inst in content_schema.instructions if not inst.startswith('===')])
                score += min(instruction_count * 3, 15)  # Up to 15 for instructions
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


# Debug helper for testing
def debug_recipe_extraction(html_file_path: str):
    """Debug helper to test recipe extraction on a specific file"""
    
    processor = FixedSuperEnhancedCostcoProcessor()
    
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract URL from filename
        filename = html_file_path.split('/')[-1]
        url = f"https://www.costco.com/{filename}"
        
        # Debug the extraction
        processor.universal_extractor.debug_recipe_extraction(html_content, url)
        
        # Process with fixed system
        result = processor.process_content(html_content, url, filename)
        
        if result and result.content.content_type == ContentType.RECIPE:
            print("\n=== FIXED RECIPE RESULTS ===")
            print(f"Title: {result.content.title}")
            print(f"Byline: {result.content.byline}")
            print(f"Ingredients ({len(result.content.ingredients)}):")
            for i, ingredient in enumerate(result.content.ingredients[:10]):
                print(f"  {i+1}. {ingredient}")
            print(f"Instructions ({len(result.content.instructions)}):")
            for i, instruction in enumerate(result.content.instructions[:5]):
                print(f"  {i+1}. {instruction[:100]}...")
            print(f"Quality Score: {result.content_quality_score}")
        
    except Exception as e:
        print(f"Debug failed: {e}")


if __name__ == "__main__":
    # Example usage
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Test with sample content
    test_html = """
    <html>
        <head><title>Grape Crumble | Costco</title></head>
        <body>
            <article>
                <h1>Grape Crumble</h1>
                <h3>FILLING</h3>
                <ul>
                    <li>2 cups black grapes</li>
                    <li>⅔ cup sugar</li>
                    <li>6 Tbsp water, divided</li>
                </ul>
                <h3>STREUSEL</h3>
                <ul>
                    <li>⅓ cup flour</li>
                    <li>¼ cup sugar</li>
                </ul>
                <img src="/live/resource/img/grape_crumble.jpg" alt="Delicious grape crumble" />
            </article>
        </body>
    </html>
    """
    
    result = processor.process_content(
        test_html, 
        "https://www.costco.com/recipe-grape-crumble", 
        "recipe-grape-crumble-september-2023.html"
    )
    
    if result:
        print(f"✅ Title: {result.content.title}")
        print(f"✅ Type: {result.content.content_type}")
        print(f"✅ Ingredients: {len(result.content.ingredients)}")
        print(f"✅ Quality: {result.content_quality_score}")
    else:
        print("❌ Processing failed")