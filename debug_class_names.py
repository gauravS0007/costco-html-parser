#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_class_names():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for divs with col- classes more broadly
    all_divs_with_col = soup.find_all('div', class_=lambda x: x and any('col-' in cls for cls in x))
    print(f"📄 Divs with col- classes: {len(all_divs_with_col)}")
    
    # Show first few examples
    for i, div in enumerate(all_divs_with_col[:10]):
        classes = div.get('class', [])
        link = div.find('a', href=True)
        img = div.find('img')
        
        print(f"\n📄 DIV {i+1}:")
        print(f"   Classes: {classes}")
        print(f"   Has link: {link is not None}")
        print(f"   Has image: {img is not None}")
        
        if link and '/connection-' in link.get('href', ''):
            print(f"   ✅ Has connection link: {link.get('href', '')}")
        if img:
            print(f"   ✅ Image alt: {img.get('alt', '')}")

if __name__ == "__main__":
    debug_class_names()