#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_scoring():
    """Debug the image assignment scoring logic"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Test data based on what we found
    test_images = [
        {'src': '10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'},
        {'src': '10_23_UF_CostcoLife_Glasses.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Card.jpg', 'alt': 'xxxxx'},
        {'src': '10_23_UF_CostcoLife_Rollups.jpg', 'alt': 'Spinach Lasagna Roll Ups'}
    ]
    
    headings_data = [
        {'text': 'Celebrate, your way', 'content': ['Fun times for all']},
        {'text': 'Fun times for all', 'content': ['Sample content about fun times']}, 
        {'text': 'Donation program', 'content': ['Sample content about donation program']},
        {'text': 'Where has your card been?', 'content': ['Sample content about card']},
        {'text': 'Spinach Lasagna Roll Ups', 'content': ['Sample content about recipe']}
    ]
    
    print("🔍 TESTING IMAGE ASSIGNMENT SCORING:")
    
    for img in test_images:
        filename = img['src'].split('/')[-1]
        print(f"\n📷 Image: {filename}")
        print(f"   Alt: {img['alt']}")
        
        best_match_index = -1
        best_match_score = 0
        
        # Test scoring against each heading
        for i, heading_info in enumerate(headings_data):
            heading_text = heading_info['text']
            section_text = ' '.join(heading_info['content'])
            
            score = 0
            match_type = "none"
            
            # Test specific matching
            if extractor._is_image_specifically_for_section(img, heading_text, section_text):
                score = 100
                match_type = "specific"
            # Test general contextual relevance
            elif extractor._is_image_contextually_relevant(img, heading_text, section_text):
                score = 50
                match_type = "general"
            
            print(f"   vs '{heading_text}': score={score} ({match_type})")
            
            if score > best_match_score:
                best_match_score = score
                best_match_index = i
        
        if best_match_index >= 0:
            best_heading = headings_data[best_match_index]['text']
            print(f"   🎯 BEST MATCH: '{best_heading}' (score: {best_match_score})")
        else:
            print(f"   ❌ NO MATCH FOUND")

if __name__ == "__main__":
    debug_scoring()