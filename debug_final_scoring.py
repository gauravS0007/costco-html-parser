#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_final_scoring():
    """Debug the final scoring for each specific image-section combination"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Test the 4 main content images
    test_images = [
        {'src': '10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'},
        {'src': '10_23_UF_CostcoLife_Glasses.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Card.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Rollups.jpg', 'alt': 'Spinach Lasagna Roll Ups'}
    ]
    
    # Test headings from the actual extraction
    test_headings = [
        'Celebrate, your way',
        'Fun times for all', 
        'Donation program',
        'Where has your card been?',
        'Spinach Lasagna Roll Ups'
    ]
    
    print("🔍 FINAL SCORING DEBUG:")
    
    for img in test_images:
        filename = img['src'].split('/')[-1]
        print(f"\n📷 {filename}")
        
        best_match = None
        best_score = 0
        
        for heading in test_headings:
            # Test specific matching
            specific_match = extractor._is_image_specifically_for_section(img, heading, "")
            # Test general contextual matching  
            general_match = extractor._is_image_contextually_relevant(img, heading, "")
            
            score = 0
            if specific_match:
                score = 100
            elif general_match:
                score = 50
            
            print(f"   vs '{heading}': score={score}")
            
            if score > best_score:
                best_score = score
                best_match = heading
        
        print(f"   🎯 SHOULD GO TO: '{best_match}' (score: {best_score})")

if __name__ == "__main__":
    debug_final_scoring()