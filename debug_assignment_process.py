#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

def debug_assignment_process():
    """Debug the step-by-step assignment process"""
    
    extractor = FixedUniversalContentExtractor()
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"\n🔍 Debugging assignment process: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        main_content_area = soup.find('main') or soup.find('article') or soup
        
        # Manually call the extraction method to debug
        from src.utils.universal_content_extractor import ExtractedContent
        extracted = ExtractedContent()
        extracted.content_type = "lifestyle"
        
        # Call the method that should do the enhanced assignment
        extractor._extract_lifestyle_structured_content_with_images(main_content_area, extracted)
        
        print(f"\n📊 ASSIGNMENT RESULTS:")
        
        for i, heading in enumerate(extracted.headings):
            heading_text = heading.get('text', 'No text')
            images = heading.get('images', [])
            
            print(f"\nHeading {i+1}: '{heading_text}'")
            print(f"  Images: {len(images)}")
            
            for j, img in enumerate(images):
                filename = img.get('src', '').split('/')[-1] if img.get('src') else 'unknown'
                alt = img.get('alt', '')
                print(f"    {j+1}. {filename}")
                print(f"       Alt: {alt}")
    
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    debug_assignment_process()