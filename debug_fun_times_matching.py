#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_fun_times_matching():
    """Debug why images match 'Fun times for all'"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Test all 4 images against different headings
    test_images = [
        {'src': '10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'},
        {'src': '10_23_UF_CostcoLife_Glasses.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Card.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Rollups.jpg', 'alt': 'Spinach Lasagna Roll Ups'}
    ]
    
    headings = [
        "Celebrate, your way",
        "Fun times for all",  
        "Donation program",
        "Where has your card been?",
        "Spinach Lasagna Roll Ups"
    ]
    
    print(f"🔍 DEBUGGING IMAGE-TO-HEADING MATCHING:")
    
    for img in test_images:
        filename = img['src'].split('/')[-1]
        print(f"\n📷 Testing: {filename}")
        print(f"   Alt: {img['alt']}")
        
        for heading in headings:
            match = extractor._is_image_specifically_for_section(img, heading, "sample content")
            match_contextual = extractor._is_image_contextually_relevant(img, heading, "sample content")
            
            if match or match_contextual:
                match_type = "SPECIFIC" if match else "CONTEXTUAL"
                print(f"   ✅ MATCHES '{heading}' ({match_type})")

if __name__ == "__main__":
    debug_fun_times_matching()