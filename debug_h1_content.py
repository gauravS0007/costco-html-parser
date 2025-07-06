#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_h1_content():
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: H1 CONTENT BETWEEN HEADINGS")
    print("=" * 60)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Get correct content area
    content_area = soup.find('div', class_='col-xs-12 col-md-8')
    
    if content_area:
        # Find H1 and H2
        h1 = content_area.find('h1')
        h2 = content_area.find('h2')
        
        if h1 and h2:
            print(f"📄 H1: '{h1.get_text().strip()}'")
            print(f"📄 H2: '{h2.get_text().strip()}'")
            
            # Get HTML between H1 and H2
            h1_html = str(h1)
            h2_html = str(h2)
            content_html = str(content_area)
            
            h1_pos = content_html.find(h1_html)
            h2_pos = content_html.find(h2_html)
            
            if h1_pos != -1 and h2_pos != -1:
                between_html = content_html[h1_pos + len(h1_html):h2_pos]
                print(f"\n🔍 HTML between H1 and H2 ({len(between_html)} chars):")
                print(between_html[:500] + ("..." if len(between_html) > 500 else ""))
                
                # Parse what's between
                between_soup = BeautifulSoup(between_html, 'html.parser')
                paragraphs = between_soup.find_all('p')
                images = between_soup.find_all('img')
                
                print(f"\n📝 Paragraphs between H1 and H2: {len(paragraphs)}")
                for i, p in enumerate(paragraphs):
                    text = p.get_text().strip()
                    if text:
                        print(f"   P{i+1}: {text[:60]}...")
                
                print(f"\n🖼️  Images between H1 and H2: {len(images)}")
                for i, img in enumerate(images):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    print(f"   I{i+1}: {alt} - {src[:50]}...")
                    
            else:
                print("❌ Could not find H1 or H2 positions in HTML")
        else:
            print("❌ Could not find H1 or H2 in content area")
    else:
        print("❌ Content area not found")

if __name__ == "__main__":
    debug_h1_content()