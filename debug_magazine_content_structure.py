#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_magazine_content_structure():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: MAGAZINE CONTENT STRUCTURE")
    print("=" * 80)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find the main content area
    content_area = soup.find('div', class_='col-xs-12 col-md-8')
    if not content_area:
        content_area = soup.find('main')
    
    if content_area:
        print("📄 Found main content area")
        
        # Look for specific magazine sections
        print("\n🔍 Looking for magazine sections...")
        
        # Find all divs with images and links
        image_containers = content_area.find_all('div', class_=True)
        
        print(f"Found {len(image_containers)} divs with classes")
        
        for i, container in enumerate(image_containers[:15]):  # First 15 containers
            classes = ' '.join(container.get('class', []))
            images = container.find_all('img')
            links = container.find_all('a', href=lambda href: href and '/connection-' in href)
            
            if images or links:
                print(f"\n📦 CONTAINER {i+1}: class='{classes}'")
                print(f"   Images: {len(images)}")
                print(f"   Article links: {len(links)}")
                
                for img in images:
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    print(f"      🖼️  {alt} - {src}")
                    
                for link in links:
                    href = link.get('href', '')
                    title = link.get_text().strip()
                    print(f"      🔗 {title} - {href}")
        
        # Look for specific pattern containers
        print("\n🔍 Looking for specific patterns...")
        
        # Find containers with both images and article links
        mixed_containers = []
        for container in content_area.find_all('div'):
            images = container.find_all('img')
            links = container.find_all('a', href=lambda href: href and '/connection-' in href)
            
            # Filter out images that are just logos/navigation
            content_images = [img for img in images if not any(skip in img.get('src', '').lower() for skip in ['logo', 'nav', 'costco-wholesale', 'connection-logo'])]
            
            if content_images and links:
                mixed_containers.append(container)
        
        print(f"Found {len(mixed_containers)} containers with both images and article links")
        
        for i, container in enumerate(mixed_containers[:5]):  # First 5 mixed containers
            print(f"\n📦 MIXED CONTAINER {i+1}:")
            images = container.find_all('img')
            links = container.find_all('a', href=lambda href: href and '/connection-' in href)
            
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt', '')
                if not any(skip in src.lower() for skip in ['logo', 'nav', 'costco-wholesale', 'connection-logo']):
                    print(f"      🖼️  {alt} - {src}")
                    
            for link in links:
                href = link.get('href', '')
                title = link.get_text().strip()
                print(f"      🔗 {title} - {href}")
    
    else:
        print("❌ Could not find main content area")

if __name__ == "__main__":
    debug_magazine_content_structure()