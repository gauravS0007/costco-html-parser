#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup

def debug_missing_content():
    """Debug what content should be in the missing sections"""
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"🔍 Debugging missing content: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        main_content = soup.find('main') or soup.find('article') or soup
        
        # Find all headings
        all_headings = main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        print(f"\n📊 EXPECTED CONTENT FOR EACH SECTION:")
        
        target_headings = ["Donation program", "Spinach Lasagna Roll Ups"]
        
        for heading in all_headings:
            heading_text = heading.get_text().strip()
            if any(target in heading_text for target in target_headings):
                print(f"\n🎯 Found: {heading_text}")
                print(f"   Heading tag: {heading.name}")
                
                # Look for content after this heading manually
                current = heading.next_sibling
                content_found = []
                
                for i in range(10):  # Look at next 10 siblings
                    if current:
                        if hasattr(current, 'name'):
                            if current.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                                print(f"   → Stopped at next heading: {current.get_text().strip()}")
                                break
                            elif current.name == 'p':
                                text = current.get_text().strip()
                                if text and len(text) > 10:
                                    content_found.append(text[:100] + "...")
                                    print(f"   Content {len(content_found)}: {text[:100]}...")
                        current = current.next_sibling
                    else:
                        print(f"   → Reached end of siblings")
                        break
                
                if not content_found:
                    print(f"   ⚠️  NO CONTENT FOUND for {heading_text}")
    
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    debug_missing_content()