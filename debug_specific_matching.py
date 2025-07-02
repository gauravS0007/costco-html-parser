#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_specific_matching():
    """Debug the specific image-to-section matching logic"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Test data based on what we found
    test_images = [
        {'src': '10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'},
        {'src': '10_23_UF_CostcoLife_Glasses.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Card.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Rollups.jpg', 'alt': 'Spinach Lasagna Roll Ups'}
    ]
    
    test_headings = [
        'Celebrate, your way',
        'Fun times for all', 
        'Donation program',
        'Where has your card been?',
        'Spinach Lasagna Roll Ups'
    ]
    
    print("🔍 TESTING SPECIFIC IMAGE-TO-SECTION MATCHING:")
    
    for img in test_images:
        filename = img['src'].split('/')[-1]
        print(f"\n📷 Image: {filename}")
        print(f"   Alt: {img['alt']}")
        
        for heading in test_headings:
            match = extractor._is_image_specifically_for_section(img, heading, "")
            print(f"   vs '{heading}': {'✅ MATCH' if match else '❌ no match'}")
            
            # Also test the general contextual relevance
            general_match = extractor._is_image_contextually_relevant(img, heading, "")
            if general_match and not match:
                print(f"     (general match: ✅)")

if __name__ == "__main__":
    debug_specific_matching()