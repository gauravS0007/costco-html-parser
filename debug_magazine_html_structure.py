#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_magazine_html_structure():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: MAGAZINE HTML STRUCTURE")
    print("=" * 80)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find areas with magazine images
    magazine_images = soup.find_all('img', src=lambda src: src and ('10_23_LP' in src or 'connection-' in src))
    
    print(f"📄 Found {len(magazine_images)} magazine-specific images")
    
    for i, img in enumerate(magazine_images[:10]):  # First 10 magazine images
        src = img.get('src', '')
        alt = img.get('alt', '')
        print(f"\n🖼️  IMAGE {i+1}: {alt}")
        print(f"   Src: {src}")
        
        # Find the parent containers and nearby links
        parent = img.find_parent(['div', 'section', 'article'])
        if parent:
            print(f"   Parent: {parent.name}")
            
            # Look for article links near this image
            nearby_links = parent.find_all('a', href=lambda href: href and '/connection-' in href)
            print(f"   Nearby article links: {len(nearby_links)}")
            
            for link in nearby_links:
                href = link.get('href', '')
                title = link.get_text().strip()
                print(f"      🔗 {title} - {href}")
    
    # Also look for specific magazine content patterns
    print("\n" + "=" * 80)
    print("🔍 Looking for magazine content patterns...")
    
    # Find content with "october", "connection", etc.
    content_elements = soup.find_all(string=lambda text: text and any(keyword in text.lower() for keyword in ['october', 'costco connection', 'in this issue', 'special section']))
    
    print(f"Found {len(content_elements)} content elements with magazine keywords")
    
    for i, element in enumerate(content_elements[:5]):  # First 5 elements
        text = element.strip()
        if text and len(text) > 5:
            print(f"\n📝 CONTENT {i+1}: {text[:50]}...")
            
            parent = element.find_parent(['div', 'section', 'article'])
            if parent:
                # Look for images and links in this parent
                images = parent.find_all('img')
                links = parent.find_all('a', href=lambda href: href and '/connection-' in href)
                
                print(f"   Parent images: {len(images)}")
                print(f"   Parent links: {len(links)}")
                
                for img in images:
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    print(f"      🖼️  {alt} - {src}")
                    
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text().strip()
                    print(f"      🔗 {title} - {href}")

if __name__ == "__main__":
    debug_magazine_html_structure()