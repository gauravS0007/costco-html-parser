#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_halloween_match():
    """Debug why Halloween image matches multiple sections"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Halloween image
    img = {'src': '10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'}
    
    test_headings = [
        'Celebrate, your way',
        'Fun times for all'
    ]
    
    print("🔍 DEBUGGING HALLOWEEN IMAGE MATCHING:")
    print(f"Image: {img['src']}")
    print(f"Alt: {img['alt']}")
    
    for heading in test_headings:
        print(f"\nTesting against: '{heading}'")
        
        # Test the specific matching conditions one by one
        src = img['src'].lower()
        alt = img['alt'].lower()
        heading_lower = heading.lower()
        filename = src.split('/')[-1] if src else ''
        
        print(f"  filename: {filename}")
        print(f"  alt: {alt}")
        print(f"  heading_lower: {heading_lower}")
        
        # Check each condition
        print(f"  Conditions:")
        
        # Halloween/Costume matching
        holiday_words_in_filename = [word for word in ['halloween', 'costume'] if word in filename]
        holiday_words_in_heading = [word for word in ['halloween', 'celebrate', 'fun', 'costume'] if word in heading_lower]
        
        print(f"    Holiday words in filename: {holiday_words_in_filename}")
        print(f"    Holiday words in heading: {holiday_words_in_heading}")
        
        if holiday_words_in_filename and holiday_words_in_heading:
            print(f"    ✅ Holiday/costume match: TRUE")
        else:
            print(f"    ❌ Holiday/costume match: FALSE")
            
        # Alt text matching
        alt_words = set(alt.replace(',', '').split())
        heading_words = set(heading_lower.replace(',', '').split())
        meaningful_overlap = alt_words.intersection(heading_words) - {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are'
        }
        
        print(f"    Alt words: {alt_words}")
        print(f"    Heading words: {heading_words}")
        print(f"    Meaningful overlap: {meaningful_overlap}")
        
        if meaningful_overlap and len(meaningful_overlap) >= 1:
            print(f"    ✅ Alt text match: TRUE")
        else:
            print(f"    ❌ Alt text match: FALSE")
        
        # Final result
        match = extractor._is_image_specifically_for_section(img, heading, "")
        print(f"  Final result: {'✅ MATCH' if match else '❌ NO MATCH'}")

if __name__ == "__main__":
    debug_halloween_match()