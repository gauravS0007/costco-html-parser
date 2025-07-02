#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_section_content():
    """Debug the actual section content being extracted"""
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"🔍 Debugging section content: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        extractor = FixedUniversalContentExtractor()
        
        # Run the actual extraction process 
        result = extractor.extract_all_content(html_content, html_file)
        
        print(f"\n📊 ACTUAL SECTION CONTENT:")
        
        for i, heading in enumerate(result.headings):
            heading_text = heading.get('text', 'Unknown')
            content = heading.get('content', [])
            images = heading.get('images', [])
            
            print(f"\nHeading {i+1}: {heading_text}")
            print(f"  Content items: {len(content)}")
            for j, text in enumerate(content[:2]):  # Show first 2 content items
                print(f"    Content {j+1}: {text[:100]}...")
            
            print(f"  Images: {len(images)}")
            for j, img in enumerate(images):
                filename = img.get('src', '').split('/')[-1]
                alt = img.get('alt', '')
                print(f"    Image {j+1}: {filename} (alt: {alt})")
                
                # Test assignment manually for this image
                section_text = ' '.join(content) if content else ''
                specific_match = extractor._is_image_specifically_for_section(img, heading_text, section_text)
                contextual_match = extractor._is_image_contextually_relevant(img, heading_text, section_text)
                
                if specific_match:
                    print(f"      → SPECIFIC match (100 points)")
                elif contextual_match:
                    print(f"      → CONTEXTUAL match (50 points)")
                else:
                    print(f"      → NO match (0 points)")
    
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    debug_section_content()