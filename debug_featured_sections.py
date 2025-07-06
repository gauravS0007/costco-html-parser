#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_featured_sections():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: FEATURED SECTIONS STRUCTURE")
    print("=" * 80)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for "FEATURED SECTIONS" text
    featured_text = soup.find(string=lambda text: text and 'FEATURED SECTIONS' in text)
    print(f"📄 'FEATURED SECTIONS' text found: {featured_text is not None}")
    
    if featured_text:
        print(f"📄 Text content: '{featured_text.strip()}'")
        
        # Look for all row divs after this
        all_rows = soup.find_all('div', class_='row')
        print(f"📄 Total rows found: {len(all_rows)}")
        
        # Look for rows with grid items and images, but limit to rows after the featured sections header
        featured_parent = featured_text.find_parent()
        if featured_parent:
            # Find all following sibling divs
            current = featured_parent
            rows_checked = 0
            
            while current and rows_checked < 10:  # Limit to next 10 elements
                current = current.find_next_sibling()
                if current and current.name == 'div':
                    rows_checked += 1
                    
                    grid_items = current.find_all('div', class_=lambda x: x and ('col-xs-' in ' '.join(x) or 'col-md-' in ' '.join(x)))
                    images_in_element = current.find_all('img')
                    
                    if len(grid_items) > 0 and len(images_in_element) > 0:
                        print(f"\n📄 SIBLING {rows_checked}: {len(grid_items)} grid items, {len(images_in_element)} images")
                        
                        for j, item in enumerate(grid_items[:4]):  # First 4 items
                            link = item.find('a', href=True)
                            img = item.find('img')
                            category_div = item.find('div', string=lambda text: text and any(cat in text for cat in ['For Your', 'Inside Costco', 'Member Connection']))
                            title_div = item.find('div', style=lambda style: style and 'color: #0f4878' in style)
                            
                            print(f"     ITEM {j+1}:")
                            print(f"       Has link: {link is not None}")
                            print(f"       Has image: {img is not None}")
                            print(f"       Has category: {category_div is not None}")
                            print(f"       Has title div: {title_div is not None}")
                            
                            if link:
                                href = link.get('href', '')
                                print(f"       Link href: {href}")
                                print(f"       Has connection: {'/connection-' in href}")
                            if img:
                                print(f"       Image alt: {img.get('alt', '')}")
                            if category_div:
                                print(f"       Category: {category_div.get_text().strip()}")
                            if title_div:
                                print(f"       Title: {title_div.get_text().strip()}")

if __name__ == "__main__":
    debug_featured_sections()