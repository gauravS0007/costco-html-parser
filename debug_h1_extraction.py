#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_h1_extraction():
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: H1 EXTRACTION")
    print("=" * 60)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all H1 tags
    h1_tags = soup.find_all('h1')
    print(f"Found {len(h1_tags)} H1 tags:")
    
    for i, h1 in enumerate(h1_tags):
        print(f"\n📄 H1 #{i+1}:")
        print(f"   Text: '{h1.get_text().strip()}'")
        print(f"   HTML: {str(h1)[:100]}...")
        
        # Check what comes after this H1
        next_element = h1.next_sibling
        content_count = 0
        
        print(f"   Content after H1:")
        while next_element and content_count < 5:
            if hasattr(next_element, 'name'):
                if next_element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    print(f"     NEXT HEADING: {next_element.name} - {next_element.get_text().strip()}")
                    break
                elif next_element.name == 'p':
                    text = next_element.get_text().strip()
                    if text and len(text) > 10:
                        print(f"     P: {text[:60]}...")
                        content_count += 1
                elif next_element.name == 'img':
                    print(f"     IMG: {next_element.get('alt', 'No alt')}")
                    content_count += 1
                else:
                    if next_element.get_text().strip():
                        print(f"     {next_element.name}: {next_element.get_text().strip()[:40]}...")
            
            next_element = next_element.next_sibling
    
    # Find all H2 tags  
    h2_tags = soup.find_all('h2')
    print(f"\n\nFound {len(h2_tags)} H2 tags:")
    
    for i, h2 in enumerate(h2_tags):
        print(f"\n📄 H2 #{i+1}:")
        print(f"   Text: '{h2.get_text().strip()}'")

if __name__ == "__main__":
    debug_h1_extraction()