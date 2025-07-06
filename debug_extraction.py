#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'

with open(file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Create extractor and manually test its components
extractor = FixedUniversalContentExtractor()

# Test the cleaning process
soup = BeautifulSoup(html_content, 'html.parser')
print("1. Original soup has white-glove:", 'white-glove service' in soup.get_text())

cleaned_soup = extractor._clean_html(soup)
print("2. Cleaned soup has white-glove:", 'white-glove service' in cleaned_soup.get_text())

# Test main content finding  
main_content_area = extractor._find_main_content(cleaned_soup)
if main_content_area:
    print("3. Main content area has white-glove:", 'white-glove service' in main_content_area.get_text())
else:
    print("3. No main content area found")
    main_content_area = cleaned_soup

# Test paragraph extraction manually
print("\n4. Manual paragraph extraction:")
text_elements = main_content_area.find_all(['p', 'div', 'span', 'section', 'article'])

target_text = ""
for i, element in enumerate(text_elements):
    text = element.get_text().strip()
    
    if 'white-glove service' in text:
        print(f"   FOUND white-glove in element {i} ({element.name})")
        print(f"   Text: {text}")
        print(f"   Length: {len(text)}")
        target_text = text
        
        # Check all the filters (using new logic)
        if not text or len(text) < 10:
            print("   ❌ FILTERED: Too short")
        elif len(text) < 100 and any(nav_term in text.lower() for nav_term in ['home', 'costco connection', 'download the pdf', 'copyright', '©']):
            print("   ❌ FILTERED: Navigation content (short)")
        elif text.lower().startswith('by ') and len(text) < 50:
            print("   ❌ FILTERED: Byline content")
        elif len(text) <= 15:
            print("   ❌ FILTERED: Too short (15 chars)")
        else:
            print("   ✅ SHOULD BE INCLUDED")
        break

# Test full extraction
print("\n5. Full extraction test:")
extracted = extractor.extract_all_content(html_content, 'https://www.costco.com/buying-smart')
print(f"   Main content paragraphs: {len(extracted.main_content)}")
print(f"   Has white-glove in main_content: {any('white-glove service' in p for p in extracted.main_content)}")
print(f"   Has white-glove in full_text: {'white-glove service' in extracted.full_text}")

if target_text:
    print(f"\n6. Similarity check:")
    for i, existing in enumerate(extracted.main_content):
        similarity = extractor._text_similarity(target_text, existing)
        if similarity > 0.5:  # Show high similarities
            print(f"   Similarity with paragraph {i}: {similarity:.2f}")
            print(f"   Existing: {existing[:100]}...")
            if similarity > 0.7:
                print(f"   ❌ WOULD BE FILTERED (similarity > 0.7)")
            print()