#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_h1_html():
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: H1 HTML STRUCTURE")
    print("=" * 60)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find ALL H1 tags in the entire document
    all_h1s = soup.find_all('h1')
    print(f"📄 Total H1 tags in document: {len(all_h1s)}")
    
    for i, h1 in enumerate(all_h1s):
        print(f"\n📄 H1 #{i+1}:")
        print(f"   Text: '{h1.get_text().strip()}'")
        print(f"   Classes: {h1.get('class', [])}")
        print(f"   Style: {h1.get('style', 'None')}")
        
        # Check parent containers
        parent = h1.parent
        parent_chain = []
        while parent and len(parent_chain) < 5:
            if hasattr(parent, 'name') and parent.name:
                classes = parent.get('class', [])
                parent_info = f"{parent.name}"
                if classes:
                    parent_info += f".{'.'.join(classes)}"
                parent_chain.append(parent_info)
            parent = parent.parent
        
        print(f"   Parent chain: {' > '.join(reversed(parent_chain))}")
    
    # Check content area specifically
    content_area = soup.find('div', class_='col-xs-12 col-md-8')
    print(f"\n🔍 CONTENT AREA ANALYSIS:")
    
    if content_area:
        print("✅ Found content area div")
        h1s_in_content = content_area.find_all('h1')
        print(f"📄 H1 tags in content area: {len(h1s_in_content)}")
        
        for i, h1 in enumerate(h1s_in_content):
            print(f"   H1 #{i+1} in content: '{h1.get_text().strip()}'")
            
        # Check what comes immediately after each H1 in content area
        for i, h1 in enumerate(h1s_in_content):
            print(f"\n🔍 Content after H1 '{h1.get_text().strip()}':")
            next_elem = h1.next_sibling
            count = 0
            while next_elem and count < 10:
                if hasattr(next_elem, 'name') and next_elem.name:
                    if next_elem.name in ['h1', 'h2', 'h3']:
                        print(f"     NEXT HEADING: {next_elem.name.upper()} - '{next_elem.get_text().strip()}'")
                        break
                    elif next_elem.name == 'p':
                        text = next_elem.get_text().strip()
                        if text:
                            print(f"     P: {text[:60]}...")
                            count += 1
                    elif next_elem.name == 'img':
                        print(f"     IMG: {next_elem.get('alt', 'No alt')} - {next_elem.get('src', '')[:50]}...")
                        count += 1
                elif hasattr(next_elem, 'strip') and next_elem.strip():
                    print(f"     TEXT: {next_elem.strip()[:50]}...")
                    count += 1
                next_elem = next_elem.next_sibling
    else:
        print("❌ Content area div not found")
        
        # Find all divs with col classes
        col_divs = soup.find_all('div', class_=lambda x: x and any('col-' in cls for cls in x))
        print(f"Found {len(col_divs)} divs with col- classes")
        
        for div in col_divs[:5]:  # Show first 5
            classes = div.get('class', [])
            h1s = div.find_all('h1')
            if h1s:
                print(f"   Div with classes {classes} has {len(h1s)} H1s:")
                for h1 in h1s:
                    print(f"     - '{h1.get_text().strip()}'")

if __name__ == "__main__":
    debug_h1_html()