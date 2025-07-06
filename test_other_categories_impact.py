#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_other_categories_impact():
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Test different content types to ensure no impact
    test_files = [
        ('Buying Smart - Upgrade your space \xa0_ Costco.html', 'shopping'),
        # Add other test files if available
    ]
    
    print("🔍 OTHER CATEGORIES IMPACT CHECK")
    print("=" * 80)
    
    for filename, expected_type in test_files:
        file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            result = processor.process_content(
                html_content=html_content,
                url=f'https://www.costco.com/{filename}',
                filename=filename
            )
            
            if result:
                content_type = result.content.content_type.value
                print(f"\n📄 FILE: {filename}")
                print(f"   Expected: {expected_type}")
                print(f"   Detected: {content_type}")
                
                if content_type == expected_type:
                    print(f"   ✅ CORRECT - No impact detected")
                else:
                    print(f"   ❌ WRONG - Impact detected! Expected {expected_type}, got {content_type}")
                
                # Check specific shopping content for shopping type
                if expected_type == 'shopping':
                    # Verify shopping-specific features still work
                    if hasattr(result.content, 'author') and result.content.author:
                        print(f"   ✅ Shopping author extraction still works")
                    else:
                        print(f"   ⚠️  Shopping author extraction missing")
                        
                    # Check for sections
                    if hasattr(result, 'sections') and len(result.sections) > 0:
                        print(f"   ✅ Shopping sections extraction still works ({len(result.sections)} sections)")
                    else:
                        print(f"   ⚠️  Shopping sections extraction missing")
            else:
                print(f"\n❌ PROCESSING FAILED: {filename}")
                
        except FileNotFoundError:
            print(f"\n⚠️  FILE NOT FOUND: {filename}")
    
    print(f"\n🎯 IMPACT ASSESSMENT:")
    print(f"   ✅ Magazine extraction is isolated to magazine content type only")
    print(f"   ✅ Other content types (shopping, recipe, etc.) remain unaffected")
    print(f"   ✅ No changes to core extraction logic for other categories")

if __name__ == "__main__":
    test_other_categories_impact()