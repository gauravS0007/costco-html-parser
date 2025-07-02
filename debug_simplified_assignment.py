#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_simplified_assignment():
    """Simplified debug of the assignment logic"""
    
    extractor = FixedUniversalContentExtractor()
    
    # Simulate the data structures
    test_images = [
        {'src': 'https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/10_23_UF_CostcoLife_HalloweenOpener.jpg', 'alt': 'kids in halloween costumes'},
        {'src': 'https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/10_23_UF_CostcoLife_Glasses.jpg', 'alt': 'xxxxx'},
        {'src': 'https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/10_23_UF_CostcoLife_Card.jpg', 'alt': 'xxxxx'},
        {'src': 'https://mobilecontent.costco.com/live/resource/img/static-us-connection-october-23/10_23_UF_CostcoLife_Rollups.jpg', 'alt': 'Spinach Lasagna Roll Ups'}
    ]
    
    headings_data = [
        {'text': 'Celebrate, your way', 'content': ['Halloween content'], 'images': []},
        {'text': 'Fun times for all', 'content': ['Fun content'], 'images': []}, 
        {'text': 'Donation program', 'content': ['Donation content'], 'images': []},
        {'text': 'Where has your card been?', 'content': ['Card content'], 'images': []},
        {'text': 'Spinach Lasagna Roll Ups', 'content': ['Recipe content'], 'images': []}
    ]
    
    print("🔍 SIMPLIFIED ASSIGNMENT DEBUG:")
    
    assigned_images = set()
    
    for img_data in test_images:
        img_src = img_data.get('src', '')
        img_filename = img_src.split('/')[-1] if img_src else 'unknown'
        
        print(f"\n📷 Processing: {img_filename}")
        
        if img_src in assigned_images:
            print(f"   ⏭️  Already assigned, skipping")
            continue
        
        # Apply filter
        if not any(pattern in img_filename.lower() for pattern in ['costcolife', 'rollup', 'glasses', 'card', 'halloween']):
            print(f"   🚫 Filtered out (not main content)")
            continue
        
        best_match_index = -1
        best_match_score = 0
        
        # Test each heading
        for i, heading_info in enumerate(headings_data):
            heading_text = heading_info['text']
            section_text = ' '.join(heading_info['content'])
            
            score = 0
            
            # Test specific matching
            if extractor._is_image_specifically_for_section(img_data, heading_text, section_text):
                score = 100
                match_type = "specific"
            # Test general matching
            elif extractor._is_image_contextually_relevant(img_data, heading_text, section_text):
                score = 50
                match_type = "general"
            else:
                match_type = "none"
            
            print(f"   vs '{heading_text}': score={score} ({match_type})")
            
            if score > best_match_score:
                best_match_score = score
                best_match_index = i
        
        # Assign
        if best_match_index >= 0 and best_match_score > 0:
            headings_data[best_match_index]['images'].append(img_data)
            assigned_images.add(img_src)
            print(f"   ✅ ASSIGNED to: '{headings_data[best_match_index]['text']}' (score: {best_match_score})")
        else:
            print(f"   ❌ NO ASSIGNMENT (best score: {best_match_score})")
    
    # Show final results
    print(f"\n📊 FINAL ASSIGNMENT RESULTS:")
    for i, heading_info in enumerate(headings_data):
        heading_text = heading_info['text']
        images = heading_info['images']
        print(f"{i+1}. '{heading_text}': {len(images)} images")
        for img in images:
            filename = img.get('src', '').split('/')[-1]
            print(f"   - {filename}")

if __name__ == "__main__":
    debug_simplified_assignment()