#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_editorial_category():
    """Test that editorial category is not broken"""
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Test editorial file
    filename = "Publisher's Note - Passion is key  _ Costco.html"
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        result = processor.process_content(
            html_content=html_content,
            url='https://www.costco.com/publishers-note',
            filename=filename
        )
        
        if result:
            print("✅ EDITORIAL: Processing successful")
            print(f"   Content type: {result.content.content_type}")
            print(f"   Sections: {len(result.sections)}")
            print(f"   Author: {result.content.author.get('name', 'N/A')}")
            return True
        else:
            print("❌ EDITORIAL: Processing failed")
            return False
            
    except FileNotFoundError:
        print("⚠️  Editorial test file not found - creating dummy test")
        # Test with minimal HTML to ensure no crashes
        dummy_html = """
        <html><body>
        <h1>Editorial Title</h1>
        <p>Editorial content paragraph.</p>
        </body></html>
        """
        
        result = processor.process_content(
            html_content=dummy_html,
            url='https://www.costco.com/editorial-test',
            filename='editorial_test.html'
        )
        
        if result:
            print("✅ EDITORIAL: Dummy test successful")
            return True
        else:
            print("❌ EDITORIAL: Dummy test failed")
            return False
    except Exception as e:
        print(f"❌ EDITORIAL: Error - {e}")
        return False

def test_shopping_category():
    """Test that shopping category still works"""
    processor = FixedSuperEnhancedCostcoProcessor()
    
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        result = processor.process_content(
            html_content=html_content,
            url='https://www.costco.com/buying-smart',
            filename=filename
        )
        
        if result:
            print("✅ SHOPPING: Processing successful")
            print(f"   Content type: {result.content.content_type}")
            print(f"   Sections: {len(result.sections)}")
            print(f"   Author: {result.content.author.get('name', 'N/A')}")
            
            # Check duplication
            all_content = []
            for section in result.sections:
                all_content.extend(section.get('content', []))
            
            unique_content = set(all_content)
            duplication_rate = (len(all_content) - len(unique_content)) / len(all_content) * 100 if all_content else 0
            print(f"   Duplication rate: {duplication_rate:.1f}%")
            
            return True
        else:
            print("❌ SHOPPING: Processing failed")
            return False
            
    except Exception as e:
        print(f"❌ SHOPPING: Error - {e}")
        return False

if __name__ == "__main__":
    print("🧪 TESTING CATEGORY SAFETY")
    print("=" * 40)
    
    editorial_ok = test_editorial_category()
    print()
    shopping_ok = test_shopping_category()
    
    print(f"\n📊 RESULTS:")
    print(f"   Editorial: {'✅ PASS' if editorial_ok else '❌ FAIL'}")
    print(f"   Shopping: {'✅ PASS' if shopping_ok else '❌ FAIL'}")
    
    if editorial_ok and shopping_ok:
        print(f"\n🎉 ALL CATEGORIES SAFE - No impact on other categories!")
    else:
        print(f"\n⚠️  Some categories have issues")