#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_detailed_sections():
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
        print("🔍 DETAILED SECTION ANALYSIS")
        print("=" * 80)
        
        for i, section in enumerate(result.sections):
            print(f"\n📄 SECTION {i+1}: {section.get('heading', 'No heading')}")
            print(f"   Level: H{section.get('level', 'Unknown')}")
            print(f"   Content paragraphs: {len(section.get('content', []))}")
            print(f"   Images: {len(section.get('images', []))}")
            
            # Show first few content items
            content = section.get('content', [])
            if content:
                print("   📝 Content preview:")
                for j, text in enumerate(content[:2]):  # Show first 2 items
                    print(f"      {j+1}. {text[:80]}...")
            
            # Show images
            images = section.get('images', [])
            if images:
                print("   🖼️  Images:")
                for j, img in enumerate(images):
                    src = img.get('src', '')
                    alt = img.get('alt', '')
                    print(f"      {j+1}. Alt: {alt}")
                    print(f"         Src: {src}")
                    
                    # Check if it's an ad
                    if any(keyword in alt.lower() for keyword in ['kirkland', 'socks', 'kitty', 'pet', 'click here']):
                        print(f"         🚫 AD IMAGE DETECTED!")
        
        print(f"\n🎯 SUMMARY:")
        print(f"   Total sections: {len(result.sections)}")
        print(f"   Author: {result.content.author.get('name', 'N/A')}")
        print(f"   Featured image: {result.content.featured_image}")
        
        return True
    else:
        print("❌ Processing failed")
        return False

if __name__ == "__main__":
    test_detailed_sections()