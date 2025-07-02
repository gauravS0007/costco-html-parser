#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bs4 import BeautifulSoup

def debug_html_structure():
    """Debug the HTML structure to understand content boundaries"""
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"\n🔍 Debugging HTML structure: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        main_content = soup.find('main') or soup.find('article') or soup
        
        # Find all headings
        all_headings = main_content.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        
        print(f"\n📊 HEADINGS STRUCTURE:")
        for i, heading in enumerate(all_headings[:6]):  # First 6 headings
            heading_text = heading.get_text().strip()
            print(f"\n{i+1}. {heading.name}: '{heading_text}'")
            
            # Check immediate siblings
            print(f"   Next 3 siblings:")
            current = heading.next_sibling
            for j in range(3):
                if current:
                    if hasattr(current, 'name'):
                        if current.name:
                            text = current.get_text().strip()[:100] if hasattr(current, 'get_text') else ''
                            print(f"     {j+1}. <{current.name}>: {text}...")
                        else:
                            print(f"     {j+1}. [TEXT]: {str(current).strip()[:50]}...")
                    else:
                        print(f"     {j+1}. [STRING]: {str(current).strip()[:50]}...")
                    current = current.next_sibling
                else:
                    print(f"     {j+1}. [END]")
                    break
            
            # Check parent structure
            parent = heading.parent
            print(f"   Parent: <{parent.name if parent and hasattr(parent, 'name') else 'None'}>")
            
            # Check if content is nested in containers
            container = heading.find_next(['div', 'section', 'article'])
            if container:
                container_text = container.get_text().strip()[:100]
                print(f"   Next container: <{container.name}>: {container_text}...")
    
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    debug_html_structure()