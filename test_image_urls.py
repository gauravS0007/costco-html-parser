#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_image_urls():
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Test Treasure Hunt file if it exists
    treasure_hunt_file = 'Treasure Hunt  _ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{treasure_hunt_file}'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        result = processor.process_content(
            html_content=html_content,
            url='https://www.costco.com/treasure-hunt',
            filename=treasure_hunt_file
        )
        
        if result:
            print("🖼️  TREASURE HUNT IMAGE URL TEST")
            print("=" * 50)
            
            # Check all sections for images
            for i, section in enumerate(result.sections):
                heading = section.get('heading', '')
                images = section.get('images', [])
                
                if images:
                    print(f"\n📄 SECTION: {heading}")
                    print(f"   Images: {len(images)}")
                    
                    for j, img in enumerate(images):
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        
                        print(f"   {j+1}. Alt: {alt}")
                        print(f"      Src: {src}")
                        
                        # Check if URL is fixed properly
                        if src.startswith('http'):
                            print(f"      ✅ FIXED: Proper HTTP URL")
                        elif src.startswith('./'):
                            print(f"      ❌ BROKEN: Still local path")
                        else:
                            print(f"      ⚠️  OTHER: {src[:50]}...")
            
            return True
        else:
            print("❌ Processing failed for Treasure Hunt")
            return False
            
    except FileNotFoundError:
        print("⚠️  Treasure Hunt file not found, testing with Buying Smart")
        
        # Fallback to Buying Smart
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
            print("🖼️  BUYING SMART IMAGE URL TEST")
            print("=" * 50)
            
            # Check all sections for images
            total_images = 0
            for i, section in enumerate(result.sections):
                heading = section.get('heading', '')
                images = section.get('images', [])
                
                if images:
                    total_images += len(images)
                    print(f"\n📄 SECTION: {heading}")
                    print(f"   Images: {len(images)}")
                    
                    for j, img in enumerate(images):
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        
                        print(f"   {j+1}. Alt: {alt}")
                        print(f"      Src: {src}")
                        
                        # Check if URL is fixed properly
                        if src.startswith('https://'):
                            print(f"      ✅ FIXED: Proper HTTPS URL")
                        elif src.startswith('./'):
                            print(f"      ❌ BROKEN: Still local path")
                        else:
                            print(f"      ⚠️  OTHER: {src[:50]}...")
            
            print(f"\n📊 SUMMARY: {total_images} total images found")
            return True
        else:
            print("❌ Processing failed for Buying Smart")
            return False

if __name__ == "__main__":
    test_image_urls()