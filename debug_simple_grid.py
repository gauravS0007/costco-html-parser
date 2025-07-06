#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_simple_grid():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for all grid items - test different approaches
    approach1 = soup.find_all('div', class_=lambda x: x and any('col-xs-' in cls for cls in x))
    approach2 = soup.find_all('div', class_=lambda x: x and any('col-md-' in cls for cls in x))
    approach3 = soup.find_all('div', class_=['col-xs-6', 'col-md-3'])
    
    print(f"📄 Approach 1 (col-xs-): {len(approach1)}")
    print(f"📄 Approach 2 (col-md-): {len(approach2)}")  
    print(f"📄 Approach 3 (exact): {len(approach3)}")
    
    all_grid_items = approach1 + approach2
    print(f"📄 Total grid items: {len(all_grid_items)}")
    
    count = 0
    for item in all_grid_items:
        link = item.find('a', href=True)
        img = item.find('img')
        
        if link and img and '/connection-' in link.get('href', ''):
            count += 1
            if count <= 5:  # Show first 5
                category_div = item.find('div', string=lambda text: text and any(cat in text for cat in ['For Your', 'Inside Costco', 'Member Connection']))
                title_div = item.find('div', style=lambda style: style and 'color: #0f4878' in style)
                
                print(f"\n📄 ITEM {count}:")
                print(f"   Link: {link.get('href', '')}")
                print(f"   Image alt: {img.get('alt', '')}")
                print(f"   Has category div: {category_div is not None}")
                print(f"   Has title div: {title_div is not None}")
                
                if category_div:
                    print(f"   Category: {category_div.get_text().strip()}")
                if title_div:
                    print(f"   Title: {title_div.get_text().strip()}")
    
    print(f"\n📊 Total matching items: {count}")

if __name__ == "__main__":
    debug_simple_grid()