#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_final_shopping():
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
        print("🎯 FINAL SHOPPING IMPLEMENTATION TEST")
        print("=" * 60)
        
        # Check author details
        author = result.content.author
        print(f"👤 AUTHOR DETAILS:")
        print(f"   Name: {author.get('name', 'N/A')}")
        print(f"   Title: {author.get('title', 'N/A')}")
        print(f"   Bio: {author.get('bio', 'N/A')[:80]}...")
        print(f"   Image URL: {author.get('image', {}).get('url', 'N/A')}")
        
        # Check featured image
        print(f"\n🖼️  FEATURED IMAGE:")
        print(f"   URL: {result.content.featured_image}")
        print(f"   Alt: {result.content.image_alt}")
        
        # Check schema duplication removal
        print(f"\n🗑️  DUPLICATION REMOVAL:")
        print(f"   product_categories: {len(result.content.product_categories)} items")
        print(f"   seasonal_items: {len(result.content.seasonal_items)} items")
        print(f"   kirkland_signature: {len(result.content.kirkland_signature)} items")
        
        # Check sections
        print(f"\n📄 SECTIONS:")
        print(f"   Total sections: {len(result.sections)}")
        print(f"   Total content across sections: {sum(len(s.get('content', [])) for s in result.sections)}")
        print(f"   Total images across sections: {sum(len(s.get('images', [])) for s in result.sections)}")
        
        # Verify zero duplication
        all_content = []
        for section in result.sections:
            all_content.extend(section.get('content', []))
        
        unique_content = set(all_content)
        duplication_rate = (len(all_content) - len(unique_content)) / len(all_content) * 100 if all_content else 0
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"   ✅ Duplication rate: {duplication_rate:.1f}%")
        print(f"   ✅ Author extracted: {'Yes' if author.get('name') else 'No'}")
        print(f"   ✅ Featured image: {'Yes' if result.content.featured_image else 'No'}")
        print(f"   ✅ Schema cleaned: {'Yes' if len(result.content.product_categories) == 0 else 'No'}")
        print(f"   ✅ Comment-guided sections: {'Yes' if len(result.sections) > 0 else 'No'}")
        
        if duplication_rate == 0.0 and author.get('name') and result.content.featured_image and len(result.content.product_categories) == 0:
            print(f"\n🎉 ALL REQUIREMENTS MET - IMPLEMENTATION COMPLETE!")
        else:
            print(f"\n⚠️  Some requirements not fully met")
        
        return True
    else:
        print("❌ Processing failed")
        return False

if __name__ == "__main__":
    test_final_shopping()