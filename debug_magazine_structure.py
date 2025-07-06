#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_magazine_structure():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: MAGAZINE STRUCTURE FOR IN THIS ISSUE")
    print("=" * 80)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main content area - but search the whole document for magazine sections
    content_area = soup  # Search the whole document instead of just main content
    
    print(f"📄 Content area found: {content_area is not None}")
    
    # Look for "In This Issue" text
    in_this_issue_text = content_area.find(string=lambda text: text and 'in this issue' in text.lower()) if content_area else None
    print(f"📄 'In This Issue' text found: {in_this_issue_text is not None}")
    
    if in_this_issue_text:
        print(f"📄 Text content: '{in_this_issue_text.strip()}'")
        parent = in_this_issue_text.find_parent(['div', 'section'])
        print(f"📄 Parent found: {parent is not None}")
        
        if parent:
            print(f"📄 Parent tag: {parent.name}")
            print(f"📄 Parent classes: {parent.get('class', [])}")
            
            # Look for ul
            ul = parent.find('ul')
            print(f"📄 UL found: {ul is not None}")
            
            if ul:
                lis = ul.find_all('li')
                print(f"📄 LI items found: {len(lis)}")
                
                for i, li in enumerate(lis[:3]):
                    link = li.find('a', href=True)
                    print(f"📄 LI {i+1}: {li.get_text()[:50]}...")
                    if link:
                        print(f"     Link: {link.get('href')}")
    
    print("\n" + "=" * 80)
    print("🔍 DEBUG: FEATURED SECTIONS STRUCTURE")
    
    # Look for "Featured Sections" text
    featured_text = content_area.find(string=lambda text: text and 'featured section' in text.lower()) if content_area else None
    print(f"📄 'Featured Sections' text found: {featured_text is not None}")
    
    if featured_text:
        print(f"📄 Text content: '{featured_text.strip()}'")
        parent = featured_text.find_parent(['div', 'section'])
        print(f"📄 Parent found: {parent is not None}")
        
        if parent:
            print(f"📄 Parent tag: {parent.name}")
            
            # Look for next siblings
            next_sibling = parent.find_next_sibling()
            print(f"📄 Next sibling found: {next_sibling is not None}")
            
            if next_sibling:
                print(f"📄 Next sibling tag: {next_sibling.name}")
                print(f"📄 Next sibling classes: {next_sibling.get('class', [])}")
                
                # Look for grid items
                grid_items = next_sibling.find_all('div', class_=lambda x: x and ('col-xs-' in ' '.join(x) or 'col-md-' in ' '.join(x)))
                print(f"📄 Grid items found: {len(grid_items)}")
                
                for i, item in enumerate(grid_items[:3]):
                    img = item.find('img')
                    link = item.find('a', href=True)
                    print(f"📄 Grid item {i+1}: has image={img is not None}, has link={link is not None}")
                    if img:
                        print(f"     Image alt: {img.get('alt', 'No alt')}")
                    if link:
                        print(f"     Link: {link.get('href')}")

if __name__ == "__main__":
    debug_magazine_structure()