#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'

with open(file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("🔍 DEBUGGING SECTION EXTRACTION")
print("=" * 40)

extractor = FixedUniversalContentExtractor()
soup = BeautifulSoup(html_content, 'html.parser')
main_content_area = extractor._find_main_content(soup)

if main_content_area:
    print("✅ Found main content area")
    
    # Test the new section extraction
    sections = extractor.extract_sections_between_headings(main_content_area)
    print(f"📋 Extracted {len(sections)} sections")
    
    # Look for the missing content
    for i, section in enumerate(sections):
        heading = section.get('heading', '')
        content = section.get('content', [])
        
        print(f"\n{i+1}. SECTION: {heading}")
        print(f"   Content items: {len(content)}")
        
        # Check for the missing "Through Costco's" content
        for j, para in enumerate(content):
            if "Through Costco's Countertop Installation program" in para:
                print(f"   ✅ FOUND 'Through Costco's' in item {j+1}")
                print(f"      Full text: {para}")
            if "white-glove service" in para:
                print(f"   ✅ FOUND 'white-glove service' in item {j+1}")
            if "When the job is completed" in para:
                print(f"   ✅ FOUND 'When the job is completed' in item {j+1}")
    
    # Check raw HTML for headings
    print(f"\n🏷️  ALL HEADINGS IN ORDER:")
    all_headings = main_content_area.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    for i, h in enumerate(all_headings):
        print(f"   {i+1}. H{h.name[1]}: {h.get_text().strip()}")
    
else:
    print("❌ No main content area found")