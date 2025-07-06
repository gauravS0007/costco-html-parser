#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from bs4 import BeautifulSoup

def debug_in_this_issue():
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print("🔍 DEBUG: IN THIS ISSUE SPECIFIC STRUCTURE")
    print("=" * 80)
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Look for the sidebar
    sidebar = soup.find('div', class_='col-xs-12 col-md-4')
    print(f"📄 Sidebar found: {sidebar is not None}")
    
    if sidebar:
        # Look for the blue border container
        blue_container = sidebar.find('div', style=lambda style: style and 'border-top: 8px solid #54b6cc' in style)
        print(f"📄 Blue container found: {blue_container is not None}")
        
        if blue_container:
            # Look for "IN THIS ISSUE" text
            issue_text = blue_container.find(string=lambda text: text and 'IN THIS ISSUE' in text)
            print(f"📄 'IN THIS ISSUE' text found: {issue_text is not None}")
            
            # Look for the ul
            ul = blue_container.find('ul')
            print(f"📄 UL found: {ul is not None}")
            
            if ul:
                lis = ul.find_all('li')
                print(f"📄 LI items found: {len(lis)}")
                
                for i, li in enumerate(lis[:8]):  # Show first 8
                    link = li.find('a', href=True)
                    if link:
                        href = link.get('href', '')
                        text = link.get_text().strip()
                        lines = [line.strip() for line in text.split('\n') if line.strip()]
                        
                        print(f"📄 LI {i+1}:")
                        print(f"     Href: {href}")
                        print(f"     Text lines: {len(lines)}")
                        if len(lines) >= 1:
                            print(f"     Title: {lines[0]}")
                        if len(lines) >= 2:
                            print(f"     Desc: {lines[1]}")
                        
                        # Check for span
                        span = li.find('span', style=lambda style: style and 'font-size: 0.8em' in style)
                        if span:
                            print(f"     Span: {span.get_text().strip()}")

if __name__ == "__main__":
    debug_in_this_issue()