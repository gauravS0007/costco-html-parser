#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def debug_h1_sections():
    processor = FixedSuperEnhancedCostcoProcessor()
    
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    result = processor.process_content(
        html_content=html_content,
        url='https://www.costco.com/buying-smart',
        filename=filename
    )
    
    if result:
        print("🔍 H1 SECTIONS ANALYSIS")
        print("=" * 60)
        
        h1_sections = [s for s in result.sections if s.get('level') == 1]
        other_sections = [s for s in result.sections if s.get('level') != 1]
        
        print(f"H1 sections found: {len(h1_sections)}")
        print(f"Other sections found: {len(other_sections)}")
        
        for i, section in enumerate(h1_sections):
            print(f"\n📄 H1 SECTION #{i+1}:")
            print(f"   Heading: '{section.get('heading', '')}'")
            print(f"   Content items: {len(section.get('content', []))}")
            print(f"   Images: {len(section.get('images', []))}")
            
            if section.get('content'):
                print("   📝 Content:")
                for j, content in enumerate(section.get('content', [])[:3]):
                    print(f"      {j+1}. {content[:60]}...")
                    
            if section.get('images'):
                print("   🖼️  Images:")
                for j, img in enumerate(section.get('images', [])):
                    print(f"      {j+1}. {img.get('alt', 'No alt')} - {img.get('src', '')[:60]}...")
        
        # Check if both H1 headings are in the HTML
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        all_h1s = soup.find_all('h1')
        
        print(f"\n🔍 ALL H1 TAGS IN HTML:")
        for i, h1 in enumerate(all_h1s):
            print(f"   H1 #{i+1}: '{h1.get_text().strip()}'")
            
        print(f"\n🎯 SUMMARY:")
        print(f"   Expected H1 sections: 2 ('Buying Smart', 'Upgrade your space')")
        print(f"   Actual H1 sections: {len(h1_sections)}")
        
        if len(h1_sections) < 2:
            print(f"   ❌ Missing H1 section(s)")
        else:
            print(f"   ✅ All H1 sections found")

if __name__ == "__main__":
    debug_h1_sections()