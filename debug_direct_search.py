#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_direct_search():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for specific images from the HTML you provided
    specific_images = [
        '10_23_LP_FYH_Keeping_Cool.jpg',
        '10_23_LP_FYT_Yellowstone.jpg',
        '10_23_LP_FYT_PastaSauce.jpg',
        '10_23_LP_FYE_Author.jpg'
    ]
    
    print("🔍 SEARCHING FOR SPECIFIC FEATURED SECTION IMAGES")
    print("=" * 80)
    
    for img_name in specific_images:
        img = soup.find('img', src=lambda src: src and img_name in src)
        if img:
            print(f"\n📄 FOUND: {img_name}")
            print(f"   Alt: {img.get('alt', '')}")
            print(f"   Src: {img.get('src', '')}")
            
            # Find parent container
            parent = img.find_parent('div')
            if parent:
                print(f"   Parent classes: {parent.get('class', [])}")
                
                # Look for link in parent
                link = parent.find('a', href=True)
                if link:
                    print(f"   Link: {link.get('href', '')}")
                
                # Look for category text
                category_text = parent.find('div', string=lambda text: text and any(cat in text for cat in ['For Your', 'Inside Costco']))
                if category_text:
                    print(f"   Category: {category_text.get_text().strip()}")
                
                # Look for title text
                title_text = parent.find('div', style=lambda style: style and 'color: #0f4878' in style)
                if title_text:
                    print(f"   Title: {title_text.get_text().strip()}")
        else:
            print(f"\n❌ NOT FOUND: {img_name}")

if __name__ == "__main__":
    debug_direct_search()