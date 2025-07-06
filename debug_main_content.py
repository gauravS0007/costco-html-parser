#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

def debug_main_content():
    extractor = FixedUniversalContentExtractor()
    
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: MAIN CONTENT DETECTION")
    print("=" * 60)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Test what _find_main_content returns
    main_content_area = extractor._find_main_content(soup)
    
    if main_content_area:
        print("✅ Found main content area")
        
        # Check classes of main content area
        classes = main_content_area.get('class', [])
        print(f"📄 Main content area classes: {classes}")
        print(f"📄 Main content area tag: {main_content_area.name}")
        
        # Find H1s in this area
        h1s_in_main = main_content_area.find_all('h1')
        print(f"📄 H1 tags in main content area: {len(h1s_in_main)}")
        
        for i, h1 in enumerate(h1s_in_main):
            print(f"   H1 #{i+1}: '{h1.get_text().strip()}'")
            
        print(f"\n🔍 Main content area HTML (first 500 chars):")
        print(str(main_content_area)[:500] + "...")
        
    else:
        print("❌ Main content area not found")
    
    # Compare with correct content area
    print(f"\n🔍 CORRECT CONTENT AREA (col-xs-12 col-md-8):")
    correct_area = soup.find('div', class_='col-xs-12 col-md-8')
    
    if correct_area:
        print("✅ Found correct content area")
        h1s_in_correct = correct_area.find_all('h1')
        print(f"📄 H1 tags in correct area: {len(h1s_in_correct)}")
        
        for i, h1 in enumerate(h1s_in_correct):
            print(f"   H1 #{i+1}: '{h1.get_text().strip()}'")
            
        # Check if they're the same
        if main_content_area == correct_area:
            print("✅ Main content detection is correct")
        else:
            print("❌ Main content detection is wrong - using wrong area")
    else:
        print("❌ Correct content area not found")

if __name__ == "__main__":
    debug_main_content()