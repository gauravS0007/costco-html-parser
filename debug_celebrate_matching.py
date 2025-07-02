#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_celebrate_matching():
    """Debug why all images match 'Celebrate, your way'"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Test all 4 images against "Celebrate, your way"
    test_images = [
        {'src': '10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'},
        {'src': '10_23_UF_CostcoLife_Glasses.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Card.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Rollups.jpg', 'alt': 'Spinach Lasagna Roll Ups'}
    ]
    
    heading = "Celebrate, your way"
    section_text = "Some section content"
    
    print(f"🔍 DEBUGGING WHY ALL IMAGES MATCH '{heading}':")
    
    for img in test_images:
        filename = img['src'].split('/')[-1]
        print(f"\n📷 Testing: {filename}")
        print(f"   Alt: {img['alt']}")
        
        # Test the specific matching step by step
        match = extractor._is_image_specifically_for_section(img, heading, section_text)
        print(f"   Result: {'✅ MATCH' if match else '❌ NO MATCH'}")
        
        # Let me manually check each condition in the method
        src = img['src'].lower()
        alt = img['alt'].lower()
        heading_lower = heading.lower()
        section_lower = section_text.lower()
        filename_lower = src.split('/')[-1] if src else ''
        
        print(f"   Details:")
        print(f"     filename: {filename_lower}")
        print(f"     alt: {alt}")
        print(f"     heading: {heading_lower}")
        
        # Check each condition manually
        # 1. Glasses/Donation
        glasses_match = 'glasses' in filename_lower and any(word in heading_lower for word in ['donation', 'optical', 'program'])
        print(f"     Glasses/donation match: {glasses_match}")
        
        # 2. Card/Travel
        card_match = 'card' in filename_lower and any(word in heading_lower for word in ['card', 'where', 'been', 'travel'])
        print(f"     Card/travel match: {card_match}")
        
        # 3. Recipe/Food
        recipe_match = any(food_word in filename_lower for food_word in ['rollup', 'lasagna', 'recipe']) and \
                       any(food_word in heading_lower for food_word in ['lasagna', 'recipe', 'roll', 'spinach'])
        print(f"     Recipe/food match: {recipe_match}")
        
        # 4. Halloween/Costume
        halloween_match = any(holiday_word in filename_lower for holiday_word in ['halloween', 'costume']) and \
                         any(main_word in heading_lower for main_word in ['halloween', 'celebrate', 'costume'])
        print(f"     Halloween/costume match: {halloween_match}")
        
        # 7. Alt text matching
        if alt and heading_lower:
            alt_words = set(alt.replace(',', '').split())
            heading_words = set(heading_lower.replace(',', '').split())
            meaningful_overlap = alt_words.intersection(heading_words) - {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
                'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are'
            }
            alt_text_match = meaningful_overlap and len(meaningful_overlap) >= 1
            print(f"     Alt text overlap: {meaningful_overlap}")
            print(f"     Alt text match: {alt_text_match}")

if __name__ == "__main__":
    debug_celebrate_matching()