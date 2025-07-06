#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_all_headings():
    extractor = FixedUniversalContentExtractor()
    
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: ALL HEADINGS IN SHOPPING EXTRACTION")
    print("=" * 60)
    
    # Extract content
    extracted = extractor.extract_all_content(html_content, 'https://www.costco.com/buying-smart')
    
    print(f"Content type: {extracted.content_type}")
    print(f"Title: {extracted.title}")
    print(f"Headings found: {len(extracted.headings)}")
    
    for i, heading in enumerate(extracted.headings):
        print(f"\n📄 Heading #{i+1}:")
        print(f"   Level: {heading.get('level', 'Unknown')}")
        print(f"   Text: '{heading.get('text', '')}'")
    
    # Test section extraction directly
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    content_area = soup.find('div', class_='col-xs-12 col-md-8')
    
    if content_area:
        sections = extractor.extract_sections_between_headings(content_area, "shopping")
        print(f"\n🔧 SECTION EXTRACTION RESULTS:")
        print(f"Sections found: {len(sections)}")
        
        for i, section in enumerate(sections):
            print(f"\n📄 Section #{i+1}:")
            print(f"   Heading: '{section.get('heading', '')}'")
            print(f"   Level: H{section.get('level', 'Unknown')}")
            print(f"   Content items: {len(section.get('content', []))}")
            print(f"   Images: {len(section.get('images', []))}")
    else:
        print("❌ Content area not found")

if __name__ == "__main__":
    debug_all_headings()