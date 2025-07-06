#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_treasure_hunt_images():
    processor = FixedSuperEnhancedCostcoProcessor()
    
    filename = 'Treasure Hunt  _ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    result = processor.process_content(
        html_content=html_content,
        url='https://www.costco.com/treasure-hunt',
        filename=filename
    )
    
    if result:
        print("🏴‍☠️ TREASURE HUNT IMAGE URL TEST")
        print("=" * 50)
        
        # Check all sections for images
        total_images = 0
        local_images = 0
        fixed_images = 0
        
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
                        fixed_images += 1
                    elif src.startswith('./'):
                        print(f"      ❌ BROKEN: Still local path")
                        local_images += 1
                    else:
                        print(f"      ⚠️  OTHER: {src[:50]}...")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total images: {total_images}")
        print(f"   Fixed images: {fixed_images}")
        print(f"   Local images: {local_images}")
        
        if local_images == 0:
            print(f"   ✅ SUCCESS: All images have proper URLs!")
        else:
            print(f"   ❌ ISSUE: {local_images} images still have local paths")
        
        return local_images == 0
    else:
        print("❌ Processing failed for Treasure Hunt")
        return False

if __name__ == "__main__":
    test_treasure_hunt_images()