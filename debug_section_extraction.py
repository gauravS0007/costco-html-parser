#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_section_extraction():
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: SECTION EXTRACTION STEP BY STEP")
    print("=" * 60)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    content_area = soup.find('div', class_='col-xs-12 col-md-8')
    
    if not content_area:
        print("❌ Content area not found")
        return
        
    # Find all headings in document order
    all_headings = content_area.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    print(f"Found {len(all_headings)} headings in content area")
    
    sections = []
    html_content_str = str(content_area)
    
    # For each heading, extract content based on comment boundaries
    for i, heading in enumerate(all_headings):
        heading_text = heading.get_text().strip()
        print(f"\n📄 Processing heading #{i+1}: '{heading_text}'")
        
        if not heading_text or len(heading_text) < 2:
            print(f"   ❌ Skipped: Text too short")
            continue
        
        # Filter out cookies/navigation headings
        if any(nav_term in heading_text.lower() for nav_term in ['cookie', 'privacy', 'advertising and products']):
            print(f"   ❌ Skipped: Navigation heading")
            continue
            
        level = int(heading.name[1])
        section_content = []
        section_images = []
        
        # Find the HTML position of this heading
        heading_html = str(heading)
        heading_start = html_content_str.find(heading_html)
        
        print(f"   📍 Level: H{level}")
        print(f"   📍 HTML position: {heading_start}")
        
        if heading_start == -1:
            print(f"   ❌ Skipped: Heading HTML not found")
            continue
            
        # Find the next heading to determine section boundaries
        next_heading = all_headings[i + 1] if i + 1 < len(all_headings) else None
        section_end = len(html_content_str)
        
        if next_heading:
            next_heading_html = str(next_heading)
            next_start = html_content_str.find(next_heading_html, heading_start + len(heading_html))
            if next_start != -1:
                section_end = next_start
                print(f"   📍 Section ends at: {section_end} (next heading: '{next_heading.get_text().strip()}')")
        else:
            print(f"   📍 Section ends at: {section_end} (end of content)")
        
        # Extract content in this section only
        section_html = html_content_str[heading_start:section_end]
        print(f"   📍 Section HTML length: {len(section_html)}")
        
        # Parse this section to find paragraphs and images
        section_soup = BeautifulSoup(section_html, 'html.parser')
        
        # Find paragraphs in this section
        paragraphs = section_soup.find_all('p')
        images = section_soup.find_all('img')
        
        print(f"   📝 Found {len(paragraphs)} paragraphs")
        print(f"   🖼️  Found {len(images)} images")
        
        # Process paragraphs
        for j, p in enumerate(paragraphs):
            text = p.get_text().strip()
            if text and len(text) > 3:
                section_content.append(text)
                print(f"     P{j+1}: {text[:50]}...")
        
        # Process images
        for j, img in enumerate(images):
            src = img.get('src', '')
            alt = img.get('alt', '')
            if src:
                print(f"     I{j+1}: {alt} - {src[:50]}...")
                section_images.append({
                    'src': src,
                    'alt': alt,
                    'caption': '',
                    'relevance_score': 6
                })
        
        # Create section if we have content
        if section_content or section_images:
            sections.append({
                "heading": heading_text,
                "level": level,
                "content": section_content,
                "images": section_images
            })
            print(f"   ✅ Created section with {len(section_content)} content items and {len(section_images)} images")
        else:
            print(f"   ❌ No content found - section not created")
    
    print(f"\n🎯 FINAL RESULT: {len(sections)} sections created")

if __name__ == "__main__":
    debug_section_extraction()