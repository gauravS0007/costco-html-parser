#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_improved_sections():
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
        print("🎯 IMPROVED SHOPPING SECTIONS TEST")
        print("=" * 60)
        
        print(f"📊 SUMMARY:")
        print(f"   Total sections: {len(result.sections)}")
        print(f"   Author: {result.content.author.get('name', 'N/A')}")
        
        print(f"\n📋 SECTION BREAKDOWN:")
        total_content_items = 0
        for i, section in enumerate(result.sections):
            heading = section.get('heading', '')
            level = section.get('level', 0)
            content = section.get('content', [])
            images = section.get('images', [])
            
            print(f"\n{i+1}. SECTION: {heading}")
            print(f"   Level: H{level}")
            print(f"   Content items: {len(content)}")
            print(f"   Images: {len(images)}")
            
            total_content_items += len(content)
            
            # Show first 2 content items for verification
            for j, para in enumerate(content[:2]):
                print(f"      {j+1}. {para[:80]}...")
            
            if len(content) > 2:
                print(f"      ... and {len(content) - 2} more items")
        
        print(f"\n📈 DUPLICATION CHECK:")
        print(f"   Total content items across all sections: {total_content_items}")
        
        # Check for duplicate content between sections
        all_content = []
        for section in result.sections:
            all_content.extend(section.get('content', []))
        
        unique_content = set(all_content)
        duplication_rate = (len(all_content) - len(unique_content)) / len(all_content) * 100 if all_content else 0
        
        print(f"   Unique content items: {len(unique_content)}")
        print(f"   Duplication rate: {duplication_rate:.1f}%")
        
        if duplication_rate < 10:
            print(f"   ✅ SUCCESS: Low duplication rate!")
        else:
            print(f"   ⚠️  WARNING: High duplication rate")
        
        # Check if key content is present
        target_content = [
            "Through Costco's Countertop Installation program",
            "white-glove service",
            "When the job is completed",
            "Sustainability is a core value at Cosentino"
        ]
        
        print(f"\n🔍 KEY CONTENT CHECK:")
        for target in target_content:
            found = any(target in para for section in result.sections for para in section.get('content', []))
            status = "✅ FOUND" if found else "❌ MISSING"
            print(f"   {status}: {target[:40]}...")
    
    else:
        print("❌ Processing failed")

if __name__ == "__main__":
    test_improved_sections()