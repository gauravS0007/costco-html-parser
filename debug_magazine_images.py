#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_magazine_images():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: MAGAZINE IMAGES AND ARTICLE STRUCTURE")
    print("=" * 80)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all article links
    article_links = soup.find_all('a', href=lambda href: href and '/connection-' in href)
    
    print(f"📄 Found {len(article_links)} article links")
    
    # Check first few article links for associated images
    for i, link in enumerate(article_links[:10]):  # First 10 links
        href = link.get('href', '')
        title = link.get_text().strip()
        
        print(f"\n🔗 ARTICLE {i+1}: {title}")
        print(f"   Link: {href}")
        
        # Check parent containers for images
        parent = link.find_parent(['div', 'li', 'section'])
        if parent:
            print(f"   Parent tag: {parent.name}")
            
            # Look for images in parent
            images = parent.find_all('img')
            print(f"   Images in parent: {len(images)}")
            
            for j, img in enumerate(images):
                src = img.get('src', '')
                alt = img.get('alt', '')
                print(f"      IMG{j+1}: {alt} - {src}")
                
        # Check siblings for images
        siblings = link.find_next_siblings(['img', 'div'])
        for sibling in siblings[:2]:  # Check first 2 siblings
            if sibling.name == 'img':
                print(f"   Sibling image: {sibling.get('alt', '')} - {sibling.get('src', '')}")
            elif sibling.name == 'div':
                div_images = sibling.find_all('img')
                for img in div_images:
                    print(f"   Div sibling image: {img.get('alt', '')} - {img.get('src', '')}")
                    
    print("\n" + "=" * 80)
    print("🖼️  ALL IMAGES IN DOCUMENT:")
    all_images = soup.find_all('img')
    print(f"Total images: {len(all_images)}")
    
    for i, img in enumerate(all_images[:15]):  # Show first 15 images
        src = img.get('src', '')
        alt = img.get('alt', '')
        print(f"   {i+1}. {alt} - {src}")

if __name__ == "__main__":
    debug_magazine_images()