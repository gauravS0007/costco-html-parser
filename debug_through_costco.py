#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'

with open(file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("🔍 DEBUGGING 'Through Costco's' PARAGRAPH")
print("=" * 50)

# Search for the exact paragraph in HTML
target = "Through Costco's Countertop Installation program"
if target in html_content:
    print(f"✅ Found '{target}' in HTML")
    
    # Find which section it's in
    soup = BeautifulSoup(html_content, 'html.parser')
    all_paragraphs = soup.find_all('p')
    
    for i, p in enumerate(all_paragraphs):
        if target in p.get_text():
            print(f"📍 Found in paragraph {i+1}: {p.get_text()[:100]}...")
            
            # Find which heading this paragraph is closest to
            # Walk backwards to find the closest heading
            current = p
            while current:
                current = current.previous_sibling
                if hasattr(current, 'name') and current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    print(f"   📋 Closest heading: {current.name.upper()}: {current.get_text().strip()}")
                    break
                elif hasattr(current, 'name'):
                    continue
            
            # Also check next heading
            current = p
            while current:
                current = current.next_sibling
                if hasattr(current, 'name') and current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    print(f"   📋 Next heading: {current.name.upper()}: {current.get_text().strip()}")
                    break
                elif hasattr(current, 'name'):
                    continue
            break
else:
    print(f"❌ '{target}' NOT found in HTML")

# Test the extraction
extractor = FixedUniversalContentExtractor()
soup = BeautifulSoup(html_content, 'html.parser')
main_content_area = extractor._find_main_content(soup)

if main_content_area:
    sections = extractor.extract_sections_between_headings(main_content_area)
    
    print(f"\n📋 SECTION ANALYSIS:")
    for i, section in enumerate(sections):
        heading = section.get('heading', '')
        content = section.get('content', [])
        
        print(f"\n{i+1}. {heading}")
        for j, para in enumerate(content):
            if target in para:
                print(f"   ✅ FOUND 'Through Costco's' in this section!")
                print(f"      Full text: {para}")
            elif "white-glove" in para:
                print(f"   📝 Has 'white-glove': {para[:80]}...")
            else:
                print(f"   📄 Paragraph {j+1}: {para[:60]}...")