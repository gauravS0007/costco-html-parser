#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_assignment_scoring():
    """Debug the assignment scoring for each image"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Test specific images with actual headings from the file
    test_cases = [
        {
            'img': {'src': '10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'},
            'expected_section': 'Celebrate, your way'
        },
        {
            'img': {'src': '10_23_UF_CostcoLife_Glasses.jpg', 'alt': 'xxxxx'},
            'expected_section': 'Donation program'
        },
        {
            'img': {'src': '10_23_UF_CostcoLife_Card.jpg', 'alt': 'xxxxx'},
            'expected_section': 'Where has your card been?'
        },
        {
            'img': {'src': '10_23_UF_CostcoLife_Rollups.jpg', 'alt': 'Spinach Lasagna Roll Ups'},
            'expected_section': 'Spinach Lasagna Roll Ups'
        }
    ]
    
    headings = [
        {"text": "Celebrate, your way", "content": ["Halloween celebration content"]},
        {"text": "Fun times for all", "content": ["Festival content"]},
        {"text": "Donation program", "content": ["Glasses donation content"]},
        {"text": "Where has your card been?", "content": ["Travel card content"]},
        {"text": "Spinach Lasagna Roll Ups", "content": ["Recipe content"]}
    ]
    
    print(f"🎯 DEBUGGING ASSIGNMENT SCORING:")
    
    for case in test_cases:
        img = case['img']
        expected = case['expected_section']
        filename = img['src'].split('/')[-1]
        
        print(f"\n📷 Testing: {filename}")
        print(f"   Expected: {expected}")
        
        best_score = 0
        best_section = None
        
        for i, heading_info in enumerate(headings):
            heading_text = heading_info['text']
            section_text = ' '.join(heading_info['content'])
            
            score = 0
            match_type = ""
            
            # High priority: specific section matching
            if extractor._is_image_specifically_for_section(img, heading_text, section_text):
                score = 100
                match_type = "SPECIFIC"
            # Medium priority: general contextual relevance
            elif extractor._is_image_contextually_relevant(img, heading_text, section_text):
                score = 50
                match_type = "CONTEXTUAL"
            
            if score > 0:
                print(f"   '{heading_text}': {score} points ({match_type})")
                
                if score > best_score:
                    best_score = score
                    best_section = heading_text
        
        print(f"   → ASSIGNED TO: '{best_section}' ({best_score} points)")
        print(f"   → CORRECT: {'✅' if best_section == expected else '❌'}")

if __name__ == "__main__":
    debug_assignment_scoring()