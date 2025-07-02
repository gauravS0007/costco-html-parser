#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_actual_assignment():
    """Debug the actual assignment process step by step"""
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"🔍 Debugging actual assignment: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        extractor = FixedUniversalContentExtractor()
        
        # Run the actual extraction process 
        result = extractor.extract_all_content(html_content, html_file)
        
        print(f"\n📊 ACTUAL EXTRACTION RESULTS:")
        print(f"Headings found: {len(result.headings)}")
        
        for i, heading in enumerate(result.headings):
            heading_text = heading.get('text', 'Unknown')
            images = heading.get('images', [])
            print(f"\nHeading {i+1}: {heading_text}")
            print(f"  Images: {len(images)}")
            for j, img in enumerate(images):
                filename = img.get('src', '').split('/')[-1]
                print(f"    Image {j+1}: {filename}")
                print(f"      Alt: {img.get('alt', '')}")
    
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    debug_actual_assignment()