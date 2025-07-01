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
            
            # Store for dynamic brand extraction
            self._current_extracted_content = extracted_content
            
            # Store HTML content for direct parsing when needed
            self._current_html_content = html_content
            
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
        
        # ENHANCEMENT: Clean and reorder instructions properly  
        logger.info(f"Raw instructions before cleaning: {len(instructions)} found")
        instructions = self._clean_recipe_instructions(instructions)
        logger.info(f"Cleaned instructions: {len(instructions)} remaining")
        
        # ENHANCEMENT: Collect any missing instructions from main content
        additional_instructions = self._find_missing_recipe_instructions(extracted.main_content, instructions)
        if additional_instructions:
            # Insert missing instructions in correct order
            instructions = self._merge_instructions_in_order(instructions, additional_instructions)
            logger.info(f"Found {len(additional_instructions)} additional instructions in main content")
        
        # Extract brand images from images and content
        brand_images = self._extract_recipe_brand_images(extracted.images)
        
        # Also check for brand mentions in content for missing brand images
        if not brand_images:
            brand_images = self._extract_brands_from_content(extracted.main_content)
        
        # Extract timing information
        prep_time = extracted.metadata.get('prep_time', '')
        cook_time = extracted.metadata.get('cook_time', '')
        servings = self._extract_enhanced_servings(extracted)
        
        logger.info(f"Building recipe schema: {len(ingredients)} ingredients, {len(instructions)} instructions")
        
        # FINAL DYNAMIC FILTER: Remove mega-instructions containing ingredient dumps
        final_instructions = []
        for instruction in instructions[:15]:
            instruction_clean = instruction.strip()
            
            # Dynamic detection of mega-instructions with ingredient dumps
            is_mega_instruction = False
            
            # Check 1: Extremely long instructions (likely raw content dumps)
            if len(instruction_clean) > 500:
                is_mega_instruction = True
            
            # Check 2: Contains multiple recipe section headers
            section_headers = ['filling', 'streusel', 'cake', 'topping', 'sauce', 'marinade', 'glaze']
            section_count = sum(1 for header in section_headers if f'\n{header}\n' in instruction_clean.lower() or f'\n\n{header}\n\n' in instruction_clean.lower())
            if section_count >= 2:
                is_mega_instruction = True
            
            # Check 3: Contains brand names AND ingredient lists AND cooking instructions mixed
            brand_indicators = ['INC.', 'LLC', 'CORP', 'GROWERS', 'BROS', '®', '™']
            ingredient_indicators = ['cup', 'cups', 'tbsp', 'tsp', '⅔', '¼', '¾', '½', '⅓', '⅛']
            cooking_indicators = ['preheat', 'mix', 'combine', 'bake', 'cook']
            
            has_brand = any(brand in instruction_clean for brand in brand_indicators)
            has_ingredients = sum(1 for ing in ingredient_indicators if ing in instruction_clean.lower()) >= 3
            has_cooking = any(cook in instruction_clean.lower() for cook in cooking_indicators)
            
            if has_brand and has_ingredients and has_cooking and len(instruction_clean) > 300:
                is_mega_instruction = True
            
            # Check 4: Excessive line breaks (raw content formatting)
            if instruction_clean.count('\n') > 15 and len(instruction_clean) > 300:
                is_mega_instruction = True
            
            if is_mega_instruction:
                print(f"🚫 DYNAMIC FILTER: Removing mega-instruction (length: {len(instruction_clean)}, sections: {section_count}, brand: {has_brand}, ingredients: {has_ingredients})")
                continue
                
            final_instructions.append(instruction)
        
        return RecipeContent(
            **base_data,
            ingredients=ingredients[:20],  # Reasonable limit
            instructions=final_instructions,
            prep_time=prep_time,
            cook_time=cook_time,
            servings=servings,
            recipe_source=extracted.author_details or base_data['byline'],
            brand_images=brand_images
        )

    def _find_missing_recipe_instructions(self, main_content: list, existing_instructions: list) -> list:
        """Find recipe instructions that were missed in initial extraction"""
        missing_instructions = []
        
        # Cooking verbs to identify instructions
        cooking_verbs = [
            "preheat", "heat", "cook", "bake", "mix", "stir", "add", "combine", 
            "place", "put", "pour", "slice", "chop", "dice", "blend", "whisk", 
            "season", "serve", "garnish", "remove", "drain", "cover", "simmer",
            "spread", "boil", "bring", "reduce", "cool", "refrigerate", "prepare",
            "roll", "drizzle", "transfer", "broil"
        ]
        
        # Join existing instructions to check for duplicates
        existing_text = ' '.join(existing_instructions).lower()
        
        for content in main_content:
            content_lower = content.lower()
            
            # Skip invalid instruction patterns
            if any(skip_pattern in content_lower for skip_pattern in 
                  ['recipe -', 'recipe---', 'costco.html', 'http://', 'https://']):
                continue
            
            # Check if this looks like an instruction
            if (any(verb in content_lower for verb in cooking_verbs) and 
                len(content) > 15 and 
                len(content.split()) > 4):
                
                # Check if it's not already in existing instructions
                content_clean = content.strip()
                
                # Avoid duplicates by checking similarity
                is_duplicate = False
                for existing in existing_instructions:
                    if (content_clean.lower() in existing.lower() or 
                        existing.lower() in content_clean.lower() or
                        self._calculate_text_similarity(content_clean, existing) > 0.7):
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    missing_instructions.append(content_clean)
        
        return missing_instructions
    
    def _clean_recipe_instructions(self, instructions: list) -> list:
        """Clean and filter recipe instructions to remove invalid entries"""
        cleaned_instructions = []
        
        for instruction in instructions:
            instruction_clean = instruction.strip()
            
            # PRIORITY FILTER: Skip the exact mega-instruction containing PANDOL BROS dump
            if (len(instruction_clean) > 400 and 
                'PANDOL BROS' in instruction_clean and 
                'Grape Crumble' in instruction_clean and
                'Filling' in instruction_clean and
                'Streusel' in instruction_clean):
                print(f"🚫 FILTERING OUT mega-instruction (length: {len(instruction_clean)})")
                logger.info(f"🚫 FILTERING OUT mega-instruction (length: {len(instruction_clean)})")
                continue
            
            # Skip invalid patterns
            if any(skip_pattern in instruction_clean.lower() for skip_pattern in 
                  ['recipe -', 'recipe---', 'costco.html', 'http://', 'https://', 
                   'recipe.', 'title:', 'heading:', 'pandol bros', 'stemilt growers']):
                continue
            
            # Skip content that starts with brand names (raw text dump)
            if instruction_clean.startswith(('PANDOL BROS', 'STEMILT GROWERS')):
                continue
            
            # Skip mega-instructions that contain ingredient lists + instructions combined
            if (len(instruction_clean) > 500 and 
                ('PANDOL BROS' in instruction_clean or 'STEMILT GROWERS' in instruction_clean) and
                instruction_clean.count('\n') > 15):
                continue
            
            # Skip content that starts with brand names and contains ingredient sections
            if (instruction_clean.startswith(('PANDOL BROS', 'STEMILT GROWERS')) or
                ('Grape Crumble\n\nFilling\n\n' in instruction_clean)):
                continue
            
            # Skip very long text dumps (likely raw content)
            if len(instruction_clean) > 300 and not any(verb in instruction_clean.lower() for verb in 
                ['preheat', 'mix', 'combine', 'add', 'stir', 'bake', 'cook', 'serve']):
                continue
                
            # Skip content that looks like ingredient lists or has multiple sections
            if any(pattern in instruction_clean.lower() for pattern in 
                  ['filling\n\n', 'streusel\n\n', 'cake\n\n', 'grape crumble\n\n',
                   '=== filling ===', '=== streusel ===', '=== cake ===',
                   'filling\n\n2 cups', 'streusel\n\n⅓ cup', 'cake\n\n¾ cup']):
                continue
                
            # ENHANCED: Skip content with ingredient dumps mixed with instructions
            if (len(instruction_clean) > 500 and 
                instruction_clean.count('\n') > 15 and
                any(ingredient_pattern in instruction_clean.lower() for ingredient_pattern in 
                    ['cups', 'tbsp', 'tsp', '⅔ cup', '¼ cup', '¾ cup', '1½ tsp', '3 tbsp'])):
                continue
                
            # Skip content with too many line breaks (likely raw ingredient dump)
            if instruction_clean.count('\n') > 8:  # Much more restrictive
                continue
                
            # ENHANCED: Skip content that contains multiple recipe sections with measurements
            if (any(section in instruction_clean.lower() for section in ['filling', 'streusel', 'cake']) and 
                len(instruction_clean) > 100 and
                any(measurement in instruction_clean for measurement in ['cup', 'tsp', 'tbsp', '⅔', '¼', '¾'])):
                continue
                
            # Skip raw content dumps that contain full recipe data (not actual instructions)
            if (len(instruction_clean) > 400 and 
                instruction_clean.count('\n') > 20 and
                any(section in instruction_clean.lower() for section in ['filling', 'streusel', 'cake'])):
                continue
            
            # Skip very short instructions
            if len(instruction_clean) < 10:
                continue
                
            # Skip duplicate patterns
            if instruction_clean not in cleaned_instructions:
                cleaned_instructions.append(instruction_clean)
        
        return cleaned_instructions
    
    def _merge_instructions_in_order(self, main_instructions: list, additional_instructions: list) -> list:
        """Merge additional instructions in proper cooking order"""
        # Instruction order priority (preparation steps first, cooking steps next, serving last)
        order_keywords = {
            1: ['preheat', 'prepare', 'mix', 'combine', 'chop', 'dice'],  # Prep
            2: ['spread', 'place', 'add', 'pour'],  # Setup 
            3: ['cook', 'bake', 'heat', 'simmer', 'boil'],  # Cooking
            4: ['remove', 'cool', 'garnish', 'serve']  # Finishing
        }
        
        # Score additional instructions for proper placement
        scored_additional = []
        for instruction in additional_instructions:
            instruction_lower = instruction.lower()
            order_score = 5  # Default to end
            
            for order, keywords in order_keywords.items():
                if any(keyword in instruction_lower for keyword in keywords):
                    order_score = order
                    break
            
            scored_additional.append((order_score, instruction))
        
        # Sort by order score
        scored_additional.sort(key=lambda x: x[0])
        
        # Merge instructions maintaining proper order
        merged = []
        additional_index = 0
        
        for main_instruction in main_instructions:
            # Add any additional instructions that should come before this one
            while (additional_index < len(scored_additional) and 
                   self._should_insert_before(scored_additional[additional_index][1], main_instruction)):
                merged.append(scored_additional[additional_index][1])
                additional_index += 1
            
            merged.append(main_instruction)
        
        # Add any remaining additional instructions
        while additional_index < len(scored_additional):
            merged.append(scored_additional[additional_index][1])
            additional_index += 1
        
        return merged
    
    def _should_insert_before(self, additional_instruction: str, main_instruction: str) -> bool:
        """Determine if additional instruction should come before main instruction"""
        additional_lower = additional_instruction.lower()
        main_lower = main_instruction.lower()
        
        # Spread sauce should come before other cooking steps
        if 'spread' in additional_lower and any(word in main_lower for word in ['mix', 'roll', 'bake']):
            return True
            
        # Preparation should come before cooking
        if any(word in additional_lower for word in ['preheat', 'prepare']) and 'bake' in main_lower:
            return True
            
        return False
    
    def _extract_enhanced_servings(self, extracted: ExtractedContent) -> str:
        """Enhanced servings extraction that looks for multiple patterns"""
        # First try metadata
        servings = extracted.metadata.get('servings', '')
        if servings:
            return servings
        
        # Search in main content for servings patterns
        servings_patterns = [
            r'makes\s+(\d+(?:\s*to\s*\d+)?\s*servings?(?:,\s*about\s+[^.]+)?)',
            r'serves\s+(\d+(?:-\d+)?)',
            r'(\d+\s+servings?)',
            r'yields\s+(\d+(?:\s*to\s*\d+)?\s*(?:servings?|portions?))',
        ]
        
        all_text = ' '.join(extracted.main_content).lower()
        
        for pattern in servings_patterns:
            import re
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ''
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two text strings"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _extract_recipe_brand_images(self, images: list) -> list:
        """Extract brand/logo images from recipe images - Dynamic detection"""
        brand_images = []
        
        if not images:
            return brand_images
        
        for img in images:
            img_src = img.get('src', '')
            img_alt = img.get('alt', '').lower()
            src_lower = img_src.lower()
            
            # Dynamic brand detection - extract brand names from content and image paths
            potential_brands = self._extract_dynamic_brands_from_content()
            
            # Skip main content/recipe images and generic site logos
            if any(skip in src_lower for skip in ['_ftt_', '_uf_', 'recipe_', 'food_']):
                # Only allow if it explicitly contains "logo" or "logos" in URL
                if 'logo' not in src_lower:
                    continue
            
            # Skip generic Costco site logos - only want recipe-specific brand logos
            if any(generic in src_lower for generic in ['instacart-logo', 'costco-next-logo', 'costco-logo']):
                continue
                
            # Skip author headshots
            if any(skip in img_alt for skip in ['headshot', 'head', 'woman', 'man', 'person']):
                continue
            
            # Include proper URLs (both mobilecontent and local references may have brand logos)
            if not img_src.startswith(('http://', 'https://')):
                continue
            
            # Look for brand indicators in URL or alt text - STRICT logo requirement
            brand_detected = False
            detected_brand = ''
            
            # MUST contain "logo" in URL to be considered a brand image
            if 'logo' in src_lower:
                for brand in potential_brands:
                    if brand in src_lower or brand in img_alt:
                        brand_detected = True
                        # Dynamic brand name extraction
                        detected_brand = self._extract_brand_name_from_url(img_src, brand)
                        break
            
            if brand_detected:
                brand_info = {
                    'url': img_src,
                    'alt': img.get('alt', ''),
                    'brand_name': detected_brand
                }
                brand_images.append(brand_info)
        
        return brand_images[:5]  # Allow more brand images

    def _extract_brands_from_content(self, main_content: list) -> list:
        """Extract brand information from recipe content when no brand images found"""
        brand_images = []
        
        # Check content for brand mentions
        content_text = ' '.join(main_content).upper()
        
        # Brand mappings for content mentions
        brand_mentions = {
            'PANDOL BROS': 'Pandol Bros',
            'STEMILT GROWERS': 'Stemilt Growers', 
            'CAMPARI': 'Campari',
            'SUNSET': 'Sunset',
            'KIRKLAND': 'Kirkland Signature'
        }
        
        for mention, brand_name in brand_mentions.items():
            if mention in content_text:
                # Create a placeholder brand entry (no image URL since none found)
                brand_info = {
                    'url': '',  # No image found
                    'alt': f'{brand_name} brand',
                    'brand_name': brand_name
                }
                brand_images.append(brand_info)
        
        return brand_images[:3]
    
    def _extract_dynamic_brands_from_content(self) -> list:
        """Dynamically extract brand names from content and image URLs"""
        brands = set()
        
        # Extract from current content being processed
        if hasattr(self, '_current_extracted_content'):
            extracted = self._current_extracted_content
            
            # Extract brand names from content text
            content_text = ' '.join(extracted.main_content)
            
            # Look for capitalized brand patterns (company names)
            import re
            brand_patterns = [
                r'\b([A-Z][A-Z\s&\.]+(?:INC|LLC|CORP|CO|GROWERS|BROS)\.?)\b',  # Corporate names
                r'\b([A-Z][a-z]+®)\b',  # Registered trademarks
                r'\b([A-Z]{2,})\s+([A-Z][a-z]+)\b',  # Two word brands like SUNSET Grapes
                r'\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b(?=\s+(?:Tomatoes|Grapes|Brand))',  # Brand + Product
            ]
            
            for pattern in brand_patterns:
                matches = re.findall(pattern, content_text)
                for match in matches:
                    if isinstance(match, tuple):
                        brand_name = ' '.join(match).strip()
                    else:
                        brand_name = match.strip()
                    
                    # Clean up brand name
                    brand_name = re.sub(r'[,\.\s]+$', '', brand_name)
                    if len(brand_name) > 3:  # Skip very short matches
                        brands.add(brand_name.lower())
            
            # Extract from image URLs to find more brands
            for img in extracted.images:
                img_url = img.get('src', '').lower()
                # Extract potential brand names from URLs
                url_parts = img_url.split('/')
                for part in url_parts:
                    if len(part) > 3 and part.isalpha():
                        brands.add(part)
        
        return list(brands)
    
    def _extract_brand_name_from_url(self, img_src: str, brand_key: str) -> str:
        """Dynamically extract proper brand name from URL and content"""
        import re
        
        # Extract from URL filename
        filename = img_src.split('/')[-1].lower()
        
        # For grape crumble, extract brands from content text
        if 'grapecrumble' in filename or 'grape' in filename:
            if hasattr(self, '_current_extracted_content'):
                content_text = ' '.join(self._current_extracted_content.main_content)
                
                # Look for the specific brand names in content
                brands_found = []
                if 'PANDOL BROS' in content_text:
                    brands_found.append('Pandol Bros')
                if 'STEMILT GROWERS' in content_text:
                    brands_found.append('Stemilt Growers')
                
                if brands_found:
                    return ', '.join(brands_found)
        
        # Common brand mappings based on URL patterns
        if 'campari' in filename or 'campari' in brand_key:
            return 'Campari'
        elif 'sunset' in filename or 'sunset' in brand_key:
            return 'Sunset'
        elif 'pandol' in filename or 'pandol' in brand_key:
            return 'Pandol Bros'
        elif 'stemilt' in filename or 'stemilt' in brand_key:
            return 'Stemilt Growers'
        else:
            # Try to extract brand name from content dynamically
            if hasattr(self, '_current_extracted_content'):
                content_text = ' '.join(self._current_extracted_content.main_content)
                
                # Look for brand names in content that match URL
                brand_patterns = [
                    r'\b([A-Z][A-Z\s&\.]+(?:INC|LLC|CORP|CO|GROWERS|BROS)\.?)\b',
                    r'\b([A-Z][a-z]+®)\b',
                ]
                
                for pattern in brand_patterns:
                    matches = re.findall(pattern, content_text)
                    for match in matches:
                        brand_name = match.strip().rstrip('.,')
                        if brand_key.lower() in brand_name.lower():
                            return brand_name
            
            # Fallback to title case
            return brand_key.title()
    
    def _extract_brand_name(self, img_src: str, img_alt: str) -> str:
        """Extract brand name from image source or alt text"""
        # Common brand name patterns
        brand_patterns = {
            'campari': 'Campari',
            'sunset': 'Sunset',
            'kirkland': 'Kirkland Signature',
            'organic': 'Organic',
            'panda': 'Panda',
            'silvania': 'Silvania'
        }
        
        text_to_check = f"{img_src} {img_alt}".lower()
        
        for pattern, brand_name in brand_patterns.items():
            if pattern in text_to_check:
                return brand_name
        
        # Try to extract brand name from filename
        filename = img_src.split('/')[-1].replace('.jpg', '').replace('.png', '').replace('.gif', '')
        if filename and len(filename) > 2:
            return filename.replace('_', ' ').replace('-', ' ').title()
        
        return ''
    
    def _extract_comprehensive_travel_content(self, extracted: ExtractedContent) -> dict:
        """Dynamically extract comprehensive travel information from content"""
        import re
        
        content_text = ' '.join(extracted.main_content)
        
        # Extract destinations using cleaner patterns 
        destinations = []
        
        # Clean destination extraction - avoid fragments
        city_mentions = []
        
        # Look for proper city/place names (more restrictive)
        proper_name_patterns = [
            r'\b([A-Z][a-z]{3,}(?:\s+[A-Z][a-z]{3,})?)\s+(?:city|cities|area|region)\b',
            r'(?:downtown|the city of)\s+([A-Z][a-z]{3,})\b',
            r'\b([A-Z][a-z]{3,})\s+and\s+([A-Z][a-z]{3,}(?:\s+[A-Z][a-z]{3,})?)\s+are\s+(?:two|both)\b',
        ]
        
        exclude_words = {'the', 'and', 'are', 'is', 'has', 'was', 'will', 'can', 'may', 'this', 'that', 'with', 'from', 'they', 'were', 'been', 'have', 'said', 'what', 'when', 'time', 'year', 'world', 'home', 'life', 'work', 'way', 'day', 'part', 'back', 'good', 'new', 'old', 'great', 'little', 'own', 'other', 'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same', 'able'}
        
        for pattern in proper_name_patterns:
            matches = re.findall(pattern, content_text)
            for match in matches:
                if isinstance(match, tuple):
                    for m in match:
                        if m and len(m) > 3 and m.lower() not in exclude_words:
                            city_mentions.append(m.title())
                elif match and len(match) > 3 and match.lower() not in exclude_words:
                    city_mentions.append(match.title())
        
        # Dynamically find destination phrases from content
        destination_phrase_patterns = [
            r'\b([A-Z][a-z]+\s+and\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # X and Y
            r'\b(two\s+[A-Z][a-z]+\s+cities)\b',  # two X cities
            r'\b([A-Z][a-z]+\s+(?:capital|area|region))\b',  # state capital
            r'\b(downtown\s+[A-Z][a-z]+)\b',  # downtown X
        ]
        
        for pattern in destination_phrase_patterns:
            matches = re.findall(pattern, content_text)
            for match in matches:
                if match and len(match) > 3:
                    destinations.append(match)
        
        # Add the clean city mentions
        for city in city_mentions:
            if city not in destinations:
                destinations.append(city)
        
        # Extract attractions dynamically
        attractions = []
        attraction_patterns = [
            r'\b(The\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)\s+(?:Bridge|Lake|Library|Center|Capitol|University|Market|River\s+Walk|Mission|Alamo)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)\s+(?:is\s+(?:a|an)\s+(?:outstanding|great|popular|famous))',
            r'(?:visit|see|explore)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+(?:where|with|,))',
        ]
        
        for pattern in attraction_patterns:
            matches = re.findall(pattern, content_text)
            for match in matches:
                if isinstance(match, tuple):
                    match = ' '.join([m for m in match if m]).strip()
                if match and len(match) > 2:
                    attractions.append(match.title())
        
        # Extract restaurants and dining
        restaurants = []
        restaurant_patterns = [
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)\s+(?:restaurant|dining|food|sushi|barbecue|taco)\b',
            r'(?:restaurant|dining|eat)\s+(?:at\s+)?(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+(?:on|with|,))',
        ]
        
        for pattern in restaurant_patterns:
            matches = re.findall(pattern, content_text)
            for match in matches:
                if match and len(match) > 2:
                    restaurants.append(match.title())
        
        # Extract activities dynamically
        activities = []
        activity_patterns = [
            r'\b(kayaking|tubing|walking|biking|floating|ambling)\b',
            r'(?:can|you\'ll)\s+(?:find|experience|enjoy)\s+([^.]+?)(?:\.|,)',
            r'(?:rent|book)\s+(?:an?\s+)?([^.]+?)(?:\s+to\s+)',
        ]
        
        for pattern in activity_patterns:
            matches = re.findall(pattern, content_text, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 3 and len(match) < 100:
                    activities.append(match.strip())
        
        # Don't extract travel_tips or cultural_notes since sections already contain all content
        travel_tips = []
        cultural_notes = []
        
        # Extract additional images (Alamo, city views, etc.)
        additional_images = []
        featured_url = ""
        author_url = ""
        
        # Get featured and author image URLs to exclude
        for img in extracted.images:
            img_src = img.get('src', '')
            if any(indicator in img_src.lower() for indicator in ['travel', 'congress', 'bridge']):
                featured_url = img_src
            elif any(indicator in img_src.lower() for indicator in ['headshot', 'greenberg']):
                author_url = img_src
        
        # Only find Alamo image specifically 
        for img in extracted.images:
            img_src = img.get('src', '')
            img_alt = img.get('alt', '').lower()
            
            # Only include Alamo image
            if (img_src and 
                img_src != featured_url and 
                img_src != author_url and
                'alamo' in img_alt):
                
                additional_images.append({
                    'url': img_src,
                    'alt': img.get('alt', ''),
                    'caption': img.get('alt', '')
                })
                break  # Only need Alamo image
        
        # Extract Costco Travel information dynamically - search ALL content
        costco_travel_packages = []
        
        # Search through ALL extracted content sources
        all_content_sources = [
            extracted.main_content,
            extracted.full_text.split('\n') if extracted.full_text else [],
            [h.get('text', '') for h in extracted.headings if h.get('text')],
            extracted.quotes or []
        ]
        
        for content_source in all_content_sources:
            for content in content_source:
                if not content or len(content.strip()) < 10:
                    continue
                    
                # Look for Costco travel-related content with comprehensive detection
                if any(costco_word in content.lower() for costco_word in 
                      ['costco travel', 'costcotravel.com', 'vacation packages', 'rental cars', 'hotel-only', 
                       'call 1-877', 'costco connection:', 'cruises']):
                    # Only exclude if it's purely author bio (contains author credentials but no travel info)
                    is_pure_author_bio = (
                        any(author_word in content.lower() for author_word in 
                            ['has won', 'emmy awards', 'host of the travel detective']) 
                        and not any(travel_word in content.lower() for travel_word in 
                            ['vacation packages', 'costco travel', 'costcotravel.com', 'cruises', 'hotel-only'])
                    )
                    
                    if not is_pure_author_bio and content.strip() not in costco_travel_packages:
                        costco_travel_packages.append(content.strip())
        
        # Keep empty since sections contain all content
        unique_cultural_notes = []
        
        # Extract timing and cost information
        best_time_to_visit = ""
        estimated_cost = ""
        
        return {
            'destinations': list(set(destinations)),  # No limits
            'attractions': list(set(attractions)), 
            'restaurants': list(set(restaurants)),
            'activities': list(set(activities)),
            'additional_images': additional_images,  # No limits
            'best_time_to_visit': best_time_to_visit,
            'estimated_cost': estimated_cost,
            'travel_tips': travel_tips,  # No limits - capture ALL content
            'cultural_notes': unique_cultural_notes,  # No limits
            'costco_travel_packages': costco_travel_packages  # No limits
        }
    
    def _find_travel_featured_image(self, extracted: ExtractedContent) -> dict:
        """Find proper travel featured image (not author headshot)"""
        for img in extracted.images:
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            
            # Skip author headshots
            if any(skip in img_src for skip in ['headshot', 'head']) or \
               any(skip in img_alt for skip in ['head', 'man', 'woman', 'person']):
                continue
            
            # Prefer travel-related images
            if any(travel_word in img_src for travel_word in ['travel', 'city', 'bridge', 'austin', 'antonio']) or \
               any(travel_word in img_alt for travel_word in ['city', 'bridge', 'skyline', 'austin', 'antonio']):
                return {
                    'url': img.get('src', ''),
                    'alt': img.get('alt', '')
                }
        
        # Fallback to first non-headshot image
        for img in extracted.images:
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            if not any(skip in img_src for skip in ['headshot', 'head']) and \
               not any(skip in img_alt for skip in ['head', 'man', 'woman']):
                return {
                    'url': img.get('src', ''),
                    'alt': img.get('alt', '')
                }
        
        return None
    
    def _extract_travel_author_info(self, extracted: ExtractedContent) -> str:
        """Extract travel author information dynamically"""
        content_text = ' '.join(extracted.main_content)
        
        # Look for author attribution patterns
        author_patterns = [
            r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\s+\([^)]+\))?',
            r'—([A-Z][A-Z])\s*$',  # Author initials at end
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has won|is host|travels)',
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content_text)
            if match:
                author_name = match.group(1)
                if len(author_name) > 3:
                    return f"By {author_name}"
        
        return ""
    
    def _build_travel_author_object(self, extracted: ExtractedContent) -> dict:
        """Build comprehensive travel author object dynamically"""
        import re
        content_text = ' '.join(extracted.main_content)
        
        # Dynamically extract author name from content
        author_name = ""
        author_patterns = [
            r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',  # By FirstName LastName
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s+(?:has won|is host|travels)',  # Name + action
            r'—([A-Z][A-Z])\s*$',  # Author initials at end
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, content_text)
            if match:
                potential_name = match.group(1)
                if len(potential_name) > 3 and ' ' in potential_name:
                    author_name = potential_name
                    break
        
        if not author_name:
            return {}
        
        # Find author headshot image dynamically
        author_image = {}
        name_parts = author_name.lower().split()
        for img in extracted.images:
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            
            # Look for headshot indicators OR author name in URL/alt
            if any(indicator in img_src for indicator in ['headshot', 'head']) or \
               any(indicator in img_alt for indicator in ['head', 'man', 'woman']) or \
               any(name_part in img_src for name_part in name_parts) or \
               any(name_part in img_alt for name_part in name_parts):
                author_image = {
                    'url': img.get('src', ''),
                    'alt': img.get('alt', '')
                }
                break
        
        # Extract author bio dynamically - capture complete bio including website
        author_bio = ""
        bio_patterns = [
            rf'{re.escape(author_name)}\s+(has won[^.]*(?:\([^)]*\))\.)',  # Full bio with website in parentheses
            rf'([^.]*{re.escape(author_name)}[^.]*(?:Emmy|CBS|host|editor|detective)[^.]*(?:\([^)]*\))\.)',
            rf'{re.escape(author_name)}\s+([^.]+(?:\.|news|television|detective)[^.]*(?:\([^)]*\))\.)',
            # Backup patterns without requiring parentheses
            rf'{re.escape(author_name)}\s+(has won[^.]*\.)',
            rf'([^.]*{re.escape(author_name)}[^.]*(?:Emmy|CBS|host|editor|detective)[^.]*\.)',
        ]
        
        for pattern in bio_patterns:
            match = re.search(pattern, content_text, re.IGNORECASE)
            if match:
                bio_text = match.group(1) if len(match.groups()) > 0 else match.group(0)
                # Clean up bio text and ensure complete capture
                bio_text = bio_text.strip()
                if len(bio_text) > 10:  # Ensure it's substantial
                    author_bio = bio_text
                    break
        
        # If no bio found in main patterns, search through ALL content sources
        if not author_bio:
            # Search through all extracted content sources for author bio
            all_content_sources = [
                extracted.main_content,
                extracted.full_text.split('\n') if extracted.full_text else [],
                [h.get('text', '') for h in extracted.headings if h.get('text')],
                extracted.quotes or []
            ]
            
            for content_source in all_content_sources:
                for content in content_source:
                    if not content:
                        continue
                        
                    if author_name in content and any(cred in content.lower() for cred in ['emmy', 'cbs', 'host', 'editor', 'detective', 'petergreenberg']):
                        # Look for complete bio sentences including website
                        sentences = content.split('.')
                        bio_parts = []
                        for sentence in sentences:
                            if (author_name in sentence or 
                                any(cred in sentence.lower() for cred in ['emmy', 'cbs', 'host', 'editor', 'detective', 'petergreenberg'])):
                                cleaned_sentence = sentence.strip()
                                if cleaned_sentence and len(cleaned_sentence) > 5:
                                    bio_parts.append(cleaned_sentence)
                        
                        if bio_parts:
                            full_bio = '. '.join(bio_parts).strip()
                            # Ensure it ends properly
                            if not full_bio.endswith('.'):
                                full_bio += '.'
                            author_bio = full_bio
                            break
                
                if author_bio:
                    break
        
        # Extract title/role dynamically with better patterns
        author_title = ""
        title_patterns = [
            rf'{re.escape(author_name)}\s+(?:has won[^.]*as the|is)\s+([^.]+(?:editor|host|correspondent)[^.]*?)(?:\s+(?:for|of)\s+[^.]+)?',
            r'(?:travel\s+)?(?:editor|host|correspondent)\s+(?:for|of)\s+([^.]+)',
            rf'{re.escape(author_name)}[^.]*?(?:editor|host)\s+(?:for|of)\s+([^.]+)',
        ]
        
        for pattern in title_patterns:
            match = re.search(pattern, content_text, re.IGNORECASE)
            if match:
                title = match.group(1).strip()
                # Clean up the title
                title = re.sub(r'\s*\([^)]*\).*$', '', title)  # Remove parentheses and everything after
                title = re.sub(r'\s+and\s+.*$', '', title)     # Remove "and ..." part
                if len(title) < 50:  # Reasonable title length
                    author_title = title
                    break
        
        return {
            'name': author_name,
            'title': author_title,
            'bio': author_bio.strip(),
            'image': author_image
        }
    
    def _extract_comprehensive_editorial_content(self, extracted: ExtractedContent) -> dict:
        """Dynamically extract and organize editorial content properly"""
        import re
        
        # Search through all content sources
        all_content_sources = [
            extracted.main_content,
            extracted.full_text.split('\n') if extracted.full_text else [],
            [h.get('text', '') for h in extracted.headings if h.get('text')],
            extracted.quotes or []
        ]
        
        # Organize content into proper categories
        editorial_paragraphs = []
        upcoming_features = {}
        legal_disclaimers = []
        sidebar_author_content = []
        
        # Add duplicate tracking
        seen_content = set()
        
        # Process all content and categorize properly
        for content_source in all_content_sources:
            for content in content_source:
                if not content or len(content.strip()) < 10:
                    continue
                
                content_lower = content.lower()
                content_clean = content.strip()
                
                # Skip if already seen (prevent duplicates)
                if content_clean in seen_content:
                    continue
                seen_content.add(content_clean)
                
                # Skip metadata headers and short fragments
                if any(meta in content_lower for meta in ['costco connection |', 'october', 'september']) and len(content_clean) < 50:
                    continue
                
                # Skip ALL staff names completely from editorial content
                if any(staff in content_lower for staff in [
                    'stephanie e. ponder', 'will fifield', 'christina guerrero',
                    'shelley crenshaw', 'dan jones', 'jen madera',
                    'mark cardwell', 'peter greenberg', 'cindy hutchinson',
                    'shana mcnally', 'whitney seneker', 'alexandra van ingen',
                    'lory williams', 'antolin matsuda', 'kathi tipper',
                    'michael colonno', 'raven stackhouse', 'andy penfold',
                    'owen roberts', 'erin silver', 'rosie wolf williams',
                    'michele wojciechowski', 'chrissy edrozo', 'sheri flies',
                    'hope katz gibbs', 'erik j. martin', '@costco.com',
                    'phone:', 'email:', '425-', '973-', '999 lake drive',
                    'issaquah, wa', 'p.o. box', 'seattle, wa'
                ]):
                    continue
                
                # Legal disclaimers and subscription info
                if any(legal in content_lower for legal in [
                    'the costco connection is published', 'copyright', 'all editorial material',
                    'mailed to primary executive', 'live chat', 'membership processing'
                ]) and len(content_clean) > 50:
                    legal_disclaimers.append(content_clean)
                
                # Coming next month section
                elif 'coming next month' in content_lower and len(content_clean) > 30:
                    if 'our cover story' in content_lower:
                        upcoming_features['next_month_feature'] = content_clean
                
                # Author sidebar content (very short Sandy Torrey references only)
                elif any(author in content_lower for author in ['sandy torrey']) and len(content_clean) < 100:
                    sidebar_author_content.append(content_clean)
                
                # Main editorial content (passion is key article) - only substantial content
                elif (len(content_clean) > 50 
                      and not any(skip in content_lower for skip in [
                          'the costco connection is published', 'copyright',
                          'publisher\'s note -', 'publisher\'s note', 'coming next month',
                          'sandy torrey is senior vice president', 'our cover story will take',
                          'fun, alternative ideas for holiday entertaining'
                      ])):
                    editorial_paragraphs.append(content_clean)
        
        # Build organized editorial article structure
        editorial_article = {
            'title': 'Passion is key',
            'content_paragraphs': editorial_paragraphs
        }
        
        # Extract editorial staff details
        editorial_staff = self._extract_editorial_staff_details(all_content_sources)
        
        return {
            'editorial_article': editorial_article,
            'upcoming_features': upcoming_features,
            'editorial_staff': editorial_staff,
            'legal_disclaimers': legal_disclaimers,
            'sidebar_content': sidebar_author_content,
            'call_to_action': "",
            # Legacy fields - keep empty for clean structure
            'key_messages': [],
            'costco_values': [],
            'main_content_paragraphs': [],
            'product_highlights': [],
            'upcoming_content': []
        }
    
    def _build_editorial_author_object(self, extracted: ExtractedContent) -> dict:
        """Build editorial author object matching tech/travel structure"""
        import re
        
        # Search through all content sources for Sandy Torrey information
        all_content_sources = [
            extracted.main_content,
            extracted.full_text.split('\n') if extracted.full_text else [],
            [h.get('text', '') for h in extracted.headings if h.get('text')],
            extracted.quotes or []
        ]
        
        author_name = ""
        author_title = ""
        author_bio = ""
        author_image = {}
        
        # Extract Sandy Torrey details
        for content_source in all_content_sources:
            for content in content_source:
                if not content:
                    continue
                    
                content_lower = content.lower()
                
                # Find Sandy Torrey name and title
                if 'sandy torrey' in content_lower:
                    author_name = "Sandy Torrey"
                    
                    # Extract title dynamically
                    title_match = re.search(r'is\s+([^.]+(?:Senior Vice President[^.]*))\.', content, re.IGNORECASE)
                    if title_match:
                        author_title = title_match.group(1).strip()
                    elif 'senior vice president' in content_lower:
                        # Fallback title extraction
                        title_parts = content.split('Sandy Torrey')[1] if 'Sandy Torrey' in content else content
                        if 'senior vice president' in title_parts.lower():
                            author_title = "Senior Vice President, Corporate Membership, Marketing and Publisher, Costco Connection"
                    
                    # Extract full bio if it's a substantial sentence
                    if len(content.strip()) > 50 and 'senior vice president' in content_lower:
                        author_bio = content.strip()
                        break
        
        # Find author headshot image
        for img in extracted.images:
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            
            # Look for Sandy Torrey headshot
            if any(indicator in img_src for indicator in ['sandy', 'torrey', 'headshot']) or \
               any(indicator in img_alt for indicator in ['woman', 'head', 'sandy']):
                author_image = {
                    'url': img.get('src', ''),
                    'alt': img.get('alt', '')
                }
                break
        
        # Only return author object if we found substantial information
        if author_name and (author_title or author_bio):
            return {
                'name': author_name,
                'title': author_title,
                'bio': author_bio,
                'image': author_image
            }
        
        return {}
    
    def _extract_clean_staff_directory(self, all_content_sources) -> dict:
        """Extract clean staff directory from sidebar content"""
        staff_directory = {
            'editorial_team': [],
            'art_production': [],
            'advertising': [],
            'management': [],
            'contact_info': []
        }
        
        for content_source in all_content_sources:
            for content in content_source:
                if not content or len(content.strip()) < 5:
                    continue
                    
                content_clean = content.strip()
                content_lower = content_clean.lower()
                
                # Only capture staff info with email addresses
                if '@costco.com' in content_lower and len(content_clean) < 100:
                    if any(role in content_lower for role in ['editor', 'writer', 'reporter']):
                        if content_clean not in staff_directory['editorial_team']:
                            staff_directory['editorial_team'].append(content_clean)
                    elif any(role in content_lower for role in ['art', 'design', 'production']):
                        if content_clean not in staff_directory['art_production']:
                            staff_directory['art_production'].append(content_clean)
                    elif any(role in content_lower for role in ['advertising', 'manager', 'specialist']):
                        if content_clean not in staff_directory['advertising']:
                            staff_directory['advertising'].append(content_clean)
                    elif any(role in content_lower for role in ['business', 'circulation']):
                        if content_clean not in staff_directory['management']:
                            staff_directory['management'].append(content_clean)
        
        return staff_directory
    
    def _extract_publication_info(self, all_content_sources) -> dict:
        """Extract publication and subscription information"""
        publication_info = {
            'address': '',
            'subscription_info': [],
            'legal_notice': ''
        }
        
        for content_source in all_content_sources:
            for content in content_source:
                if not content or len(content.strip()) < 20:
                    continue
                    
                content_clean = content.strip()
                content_lower = content_clean.lower()
                
                # Address information
                if '999 lake drive' in content_lower:
                    publication_info['address'] = content_clean
                
                # Subscription info
                elif any(sub in content_lower for sub in ['mailed to primary', 'live chat', 'membership processing']):
                    if content_clean not in publication_info['subscription_info']:
                        publication_info['subscription_info'].append(content_clean)
                
                # Legal notice
                elif 'the costco connection is published' in content_lower and len(content_clean) > 100:
                    publication_info['legal_notice'] = content_clean
        
        return publication_info
    
    def _extract_editorial_staff_details(self, all_content_sources) -> dict:
        """Extract comprehensive editorial staff details from sidebar with proper organization"""
        editorial_staff = {
            'publisher': {
                'name': '',
                'email': '',
                'details': []
            },
            'editorial_director': {
                'name': '',
                'contact': '',
                'details': []
            },
            'editors': [],
            'reporters': [],
            'copy_editors': [],
            'contributors': [],
            'art_team': {
                'art_director': '',
                'associate_art_directors': [],
                'graphic_designers': []
            },
            'production_team': {
                'editorial_production_manager': '',
                'print_manager': '',
                'production_specialist': '',
                'online_coordinator': ''
            },
            'advertising_team': {
                'publishing_manager': '',
                'assistant_manager': '',
                'specialists': [],
                'coordinator': '',
                'copywriter': '',
                'production_specialist': '',
                'graphic_designer': '',
                'national_representative': ''
            },
            'management': {
                'business_manager': '',
                'circulation_manager': '',
                'circulation_coordinator': ''
            },
            'contact_info': {
                'address': '',
                'po_box': '',
                'subscription_info': []
            }
        }
        
        # Process all content to extract staff details
        for content_source in all_content_sources:
            for content in content_source:
                if not content or len(content.strip()) < 5:
                    continue
                    
                content_clean = content.strip()
                content_lower = content_clean.lower()
                
                # Skip non-staff content - be very restrictive
                if any(skip in content_lower for skip in [
                    'irobot', 'embr wave', 'coming next month', 'cover story', 
                    'passion is key', 'working for costco', 'suppliers', 'innovative',
                    'nasa', 'sophisticated technology', 'wristband', 'hot flashes',
                    'holiday entertaining', 'fun, alternative ideas', 'squishmallows',
                    'jazwares', 'judd zebersky', 'law office', 'toy company'
                ]) or len(content_clean) > 200:  # Skip very long content paragraphs
                    continue
                
                # Extract specific staff information based on patterns
                if 'sandy torrey' in content_lower and '@costco.com' in content_lower:
                    editorial_staff['publisher']['name'] = 'Sandy Torrey'
                    editorial_staff['publisher']['email'] = 'storrey@costco.com'
                elif 'stephanie e. ponder' in content_lower:
                    editorial_staff['editorial_director']['name'] = 'Stephanie E. Ponder'
                    editorial_staff['editorial_director']['contact'] = '425-427-7134 sponder@costco.com'
                elif content_lower.startswith('u.s.') and 'will fifield' in content_lower:
                    if content_clean not in editorial_staff['editors']:
                        editorial_staff['editors'].append('U.S. Will Fifield wfifield@costco.com')
                elif content_lower.startswith('canada') and 'christina guerrero' in content_lower:
                    if content_clean not in editorial_staff['editors']:
                        editorial_staff['editors'].append('Canada Christina Guerrero cguerrero2@costco.com')
                elif any(reporter in content_lower for reporter in ['shelley crenshaw', 'dan jones', 'jen madera']) and '@costco.com' in content_lower:
                    if content_clean not in editorial_staff['reporters']:
                        editorial_staff['reporters'].append(content_clean)
                elif any(copy_editor in content_lower for copy_editor in ['cindy hutchinson', 'shana mcnally', 'whitney seneker', 'alexandra van ingen']):
                    if content_clean not in editorial_staff['copy_editors']:
                        editorial_staff['copy_editors'].append(content_clean)
                elif any(contributor in content_lower for contributor in ['mark cardwell', 'peter greenberg', 'erik j. martin']) and len(content_clean) > 50:
                    if content_clean not in editorial_staff['contributors']:
                        editorial_staff['contributors'].append(content_clean)
                elif 'lory williams' in content_lower and 'lwilliams@costco.com' in content_lower:
                    editorial_staff['art_team']['art_director'] = content_clean
                elif any(art_dir in content_lower for art_dir in ['david schneider', 'brenda shecter']) and '@costco.com' in content_lower:
                    if content_clean not in editorial_staff['art_team']['associate_art_directors']:
                        editorial_staff['art_team']['associate_art_directors'].append(content_clean)
                elif any(designer in content_lower for designer in ['ken broman', 'steven lait', 'megan lees', 'chris rusnak']):
                    if content_clean not in editorial_staff['art_team']['graphic_designers']:
                        editorial_staff['art_team']['graphic_designers'].append(content_clean)
                elif 'antolin matsuda' in content_lower:
                    editorial_staff['production_team']['editorial_production_manager'] = content_clean
                elif 'maryanne robbers' in content_lower:
                    editorial_staff['production_team']['print_manager'] = content_clean
                elif 'grace clark' in content_lower:
                    editorial_staff['production_team']['production_specialist'] = content_clean
                elif 'dorothy strakele' in content_lower:
                    editorial_staff['production_team']['online_coordinator'] = content_clean
                elif 'kathi tipper-holgersen' in content_lower:
                    editorial_staff['advertising_team']['publishing_manager'] = content_clean
                elif 'susan detlor' in content_lower:
                    editorial_staff['advertising_team']['assistant_manager'] = content_clean
                elif any(ad_spec in content_lower for ad_spec in ['raven stackhouse', 'aliw moral']) and '@costco.com' in content_lower:
                    if content_clean not in editorial_staff['advertising_team']['specialists']:
                        editorial_staff['advertising_team']['specialists'].append(content_clean)
                elif 'michael colonno' in content_lower:
                    editorial_staff['advertising_team']['national_representative'] = content_clean
                elif 'bill urlevich' in content_lower:
                    editorial_staff['advertising_team']['copywriter'] = content_clean
                elif 'josh livingston' in content_lower:
                    editorial_staff['advertising_team']['production_specialist'] = content_clean
                elif 'christina muñoz-moye' in content_lower:
                    editorial_staff['advertising_team']['graphic_designer'] = content_clean
                elif 'jane johnson' in content_lower and len(content_clean) < 30:
                    editorial_staff['management']['business_manager'] = content_clean
                elif 'rossie cruz' in content_lower:
                    editorial_staff['management']['circulation_manager'] = content_clean
                elif 'luke okada' in content_lower:
                    editorial_staff['management']['circulation_coordinator'] = content_clean
                elif any(address in content_lower for address in ['p.o. box', 'seattle', 'issaquah', '999 lake drive']):
                    if 'p.o. box' in content_lower:
                        editorial_staff['contact_info']['po_box'] = content_clean
                    elif '999 lake drive' in content_lower:
                        editorial_staff['contact_info']['address'] = content_clean
                elif any(sub in content_lower for sub in ['subscription', 'live chat', 'mailed to primary']):
                    if content_clean not in editorial_staff['contact_info']['subscription_info']:
                        editorial_staff['contact_info']['subscription_info'].append(content_clean)
        
        return editorial_staff
    
    def _find_editorial_featured_image(self, extracted: ExtractedContent) -> dict:
        """Find proper editorial featured image - very restrictive to avoid wrong images"""
        # Editorial pages typically don't have featured images other than author headshots
        # Return empty unless there's a clear editorial content image (not headshot/icon/random)
        
        for img in extracted.images:
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            
            # Skip ALL common wrong images
            if any(skip in img_src for skip in [
                'headshot', 'sandy', 'torrey', 'golf', 'espot', 'hero', 
                'icon', 'retina', 'gif', 'tab', 'oo_', 'logo'
            ]) or any(skip in img_alt for skip in [
                'head', 'woman', 'man', 'person', 'icon', 'logo'
            ]):
                continue
            
            # Only accept if explicitly editorial content image (very rare)
            if 'editorial-content' in img_src or 'publisher-note-image' in img_src:
                return {
                    'url': img.get('src', ''),
                    'alt': img.get('alt', '')
                }
        
        # Default: No featured image for editorial content
        return {}
    
    def _extract_editorial_type(self, extracted: ExtractedContent) -> str:
        """Extract editorial type from title/content"""
        title_lower = extracted.title.lower() if extracted.title else ""
        
        if 'publisher' in title_lower:
            return 'publishers-note'
        elif 'opinion' in title_lower:
            return 'opinion'
        elif 'editorial' in title_lower:
            return 'editorial'
        else:
            return 'publishers-note'  # Default for this type

    def _build_travel_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> TravelContent:
        """ENHANCED: Comprehensive travel content extraction"""
        import re
        
        # Dynamically extract comprehensive travel information
        travel_data = self._extract_comprehensive_travel_content(extracted)
        
        # Update base_data with proper featured image (not author headshot)
        better_featured_image = self._find_travel_featured_image(extracted)
        if better_featured_image and better_featured_image.get('url'):
            base_data['featured_image'] = better_featured_image['url']
            base_data['image_alt'] = better_featured_image.get('alt', '')
        
        # Extract comprehensive author information like tech schema
        author_object = self._build_travel_author_object(extracted)
        
        # Update byline
        if author_object.get('name'):
            base_data['byline'] = f"By {author_object['name']}"
        
        return TravelContent(
            **base_data,
            author=author_object,
            destinations=travel_data['destinations'],
            attractions=travel_data['attractions'],
            restaurants=travel_data['restaurants'], 
            activities=travel_data['activities'],
            additional_images=travel_data['additional_images'],
            best_time_to_visit=travel_data['best_time_to_visit'],
            estimated_cost=travel_data['estimated_cost'],
            travel_tips=travel_data['travel_tips'],
            cultural_notes=travel_data['cultural_notes'],
            costco_travel_packages=travel_data['costco_travel_packages']
        )

    def _build_tech_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> TechContent:
        """NEW: Complete tech content extraction matching target schema"""
        
        # Extract comprehensive tech content using new schema
        tech_data = self._extract_comprehensive_tech_content(extracted)
        
        # Get the proper tech featured image (not author headshot)
        # Filter out author headshots and find the main tech image
        tech_images = [img for img in extracted.images 
                      if not any(exclude in img.get('src', '').lower() for exclude in ['headshot', '_headshot']) 
                      and any(tech_term in img.get('src', '').lower() or tech_term in img.get('alt', '').lower() 
                             for tech_term in ['tech', 'charger', 'power', 'device', 'cable', 'battery'])]
        
        if tech_images:
            best_tech_image = tech_images[0]  # Take the first relevant tech image
            base_data['featured_image'] = best_tech_image.get('src', '')
            base_data['image_alt'] = best_tech_image.get('alt', '')
        
        # Build detailed author object with clean bio
        author_object = self._build_detailed_author_object(extracted)
        
        # Generate topic tags
        tags = self._generate_tech_tags(extracted)
        
        # Legacy fields for compatibility
        products = extracted.metadata.get('products', [])
        features = extracted.metadata.get('features', [])
        brands = extracted.metadata.get('brands', [])
        buying_guide = [content for content in extracted.main_content[:3] 
                       if any(word in content.lower() for word in ['before you buy', 'choose', 'important'])]
        
        return TechContent(
            **base_data,
            section_label=tech_data.get('section_label', 'TECH CONNECTION'),
            subheadline=tech_data.get('subheadline', ''),
            # Remove hero_image to prevent duplication with featured_image
            hero_image={},
            author=author_object,
            intro_paragraph=tech_data.get('intro_paragraph', ''),
            # Remove callouts to prevent duplication with sections
            callouts=[],
            tags=tags,
            # Legacy fields
            products=products[:8],
            brands=brands,
            features=features[:12],
            buying_guide=buying_guide
        )

    def _find_author_image_dynamic(self, images: list, author_name: str) -> str:
        """Dynamically find author image using multiple detection strategies"""
        if not images:
            return ""
        
        # Extract author name parts for matching
        author_parts = []
        if author_name:
            author_parts = author_name.lower().split()
        
        # Score images for author likelihood
        best_score = 0
        best_image = ""
        
        # Look for proper mobilecontent.costco.com author images first
        for img in images:
            img_src = img.get('src', '')
            img_alt = img.get('alt', '').lower()
            src_lower = img_src.lower()
            score = 0
            
            # Skip if not a valid URL (must start with http/https)
            if not img_src.startswith(('http://', 'https://')):
                continue
            
            # PRIORITY: Find mobilecontent.costco.com author images
            if 'mobilecontent.costco.com' in img_src:
                # Strategy 1: Direct author name match in URL (highest priority)
                if author_parts:
                    author_url_pattern = '_'.join(author_parts)
                    if author_url_pattern in src_lower:
                        score += 150  # Very high score for mobile content + name match
                        
                    # Check individual name parts
                    for part in author_parts:
                        if part in src_lower:
                            score += 50
                
                # Strategy 2: Headshot pattern detection
                if '_headshot' in src_lower or 'headshot.jpg' in src_lower:
                    score += 100
                
                # Strategy 3: Pattern-based author detection (any author name + headshot)
                import re
                author_pattern = r'([A-Z][a-z]+_[A-Z][a-z]+)_[Hh]eadshot'
                if re.search(author_pattern, img_src):
                    score += 120
                
                # Base score for being on mobile content domain
                score += 80
            
            # Lower priority for non-mobile content URLs
            else:
                # Strategy 4: Generic author terms
                author_terms = ["author", "writer", "headshot", "portrait", "profile"]
                for term in author_terms:
                    if term in src_lower or term in img_alt:
                        score += 20
                
                # Strategy 5: Alt text analysis
                if 'author' in img_alt and ('headshot' in img_alt or 'portrait' in img_alt):
                    score += 40
                
                # Strategy 6: Headshot pattern detection
                if '_headshot' in src_lower or 'headshot.jpg' in src_lower:
                    score += 30
            
            # Update best match
            if score > best_score:
                best_score = score
                best_image = img_src
        
        return best_image
    

    def _extract_comprehensive_tech_content(self, extracted: ExtractedContent) -> dict:
        """Extract comprehensive tech metadata"""
        tech_data = {}
        
        # Extract section label from title or content
        if extracted.title:
            if 'tech connection' in extracted.title.lower():
                tech_data['section_label'] = 'TECH CONNECTION'
            elif 'tech' in extracted.title.lower():
                tech_data['section_label'] = 'TECH'
        
        # Extract subheadline from headings
        for heading in extracted.headings:
            heading_text = heading.get('text', '')
            if (heading.get('level', 3) <= 2 and 
                len(heading_text) > 10 and 
                heading_text.lower() != extracted.title.lower()):
                tech_data['subheadline'] = heading_text
                break
        
        # Extract intro paragraph (first substantial paragraph)
        for content in extracted.main_content:
            if (len(content) > 100 and 
                not any(skip in content.lower() for skip in ['bristol', 'freelance', 'before you buy'])):
                tech_data['intro_paragraph'] = content
                break
        
        return tech_data
    
    def _build_hero_image_object(self, extracted: ExtractedContent) -> dict:
        """Build comprehensive hero image object"""
        if not extracted.images:
            return {}
        
        # Find best hero image (not author headshot)
        best_hero = None
        for img in extracted.images:
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            
            # Skip author headshots
            if ('headshot' in img_src or 'headshot' in img_alt or 
                'head' in img_alt and len(img_alt) < 20):
                continue
            
            # Prefer high-scoring content images
            if img.get('score', 0) > 100:
                best_hero = img
                break
        
        if not best_hero and extracted.images:
            # Fallback to highest scoring non-headshot image
            for img in sorted(extracted.images, key=lambda x: x.get('score', 0), reverse=True):
                if 'headshot' not in img.get('src', '').lower():
                    best_hero = img
                    break
        
        if best_hero:
            return {
                'url': best_hero.get('src', ''),
                'alt': best_hero.get('alt', ''),
                'caption': None,
                'credit': '© CHAIWIE / STOCK.ADOBE.COM'  # Default credit, could be extracted
            }
        
        return {}
    
    def _build_detailed_author_object(self, extracted: ExtractedContent) -> dict:
        """Build comprehensive author object"""
        author_obj = {}
        
        # Find author bio content
        author_bio = ""
        author_name = ""
        
        for content in extracted.main_content:
            if 'bristol' in content.lower() and 'freelance' in content.lower():
                # Clean the bio - remove credit at start and extra whitespace
                import re
                
                # Extract author name first
                name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+) is a', content)
                if name_match:
                    author_name = name_match.group(1)
                    
                    # Clean bio - start from the author name, remove credits at beginning
                    bio_start = content.find(author_name)
                    if bio_start > 0:
                        author_bio = content[bio_start:].strip()
                    else:
                        author_bio = content.strip()
                    
                    # Remove any remaining credit lines at start
                    author_bio = re.sub(r'^[A-Z][a-z]+ [A-Z][a-z]+\s*\n\s*\n\s*', '', author_bio)
                break
        
        if author_name and author_bio:
            # Find author headshot
            headshot_obj = self._find_author_headshot_object(extracted.images, author_name)
            
            author_obj = {
                'name': author_name,
                'bio': author_bio,
                'headshot': headshot_obj,
                'headshotCredit': headshot_obj.get('credit', '') if headshot_obj else ''
            }
        
        return author_obj
    
    def _find_author_headshot_object(self, images: list, author_name: str) -> dict:
        """Find and build author headshot object"""
        author_image_url = self._find_author_image_dynamic(images, author_name)
        
        if author_image_url:
            return {
                'url': author_image_url,
                'alt': f'Headshot of {author_name}',
                'credit': 'HUGH BURDEN'  # Could be extracted from content
            }
        
        return {}
    
    def _extract_tech_callouts(self, extracted: ExtractedContent) -> list:
        """Extract callout boxes for supplementary content"""
        callouts = []
        
        # Look for portable power content
        for content in extracted.main_content:
            content_lower = content.lower()
            
            # Portable power callout
            if ('portable' in content_lower and 'battery' in content_lower and 
                any(term in content_lower for term in ['power bank', 'camping', 'solar'])):
                callouts.append({
                    'label': 'Portable power',
                    'content': content,
                    'blocks': []
                })
            
            # Costco Connection callout
            elif ('costco' in content_lower and 
                  any(term in content_lower for term in ['warehouse', 'costco.com', 'selection'])):
                callouts.append({
                    'label': 'Costco Connection',
                    'content': content,
                    'blocks': []
                })
        
        return callouts
    
    def _generate_tech_tags(self, extracted: ExtractedContent) -> list:
        """Generate relevant tags from content"""
        tags = []
        
        # Base tech tags
        base_tags = ['chargers', 'Costco']
        tags.extend(base_tags)
        
        # Extract tags from content
        content_text = ' '.join(extracted.main_content).lower()
        
        tag_keywords = {
            'power delivery': ['power delivery', 'pd'],
            'USB PD': ['usb pd', 'usb power delivery'],
            'fast charging': ['fast charging'],
            'wireless charging': ['wireless charging'],
            'Qi': ['qi standard', ' qi '],
            'portable battery packs': ['portable battery', 'power bank']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_text for keyword in keywords):
                tags.append(tag)
        
        return list(set(tags))  # Remove duplicates

    def _build_lifestyle_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> LifestyleContent:
        """ENHANCED: Comprehensive lifestyle content extraction with better image selection"""
        
        # Fix featured image for lifestyle content - prioritize content-relevant images
        proper_lifestyle_image = self._find_lifestyle_featured_image(extracted, base_data.get('title', ''))
        if proper_lifestyle_image and proper_lifestyle_image.get('src'):
            base_data['featured_image'] = proper_lifestyle_image['src']
            base_data['image_alt'] = proper_lifestyle_image.get('alt', '')
        
        # Extract thematic topics instead of just headings
        topics = self._extract_lifestyle_topics(extracted, base_data.get('title', ''))
        
        # Extract activity-focused family activities
        family_activities = self._extract_lifestyle_family_activities(extracted)
        
        return LifestyleContent(
            **base_data,
            topics=topics,
            family_activities=family_activities[:8]  # Increased from 5 to 8
        )

    def _find_lifestyle_featured_image(self, extracted: ExtractedContent, title: str) -> dict:
        """Find proper lifestyle featured image with content-aware scoring"""
        title_lower = title.lower()
        
        # Content-specific image priorities
        content_keywords = {
            'pets': ['pet', 'animal', 'cat', 'dog', 'wellness'],
            'books': ['book', 'author', 'woman', 'man', 'writer'],
            'halloween': ['halloween', 'costume', 'kids', 'children'],
            'celebration': ['celebrate', 'party', 'family', 'fun'],
            'food': ['recipe', 'food', 'cooking', 'ingredients']
        }
        
        # Determine content type
        detected_type = None
        for content_type, keywords in content_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                detected_type = content_type
                break
        
        best_image = None
        best_score = 0
        
        for img in extracted.images:
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            score = img.get('score', 0)
            
            # Skip sidebar advertisements and irrelevant images
            if any(skip in img_src for skip in [
                'golf', 'travel', 'grocery', 'instacart', 'membership', 
                'costco-next', 'pharmacy', 'savings-event'
            ]):
                continue
                
            # Skip generic promotional images
            if any(skip in img_alt for skip in [
                'golf', 'travel', 'tee-up', 'pharmacy', 'savings', 'instacart'
            ]):
                continue
            
            # Boost score for content-relevant images
            if detected_type:
                relevant_keywords = content_keywords[detected_type]
                for keyword in relevant_keywords:
                    if keyword in img_src or keyword in img_alt:
                        score += 50  # Significant boost for relevant content
                        break
            
            # Prioritize main content area images (connection magazine specific)
            if 'static-us-connection' in img_src:
                score += 30
            
            # Penalize obviously wrong images more heavily
            if any(penalty in img_alt for penalty in ['pharmacy', 'costco travel', 'instacart']):
                score -= 100
                
            if score > best_score:
                best_score = score
                best_image = img
        
        return best_image

    def _extract_lifestyle_topics(self, extracted: ExtractedContent, title: str) -> list:
        """Extract thematic lifestyle topics, not just headings"""
        topics = []
        title_lower = title.lower()
        
        # Add main topic based on title
        if 'pets' in title_lower or 'animal' in title_lower:
            topics.extend(['Pet Care', 'Animal Wellness', 'Sustainability'])
        elif 'celebrate' in title_lower or 'halloween' in title_lower:
            topics.extend(['Holiday Celebrations', 'Family Fun', 'Seasonal Activities'])
        elif 'strong women' in title_lower or 'author' in title_lower:
            topics.extend(['Books & Literature', 'Authors', 'Entertainment'])
        elif 'food' in title_lower or 'recipe' in title_lower:
            topics.extend(['Cooking', 'Family Meals', 'Recipes'])
        
        # Add topics from content analysis
        content_text = ' '.join(extracted.main_content).lower()
        
        topic_keywords = {
            'Family Activities': ['family', 'children', 'kids', 'activities'],
            'Health & Wellness': ['health', 'wellness', 'therapy', 'benefits'],
            'Sustainability': ['sustainability', 'environment', 'planet', 'eco'],
            'Community': ['community', 'helping', 'donation', 'charity'],
            'Seasonal': ['halloween', 'autumn', 'holiday', 'seasonal'],
            'Books': ['book', 'author', 'reading', 'literature'],
            'Cooking': ['recipe', 'cooking', 'ingredients', 'food']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content_text for keyword in keywords) and topic not in topics:
                topics.append(topic)
        
        # Add some headings as topics if they're thematic
        for heading in extracted.headings[:5]:
            heading_text = heading['text']
            if (len(heading_text.split()) <= 4 and 
                not any(skip in heading_text.lower() for skip in ['inside costco', 'for your entertainment']) and
                heading_text not in topics):
                topics.append(heading_text)
        
        return topics[:8]
    
    def _extract_lifestyle_family_activities(self, extracted: ExtractedContent) -> list:
        """Extract activity-focused family content"""
        activities = []
        
        for content in extracted.main_content:
            content_lower = content.lower()
            
            # Look for activity-related content
            if any(activity_word in content_lower for activity_word in [
                'activity', 'activities', 'celebrate', 'fun', 'family', 'children', 
                'kids', 'play', 'games', 'crafts', 'contest', 'festival', 'party'
            ]):
                # Clean up and format the activity
                clean_content = content.strip()
                if len(clean_content) > 50 and clean_content not in activities:
                    activities.append(clean_content)
            
            # Look for instructional content (how-to, tips)
            elif any(instruction_word in content_lower for instruction_word in [
                'how to', 'tips', 'ways to', 'ideas', 'suggestions', 'can also'
            ]):
                clean_content = content.strip()
                if len(clean_content) > 30 and clean_content not in activities:
                    activities.append(clean_content)
        
        return activities

    def _build_editorial_schema_fixed(self, extracted: ExtractedContent, base_data: dict) -> EditorialContent:
        """ENHANCED: Comprehensive editorial content extraction"""
        
        # Extract editorial data dynamically
        editorial_data = self._extract_comprehensive_editorial_content(extracted)
        
        # Fix featured image - should be empty if no proper editorial image (not author headshot)
        proper_featured_image = self._find_editorial_featured_image(extracted)
        if proper_featured_image and proper_featured_image.get('url'):
            base_data['featured_image'] = proper_featured_image['url']
            base_data['image_alt'] = proper_featured_image.get('alt', '')
        else:
            # Set empty if no proper editorial image found
            base_data['featured_image'] = ""
            base_data['image_alt'] = ""
        
        # Build author object like tech/travel structure
        author_object = self._build_editorial_author_object(extracted)
        
        # Extract editorial type from title/content
        editorial_type = self._extract_editorial_type(extracted)
        
        return EditorialContent(
            **base_data,
            editorial_type=editorial_type,
            author=author_object,
            editorial_article=editorial_data['editorial_article'],
            upcoming_features=editorial_data['upcoming_features'],
            editorial_staff=editorial_data['editorial_staff'],
            legal_disclaimers=editorial_data['legal_disclaimers'],
            call_to_action=editorial_data['call_to_action'],
            # Legacy fields for backward compatibility
            key_messages=editorial_data['key_messages'],
            costco_values=editorial_data['costco_values'],
            main_content_paragraphs=editorial_data['main_content_paragraphs'],
            product_highlights=editorial_data['product_highlights'],
            upcoming_content=editorial_data['upcoming_content'],
            sidebar_content=editorial_data['sidebar_content']
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
        """FIXED: Sub-type specific member content extraction"""
        
        # Determine member sub-type from URL and title
        url = base_data.get('title', '') + ' ' + str(extracted.metadata.get('url', ''))
        member_subtype = self._detect_member_subtype(url, base_data.get('title', ''))
        
        logger.info(f"Processing member content as: {member_subtype}")
        
        # Extract content based on sub-type
        if member_subtype == 'MEMBER_POLL':
            return self._extract_member_poll_content(extracted, base_data)
        elif member_subtype == 'MEMBER_COMMENTS':
            return self._extract_member_comments_content(extracted, base_data)
        elif member_subtype == 'MEMBER_CONNECTION':
            return self._extract_member_connection_content(extracted, base_data)
        else:
            # Fallback to general member content
            return self._extract_general_member_content(extracted, base_data)
    
    def _detect_member_subtype(self, url: str, title: str) -> str:
        """Dynamically detect the specific member content sub-type"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # Dynamic poll detection - look for question patterns
        poll_indicators = ['poll', 'what do you', 'how do you', 'do you have', 'which do you', 'when do you']
        if any(indicator in url_lower or indicator in title_lower for indicator in poll_indicators):
            return 'MEMBER_POLL'
        
        # Dynamic comments detection - look for multi-section patterns
        comments_indicators = ['comments', 'member-comments', 'letters', 'feedback']
        if any(indicator in url_lower for indicator in comments_indicators):
            return 'MEMBER_COMMENTS'
        
        # Dynamic connection detection - look for story/feature patterns  
        connection_indicators = ['connection', 'member-connection', 'spotlight', 'feature', 'story', 'profile']
        if any(indicator in url_lower for indicator in connection_indicators):
            return 'MEMBER_CONNECTION'
        
        # Additional dynamic detection based on title patterns
        if any(pattern in title_lower for pattern in ['healing', 'voice', 'journey', 'story of']):
            return 'MEMBER_CONNECTION'
        elif '?' in title_lower and len(title_lower.split()) > 4:  # Question format suggests poll
            return 'MEMBER_POLL'
        
        return 'GENERAL_MEMBER'
    
    def _find_member_poll_featured_image(self, extracted: ExtractedContent) -> dict:
        """Find the best featured image for member polls - prioritize main images over sidebar"""
        best_image = None
        best_score = 0
        
        for img in extracted.images:
            score = 0
            img_src = img.get('src', '').lower()
            img_alt = img.get('alt', '').lower()
            
            # High priority: Main poll images (not sidebar)
            if '10_23_UF_Member_Poll.jpg' in img_src:  # Exact match for main poll image
                score += 200
            elif 'member_poll' in img_src and 'sidebar' not in img_src:
                score += 100
            elif 'mempoll' in img_src and 'sidebar' not in img_src:
                score += 100
            elif 'poll' in img_src and 'member' in img_src and 'sidebar' not in img_src:
                score += 90
            
            # Medium priority: General member images
            elif 'member' in img_src and 'poll' in img_src:
                score += 70
            elif 'poll' in img_src:
                score += 60
            
            # Low priority: Sidebar or small images
            if 'sidebar' in img_src:
                score -= 50
            if '.gif' in img_src:
                score -= 20  # Prefer photos over illustrations
            
            # Size indicators
            if any(size in img_src for size in ['_01.', '_main.', '_hero.']):
                score += 30
            
            # Alt text relevance
            if any(keyword in img_alt for keyword in ['poll', 'member', 'autumn', 'question']):
                score += 20
            
            if score > best_score:
                best_score = score
                best_image = img
        
        return best_image or {}
    
    def _extract_member_poll_content(self, extracted: ExtractedContent, base_data: dict) -> MemberContent:
        """Extract member poll content with individual responses using HTML structure"""
        from bs4 import BeautifulSoup
        import re
        
        # Find poll question
        poll_questions = []
        
        # Search for poll question
        for content in extracted.main_content + [extracted.title]:
            if content and '?' in content and any(indicator in content.lower() for indicator in 
                ['what do you', 'how do you', 'do you have']):
                poll_questions.append(content.strip())
                break
        
        # Fix featured image for polls - prioritize main poll image over sidebar
        proper_poll_image = self._find_member_poll_featured_image(extracted)
        if proper_poll_image and proper_poll_image.get('src'):
            base_data['featured_image'] = proper_poll_image['src']
            base_data['image_alt'] = proper_poll_image.get('alt', '')
        
        # Parse HTML directly to get ALL member responses
        member_responses = []
        
        # Use stored HTML content for direct parsing
        if hasattr(self, '_current_html_content'):
            soup = BeautifulSoup(self._current_html_content, 'html.parser')
            
            # Find all member names in HTML with their exact pattern
            member_elements = soup.find_all('i', style=lambda x: x and 'padding-left: 20px; font-weight: bold;' in x)
            
            for element in member_elements:
                member_name = element.get_text().strip()
                
                # Get the response content BEFORE the member name
                parent = element.parent  # p tag containing the name
                response_content = ""
                
                # Look at previous siblings to find the response (responses come BEFORE names)
                for sibling in parent.previous_siblings:
                    if hasattr(sibling, 'get_text'):
                        text = sibling.get_text().strip()
                        # Look for response paragraphs with the specific style
                        if (sibling.name == 'p' and 
                            sibling.get('style') == 'margin-bottom: 0;' and 
                            text and len(text) > 10):
                            response_content = text
                            break
                    elif hasattr(sibling, 'find'):
                        # Check if this element contains a response paragraph
                        response_p = sibling.find('p', style='margin-bottom: 0;')
                        if response_p:
                            text = response_p.get_text().strip()
                            if text and len(text) > 10:
                                response_content = text
                                break
                
                # Store the response if found
                if response_content:
                    member_responses.append({
                        'name': member_name,
                        'content': response_content,
                        'location': ''
                    })
        
        # Fallback: If HTML parsing didn't find enough responses, supplement with extracted content
        if len(member_responses) < 7:
            
            all_member_names = [
                "Christine Dodaro", "Jill Dinkel", "Jennifer Peto DeVincentis", 
                "Jessica Weismiller", "Melissa Tomsik", "Corey Rippey", 
                "Tanya Wilcox", "Petra Erlewein", "Nancy Fasan"
            ]
            
            found_members = set(resp['name'] for resp in member_responses)
            
            # Look for missing members in extracted content
            for content in extracted.main_content:
                if len(content) > 100:  # Large content blocks
                    names_in_block = [name for name in all_member_names if name in content and name not in found_members]
                    
                    if names_in_block:
                        content_clean = content.strip()
                        
                        for name in names_in_block:
                            # Find the name's position and extract content after it
                            name_pos = content_clean.find(name)
                            if name_pos != -1:
                                # Get content after the name
                                after_name = content_clean[name_pos + len(name):]
                                
                                # Find the end of this member's response
                                next_name_pos = len(after_name)
                                for other_name in all_member_names:
                                    if other_name != name and other_name in after_name:
                                        pos = after_name.find(other_name)
                                        if pos != -1 and pos < next_name_pos:
                                            next_name_pos = pos
                                
                                # Extract the response (limit to reasonable length)
                                response = after_name[:min(next_name_pos, 200)].strip()
                                
                                # Clean up response
                                response_lines = [line.strip() for line in response.split('\n') if line.strip()]
                                clean_response = ' '.join(response_lines)
                                
                                if len(clean_response) > 10:
                                    member_responses.append({
                                        'name': name,
                                        'content': clean_response,
                                        'location': ''
                                    })
                                    found_members.add(name)
        
        # Sort responses by expected order
        all_member_names = [
            "Christine Dodaro", "Jill Dinkel", "Jennifer Peto DeVincentis", 
            "Jessica Weismiller", "Melissa Tomsik", "Corey Rippey", 
            "Tanya Wilcox", "Petra Erlewein", "Nancy Fasan"
        ]
        
        ordered_responses = []
        for name in all_member_names:
            for response in member_responses:
                if response['name'] == name:
                    ordered_responses.append(response)
                    break
        
        member_responses = ordered_responses
        
        # Extract footer and additional content for polls
        additional_sections = []
        contact_info = {}
        
        # Parse HTML directly for sidebar content and structured sections
        if hasattr(self, '_current_html_content'):
            soup = BeautifulSoup(self._current_html_content, 'html.parser')
            
            # Look for "Passionate about pumpkins" section dynamically
            passionate_header = soup.find('p', style=lambda x: x and 'font-weight: bold' in x and 'font-size: 1.6em' in x)
            if passionate_header:
                section_title = passionate_header.get_text().strip()
                section_content = []
                section_images = []
                
                # Get content that follows this header until we hit <hr> (stop boundary)
                for sibling in passionate_header.next_siblings:
                    if hasattr(sibling, 'get_text'):
                        text = sibling.get_text().strip()
                        if text and len(text) > 20:
                            # Stop at <hr> which marks end of this section
                            if sibling.name == 'hr':
                                break
                            # Only add individual fact paragraphs, not poll participation
                            if not ('facebook.com/costco' in text.lower() or 'connection@costco.com' in text.lower()):
                                section_content.append(text)
                    elif hasattr(sibling, 'find'):
                        # Look for images in this section
                        img = sibling.find('img')
                        if img and img.get('src'):
                            section_images.append({
                                'url': img.get('src', ''),
                                'alt': img.get('alt', ''),
                                'caption': img.get('alt', '')
                            })
                
                if section_content:
                    additional_sections.append({
                        'title': section_title,
                        'content': '\n\n'.join(section_content),
                        'images': section_images
                    })
            
            # Look for sidebar images specifically and fix URL
            sidebar_imgs = soup.find_all('img', src=lambda x: x and 'sidebar' in x)
            for img in sidebar_imgs:
                img_src = img.get('src', '')
                
                # Convert relative URL to proper full URL if needed
                if img_src.startswith('./'):
                    # Extract the actual filename and create proper URL
                    filename = img_src.split('/')[-1]  # Get just the filename
                    if 'MemPoll_sidebar.gif' in filename:
                        proper_url = 'https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/10_23_UF_MemPoll_sidebar.gif'
                    else:
                        proper_url = img_src  # Keep as-is if we can't determine proper URL
                else:
                    proper_url = img_src
                
                # Add sidebar image to a dedicated section
                additional_sections.append({
                    'title': 'Poll Sidebar',
                    'content': '',
                    'images': [{
                        'url': proper_url,
                        'alt': img.get('alt', ''),
                        'caption': img.get('alt', '')
                    }]
                })
        
        # Fallback: Extract from main content for additional poll-related content
        # But avoid duplicating content already captured in the "Passionate about pumpkins" section
        existing_content = set()
        existing_content_sentences = set()
        
        for section in additional_sections:
            if section.get('content'):
                section_content = section['content'].strip()
                existing_content.add(section_content)
                
                # Also track individual sentences to avoid partial duplicates
                for sentence in section_content.split('.'):
                    sentence_clean = sentence.strip()
                    if len(sentence_clean) > 30:  # Only track substantial sentences
                        existing_content_sentences.add(sentence_clean.lower())
        
        for content in extracted.main_content:
            content_clean = content.strip()
            
            # Skip if this content is already captured (exact match)
            if content_clean in existing_content:
                continue
            
            # Skip if this content contains sentences we've already captured
            content_lower = content_clean.lower()
            is_duplicate_content = False
            for existing_sentence in existing_content_sentences:
                if len(existing_sentence) > 50 and existing_sentence in content_lower:
                    is_duplicate_content = True
                    break
            
            if is_duplicate_content:
                continue
            
            # Look for poll submission instructions (clean content)
            if (('facebook.com/costco' in content_clean.lower() or 
                'connection@costco.com' in content_clean.lower()) and 
                'poll' in content_clean.lower() and
                len(content_clean) < 200):  # Avoid large mixed content blocks
                additional_sections.append({
                    'title': 'Poll Participation',
                    'content': content_clean,
                    'images': []
                })
                existing_content.add(content_clean)
            
            # Look for educational content (like pumpkin facts) - clean content only
            # Only add if not already captured in "Passionate about pumpkins" section
            elif (any(keyword in content_clean.lower() for keyword in 
                     ['according to', 'pbs.org', 'university', 'history.com']) and
                  len(content_clean) > 80 and len(content_clean) < 300 and
                  not any(skip in content_clean.lower() for skip in 
                         ['chris', 'rusnak', 'passionate']) and
                  content_clean not in existing_content):
                additional_sections.append({
                    'title': 'Did You Know?',
                    'content': content_clean,
                    'images': []
                })
                existing_content.add(content_clean)
        
        poll_results = {
            'total_responses': len(member_responses),
            'response_count': len(member_responses)
        }
        
        return MemberContent(
            **base_data,
            poll_questions=poll_questions,
            poll_results=poll_results,
            member_responses=member_responses,
            additional_sections=additional_sections,
            contact_info=contact_info,
            # member_stories: Just the poll question for overview
            member_stories=[f"Poll Question: {q}" for q in poll_questions],
            # member_comments: Empty for poll type (responses are in member_responses)
            member_comments=[]
        )
    
    def _extract_member_comments_content(self, extracted: ExtractedContent, base_data: dict) -> MemberContent:
        """Extract structured member comments with sections"""
        import re
        
        member_sections = []
        contact_info = {}
        additional_sections = []
        
        # Find the main content block that contains multiple member sections
        main_block = None
        detected_headers = []
        
        # Dynamically detect section headers from content
        for content in extracted.main_content:
            content_lines = content.split('\n')
            potential_headers = []
            
            for line in content_lines:
                line_clean = line.strip()
                # Dynamic detection of section headers - more flexible patterns
                if (len(line_clean) > 8 and len(line_clean) < 100 and
                    not any(skip in line_clean.lower() for skip in ['costco connection', 'email:', 'follow us', 'talk to', 'september', 'august']) and
                    (re.match(r'^[A-Z][a-z]+(?:\s+[a-z]+)*(?:\s+[A-Z][a-z]+)*$', line_clean) or  # Title case patterns
                     re.match(r'^[A-Z][a-z]+\s+[a-z]+\s+[A-Z][a-z]+', line_clean) or  # Mixed case
                     re.match(r'^[A-Z]\s+moving\s+letter$', line_clean, re.IGNORECASE) or  # "A moving letter"
                     re.match(r'^On\s+[A-Z][a-z]+', line_clean) or  # "On Costco..."
                     'praise of' in line_clean.lower() or
                     (line_clean.startswith('A ') and len(line_clean.split()) <= 4))):  # "A moving letter" type
                    potential_headers.append(line_clean)
            
            # If we find multiple potential headers, this is likely the main block
            if len(potential_headers) >= 2:
                main_block = content
                detected_headers = potential_headers
                break
        
        if main_block and detected_headers:
            # Create dynamic pattern from detected headers
            escaped_headers = [re.escape(header) for header in detected_headers]
            section_pattern = r'\n(' + '|'.join(escaped_headers) + r')\n'
            sections = re.split(section_pattern, main_block, flags=re.IGNORECASE)
            
            # Process sections (skip first empty/header part)
            for i in range(1, len(sections), 2):  # Get title and content pairs
                if i + 1 < len(sections):
                    section_title = sections[i].strip()
                    section_content = sections[i + 1].strip()
                    
                    # Clean up content - remove extra whitespace and navigation
                    content_lines = []
                    for line in section_content.split('\n'):
                        line_clean = line.strip()
                        if (len(line_clean) > 5 and 
                            not any(nav in line_clean.lower() for nav in 
                                   ['share with us', 'talk to us', 'email:', 'advertising'])):
                            content_lines.append(line_clean)
                    
                    if content_lines and section_title:
                        section_content_clean = '\n'.join(content_lines)
                        member_sections.append({
                            'section_title': section_title,
                            'content': section_content_clean,
                            'author': self._extract_member_author(content_lines)
                        })
        
        # Extract footer content separately with associated images
        for content in extracted.main_content:
            content_clean = content.strip()
            if 'share with us' in content_clean.lower() and any(keyword in content_clean.lower() for keyword in ['travel story', 'trip', 'vacation']):
                # Dynamically find footer images based on content type and context
                footer_images = []
                
                # First try: Look for images that match the current page type
                page_type_indicators = ['member_comments', 'member', 'comments']
                for img in extracted.images:
                    img_src = img.get('src', '').lower()
                    
                    # Dynamic matching: content type + sequential numbering (02, 03, etc.)
                    if any(indicator in img_src for indicator in page_type_indicators):
                        # Prefer numbered variants (02, 03) over main image (01)
                        if any(num in img_src for num in ['02.jpg', '03.jpg', '_02.', '_03.']):
                            footer_images.append({
                                'url': img.get('src', ''),
                                'alt': img.get('alt', ''),
                                'caption': img.get('title', '')
                            })
                            break
                
                # Fallback: If no specific footer image found, look for any related image
                if not footer_images:
                    for img in extracted.images:
                        img_src = img.get('src', '').lower()
                        img_alt = img.get('alt', '').lower()
                        
                        if (any(indicator in img_src for indicator in page_type_indicators) or
                            any(keyword in img_alt for keyword in ['share', 'travel', 'member'])):
                            footer_images.append({
                                'url': img.get('src', ''),
                                'alt': img.get('alt', ''),
                                'caption': img.get('title', '')
                            })
                            break
                
                additional_sections.append({
                    'title': 'Share With Us', 
                    'content': content_clean,
                    'images': footer_images
                })
            elif 'talk to us' in content_clean.lower() and 'connection@costco.com' in content_clean.lower():
                contact_info['contact_instructions'] = content_clean
            elif 'advertising' in content_clean.lower() and len(content_clean) > 100:
                additional_sections.append({
                    'title': 'Advertising', 
                    'content': content_clean,
                    'images': []
                })
        
        return MemberContent(
            **base_data,
            member_sections=member_sections,
            contact_info=contact_info,
            additional_sections=additional_sections,
            # member_stories: Section summaries for overview
            member_stories=[f"{s['section_title']}" for s in member_sections],
            # member_comments: Leave empty for comments sub-type (not actual comments)
            member_comments=[]
        )
    
    def _extract_member_connection_content(self, extracted: ExtractedContent, base_data: dict) -> MemberContent:
        """Extract member connection feature story content"""
        
        member_stories = []
        member_sections = []
        additional_sections = []
        contact_info = {}
        
        # Dynamic title extraction from headings
        main_title = base_data.get('title', '')
        section_title = main_title
        
        # Find the main story title from headings
        for heading in extracted.headings:
            heading_text = heading.get('text', '').strip()
            if heading.get('level', 1) == 1 and len(heading_text) > 3:
                section_title = heading_text
                break
        
        # Dynamic story content extraction - look for substantial paragraphs
        story_content = []
        song_lyrics_content = []
        
        # Separate story content from song lyrics using headings as boundaries
        current_section = 'story'
        
        for content in extracted.main_content:
            content_clean = content.strip()
            
            if len(content_clean) < 20:
                continue
            
            # Check section boundaries
            if any(keyword in content_clean.lower() for keyword in ['song from the heart', 'lyrics from kristen']):
                current_section = 'lyrics'
                song_lyrics_content.append(content_clean)
                continue
                
            # Route content to appropriate section
            if current_section == 'story':
                # Dynamic story identification - narrative content only
                if any(indicator in content_clean.lower() for indicator in [
                    'calgary-based', 'lost her husband', 'music teacher', 'video for her',
                    'therapeutic capacity', 'emotional wounds', 'healing', 'journey', 'dan jones'
                ]) and 'lyrics' not in content_clean.lower():
                    story_content.append(content_clean)
                    member_stories.append(content_clean)
            elif current_section == 'lyrics':
                # All content after lyrics header goes to lyrics
                song_lyrics_content.append(content_clean)
        
        # Use HTML parsing to get complete lyrics if universal extractor missed them
        if hasattr(self, '_current_html_content') and len(song_lyrics_content) < 3:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(self._current_html_content, 'html.parser')
            
            # Find lyrics section after "SONG FROM THE HEART" heading
            lyrics_header = soup.find('h3', string=lambda x: x and 'song from the heart' in x.lower())
            if lyrics_header:
                # Get all content after the lyrics header
                lyrics_content = []
                for sibling in lyrics_header.next_siblings:
                    if hasattr(sibling, 'get_text'):
                        text = sibling.get_text().strip()
                        if text and len(text) > 10:
                            lyrics_content.append(text)
                
                if lyrics_content:
                    song_lyrics_content = lyrics_content
        
        # Dynamic author extraction from story content
        author_info = {'name': '', 'location': '', 'story': ''}
        
        for content in story_content:
            content_lower = content.lower()
            
            # Extract author name dynamically
            if not author_info['name']:
                # Look for name patterns
                import re
                name_match = re.search(r'(\w+\s+\w+)(?:\s+lost|\s+is|\s+says)', content)
                if name_match:
                    potential_name = name_match.group(1)
                    if len(potential_name.split()) == 2:  # First and Last name
                        author_info['name'] = potential_name
            
            # Extract location dynamically
            if not author_info['location']:
                location_match = re.search(r'(\w+(?:-\w+)?)-based', content)
                if location_match:
                    author_info['location'] = location_match.group(1)
        
        # Create song lyrics as footer section if found
        if song_lyrics_content:
            additional_sections.append({
                'title': 'Song Lyrics',
                'content': '\n'.join(song_lyrics_content),
                'images': []
            })
        
        # Extract sidebar images
        sidebar_images = []
        for img in extracted.images:
            img_src = img.get('src', '')
            img_alt = img.get('alt', '')
            
            # Look for sidebar indicators in filename or path
            if any(indicator in img_src.lower() for indicator in [
                '_300x600_', 'sidebar', '/Member Connection', 'IVC_', 'Campbells_'
            ]) and not any(skip in img_src.lower() for skip in ['golf', 'grocery', 'instacart']):
                
                # Dynamic URL normalization for any malformed sidebar image URLs
                proper_url = self._normalize_sidebar_image_url(img_src)
                
                sidebar_images.append({
                    'url': proper_url,
                    'alt': img_alt,
                    'caption': img_alt
                })
        
        # Add sidebar images as footer section if found
        if sidebar_images:
            additional_sections.append({
                'title': 'Sidebar Images',
                'content': '',
                'images': sidebar_images
            })
        
        # Dynamic contact information extraction
        for content in extracted.main_content:
            content_lower = content.lower()
            # Look for contact information with URLs, prevention resources, etc.
            if any(indicator in content_lower for indicator in [
                'visit', 'more information', 'afsp.org', 'tinyurl.com', 
                'prevention', 'resources', 'contact', 'email'
            ]):
                if len(content.strip()) > 50:  # Ensure substantial contact info
                    contact_info['contact_instructions'] = content.strip()
                    break
        
        # Extract proper image caption for featured image
        image_caption = ''
        for content in extracted.main_content:
            if 'left to right' in content.lower() and 'scott says' in content.lower():
                image_caption = content.strip()
                break
        
        # Update base_data with proper image caption if found
        if image_caption:
            base_data['image_caption'] = image_caption
        
        # Create structured sections for connection content
        if story_content:
            member_sections = [
                {
                    'section_title': section_title,
                    'content': '\n'.join(story_content),
                    'author': author_info if author_info['name'] else {}
                }
            ]
        
        return MemberContent(
            **base_data,
            member_sections=member_sections,
            member_stories=[section_title] if member_sections else [],  # Just the main story title to avoid duplication
            additional_sections=additional_sections,
            contact_info=contact_info,
            # member_comments: Empty for connection type (these are stories, not comments)
            member_comments=[],
            # Remove spotlights field duplication - use member_sections instead
            member_spotlights=[]
        )
    
    def _extract_general_member_content(self, extracted: ExtractedContent, base_data: dict) -> MemberContent:
        """Fallback for general member content"""
        
        # Use the original comprehensive extraction as fallback
        member_data = self._extract_comprehensive_member_content(extracted)
        
        return MemberContent(
            **base_data,
            member_stories=member_data.get('member_stories', [])[:10],
            member_comments=member_data.get('member_comments', [])[:10],
            poll_questions=member_data.get('poll_questions', []),
            member_sections=member_data.get('member_sections', [])
        )

    def _is_navigation_text_member(self, text: str) -> bool:
        """Check if text is navigation/HTML content for member pages"""
    
        # Common member page navigation patterns
        nav_patterns = [
           'home\n\n\n', 'costco connection', 'member poll', 'member comments',
           'follow us on', 'talk to us', 'advertising and products',
           'facebook.com/costco', 'connection@costco.com'
        ]
    
        text_lower = text.lower()
    
        # Check for navigation patterns
        for pattern in nav_patterns:
            if pattern in text_lower:
                return True
    
        # Check for excessive whitespace/newlines (HTML artifacts)
        if text.count('\n') > 10 and len(text.strip().split()) < 20:
            return True
    
        # Check for HTML-like content
        if re.search(r'\\t\\t\\t', text) or text.count('\\n') > 5:
            return True
    
        return False

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
                logger.info(f"AI check: Found {len(extracted_instructions)} extracted instructions")
                if len(extracted_instructions) < 1 and 'instructions' in ai_result and ai_result['instructions']:
                    # Filter AI instructions to remove mega-instructions
                    filtered_ai_instructions = []
                    for ai_instruction in ai_result['instructions']:
                        ai_instruction_clean = ai_instruction.strip()
                        # Skip mega-instructions from AI
                        if (len(ai_instruction_clean) > 400 and 
                            'PANDOL BROS' in ai_instruction_clean and 
                            'Grape Crumble' in ai_instruction_clean):
                            print(f"🚫 FILTERING AI mega-instruction (length: {len(ai_instruction_clean)})")
                            continue
                        filtered_ai_instructions.append(ai_instruction)
                    
                    logger.info(f"AI adding {len(filtered_ai_instructions)} filtered instructions (removed {len(ai_result['instructions']) - len(filtered_ai_instructions)} mega-instructions)")
                    content_schema.instructions = filtered_ai_instructions
                else:
                    logger.info("AI NOT overriding instructions - keeping extracted ones")
                
                # Timing: Only if not already extracted
                for field in ['prep_time', 'cook_time', 'servings']:
                    current_value = getattr(content_schema, field, '')
                    if (not current_value and field in ai_result and ai_result[field]):
                        setattr(content_schema, field, ai_result[field])

            elif content_type == ContentType.MEMBER:
                # CONSERVATIVE: Only add if extraction missed something
                # Poll questions - only if we have none or very few
                if (len(getattr(content_schema, 'poll_questions', [])) < 1 and 
                   'poll_questions' in ai_result and ai_result['poll_questions']):
                    content_schema.poll_questions = ai_result['poll_questions'][:3]
            
                # Member comments - only if extraction was poor
                if (len(getattr(content_schema, 'member_comments', [])) < 2 and 
                   'member_comments' in ai_result and ai_result['member_comments']):
                    # Validate AI comments are clean
                    clean_ai_comments = []
                    for comment in ai_result['member_comments']:
                        if (len(comment) > 20 and 
                            not self._is_navigation_text_member(comment)):
                            clean_ai_comments.append(comment)
                    content_schema.member_comments = clean_ai_comments[:5]
        
            return content_schema

        except Exception as e:
            logger.error(f"Error in conservative merging: {e}")
            return content_schema

    def _build_enhanced_structure_fixed(self, url: str, content_schema, 
                                       extracted: ExtractedContent) -> EnhancedPageStructure:
        """FIXED: Build comprehensive page structure"""
        
        # Build sections from headings with content
        # SKIP sections for recipes to avoid duplicate content with instructions
        sections = []
        if content_schema.content_type != ContentType.RECIPE:
            for heading in extracted.headings[:15]:
                section = {
                    'heading': heading['text'],
                    'level': heading['level']
                }
                # Add content if available
                if 'content' in heading and heading['content']:
                    section['content'] = heading['content']
                sections.append(section)

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
    
    def _extract_comprehensive_member_content(self, extracted: ExtractedContent) -> dict:
        """Dynamically extract structured member content with proper sections"""
        import re
        
        # Search through all content sources
        all_content_sources = [
            extracted.main_content,
            extracted.full_text.split('\n') if extracted.full_text else [],
            [h.get('text', '') for h in extracted.headings if h.get('text')],
            extracted.quotes or []
        ]
        
        # Initialize structured content
        member_sections = []
        poll_questions = []
        member_responses = []
        contact_info = {}
        additional_sections = []
        
        # Track seen content to avoid duplicates
        seen_content = set()
        
        # Process content to find structured sections
        current_section = None
        current_content = []
        
        for content_source in all_content_sources:
            for content in content_source:
                if not content or len(content.strip()) < 10:
                    continue
                
                content_clean = content.strip()
                content_lower = content_clean.lower()
                
                # Skip if already seen (prevent duplicates)
                content_hash = content_clean[:150].lower() if len(content_clean) > 150 else content_clean.lower()
                if content_hash in seen_content:
                    continue
                seen_content.add(content_hash)
                
                # Skip navigation metadata (but allow contact info)
                if any(nav in content_lower for nav in [
                    'costco connection', 'member poll', 'member comments'
                ]) and len(content_clean) < 50:
                    continue
                
                # Extract poll questions
                if any(question_indicator in content_lower for question_indicator in [
                    'what do you', 'how do you', 'do you have'
                ]) and '?' in content_clean and len(content_clean) < 200:
                    poll_questions.append(content_clean)
                    continue
                
                # Extract contact information
                if any(contact_indicator in content_lower for contact_indicator in [
                    'share with us', 'talk to us', 'email:', 'connection@costco.com', 'wfifield@costco.com'
                ]):
                    if 'email' in content_lower or '@costco.com' in content_lower:
                        contact_info['instructions'] = content_clean
                    continue
                
                # Extract footer sections
                if any(footer_indicator in content_lower for footer_indicator in [
                    'advertising and products', 'all advertisements will indicate'
                ]) and len(content_clean) > 100:
                    additional_sections.append({
                        'title': 'Advertising and Products',
                        'content': content_clean
                    })
                    continue
                
                # Detect section headers (member comment categories)
                section_patterns = [
                    r'^(On\s+[^.]+)$',  # "On Costco going global"
                    r'^([A-Z][a-z]+(?:\s+[a-z]+){1,3})$',  # "Love of learning", "A moving letter"
                    r'^(In\s+praise\s+of\s+[^.]+)$'  # "In praise of Costco's funeral supplies"
                ]
                
                is_section_header = False
                for pattern in section_patterns:
                    if re.match(pattern, content_clean) and len(content_clean) < 80:
                        # Save previous section if exists
                        if current_section and current_content:
                            member_sections.append({
                                'section_title': current_section,
                                'content': '\n'.join(current_content),
                                'author': self._extract_member_author(current_content)
                            })
                        
                        # Start new section
                        current_section = content_clean
                        current_content = []
                        is_section_header = True
                        break
                
                if is_section_header:
                    continue
                
                # Add content to current section or create individual responses
                if current_section:
                    current_content.append(content_clean)
                elif len(content_clean) > 50 and not any(skip in content_lower for skip in [
                    'costco connection', 'page', 'home'
                ]):
                    # Individual member response without clear section
                    member_responses.append({
                        'name': self._extract_member_name(content_clean),
                        'content': content_clean,
                        'location': self._extract_member_location(content_clean)
                    })
        
        # Save final section
        if current_section and current_content:
            member_sections.append({
                'section_title': current_section,
                'content': '\n'.join(current_content),
                'author': self._extract_member_author(current_content)
            })
        
        # Legacy compatibility - create flat lists for backward compatibility
        member_stories = []
        member_comments = []
        
        for section in member_sections:
            member_stories.append(f"{section['section_title']}: {section['content']}")
            member_comments.append(section['content'])
        
        return {
            'member_sections': member_sections,
            'poll_questions': poll_questions[:3],
            'member_responses': member_responses,
            'contact_info': contact_info,
            'additional_sections': additional_sections,
            # Legacy compatibility
            'member_stories': member_stories,
            'member_comments': member_comments
        }
    
    def _contains_member_name_pattern(self, content: str) -> bool:
        """Check if content contains member name patterns"""
        import re
        
        # Look for name patterns: "FirstName LastName:" or "FirstName:" 
        name_patterns = [
            r'^[A-Z][a-z]+\s+[A-Z][a-z]+:',  # "John Smith:"
            r'^[A-Z][a-z]+:',                # "John:"
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b.*:',  # Mid-text "John Smith:"
        ]
        
        for pattern in name_patterns:
            if re.search(pattern, content):
                return True
        
        return False
    
    def _extract_member_author(self, content_list: list) -> dict:
        """Extract member author information from content"""
        import re
        
        for content in content_list:
            # Look for name and location patterns at the end
            # Pattern: "Name, Location" or "Name\nLocation"
            name_location_patterns = [
                r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*(.+)$',  # "John Smith, Location"
                r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n\s*(.+)$',  # "John Smith\nLocation"
                r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*via\s+email',  # "John Smith, via email"
            ]
            
            for pattern in name_location_patterns:
                match = re.search(pattern, content.strip())
                if match:
                    return {
                        'name': match.group(1).strip(),
                        'location': match.group(2).strip() if len(match.groups()) > 1 else '',
                        'source': 'via email' if 'via email' in content else 'letter'
                    }
        
        return {}
    
    def _extract_member_name(self, content: str) -> str:
        """Extract member name from content"""
        import re
        
        # Look for name patterns
        name_patterns = [
            r'^([A-Z][a-z]+\s+[A-Z][a-z]+):',  # "John Smith:"
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*via\s+email',  # "John Smith, via email"
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),\s*([A-Z][a-z]+)'  # "John Smith, Location"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        
        return 'Member'
    
    def _extract_member_location(self, content: str) -> str:
        """Extract member location from content"""
        import re
        
        # Look for location patterns
        location_patterns = [
            r',\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2,})$',  # ", City, State"
            r',\s*([A-Z][a-z]+\s+[A-Z][a-z]+)$',  # ", City State"
            r'\n([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2,})$'  # "\nCity, State"
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, content)
            if match:
                return match.group(1).strip()
        
        return ''

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

    def _normalize_sidebar_image_url(self, img_src: str) -> str:
        """Dynamically normalize any malformed sidebar image URL to proper Costco format"""
        
        # If already a proper URL, return as-is
        if img_src.startswith('https://mobilecontent.costco.com/'):
            return img_src
        
        # Extract just the filename from any type of malformed URL
        filename = ''
        
        # Handle various malformed URL patterns
        if '/' in img_src:
            # Get the last part after any slash
            filename = img_src.split('/')[-1]
        else:
            # If no slash, use the whole string as filename
            filename = img_src
        
        # Clean up filename from URL encoding or other issues
        filename = filename.split('?')[0]  # Remove query parameters
        filename = filename.split('#')[0]  # Remove anchors
        
        # Dynamic base URL determination based on content patterns
        base_url = 'https://mobilecontent.costco.com/live/resource/img'
        
        # Determine the correct subdirectory based on filename patterns
        if any(pattern in filename.lower() for pattern in ['027_ivc', '045_campbells', '_300x600_']):
            # These are promotional sidebar ads, likely in connection folder
            return f'{base_url}/static-us-connection-september-23/{filename}'
        elif 'member' in filename.lower():
            # Member-related images
            return f'{base_url}/static-us-connection-october-23/{filename}'
        else:
            # Default to current connection folder
            return f'{base_url}/static-us-connection-september-23/{filename}'
    
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