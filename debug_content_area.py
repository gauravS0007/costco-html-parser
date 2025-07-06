#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_content_area():
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: CONTENT AREA HEADINGS")
    print("=" * 60)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check what's in the content area we're using
    content_area = soup.find('div', class_='col-xs-12 col-md-8')
    
    if content_area:
        print("✅ Found content area div")
        
        # Find all headings in this content area
        headings_in_area = content_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"📄 Headings in content area: {len(headings_in_area)}")
        
        for i, heading in enumerate(headings_in_area):
            print(f"\n📄 Heading #{i+1} in content area:")
            print(f"   Tag: {heading.name}")
            print(f"   Text: '{heading.get_text().strip()}'")
            print(f"   HTML: {str(heading)[:100]}...")
    else:
        print("❌ Content area div not found")
        
        # Check all possible content areas
        all_divs = soup.find_all('div')
        print(f"Total divs found: {len(all_divs)}")
        
        for div in all_divs:
            classes = div.get('class', [])
            if any('col-' in str(cls) for cls in classes):
                headings = div.find_all(['h1', 'h2', 'h3'])
                if headings:
                    print(f"Div with classes {classes} has {len(headings)} headings")

if __name__ == "__main__":
    debug_content_area()