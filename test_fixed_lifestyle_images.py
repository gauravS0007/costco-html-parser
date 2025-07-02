#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_lifestyle_image_placement():
    """Test the fixed lifestyle image placement logic"""
    
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Test with the lifestyle URLs that have image placement issues
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"\n🔍 Testing: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        result = processor.process_content(html_content, html_file, html_file)
        
        if result and hasattr(result, 'sections'):
            print(f"\n📊 SECTIONS ANALYSIS:")
            print(f"Total sections found: {len(result.sections)}")
            
            # Track images across sections
            total_images = 0
            image_urls = set()
            
            for i, section in enumerate(result.sections):
                # Access section attributes properly
                heading = getattr(section, 'heading', 'No heading')
                images = getattr(section, 'images', [])
                
                section_image_count = len(images)
                total_images += section_image_count
                
                print(f"\n🎯 Section {i+1}: '{heading}'")
                print(f"   Images: {section_image_count}")
                
                if images:
                    for j, img in enumerate(images):
                        # Handle both dict and object attributes
                        if hasattr(img, 'src'):
                            img_url = img.src
                            img_alt = getattr(img, 'alt', '')
                            img_caption = getattr(img, 'caption', '')
                        else:
                            img_url = img.get('src', '') if isinstance(img, dict) else ''
                            img_alt = img.get('alt', '') if isinstance(img, dict) else ''
                            img_caption = img.get('caption', '') if isinstance(img, dict) else ''
                        
                        # Track unique images
                        if img_url:
                            image_urls.add(img_url)
                        
                        # Extract meaningful parts from URL for identification
                        filename = img_url.split('/')[-1] if img_url else 'unknown'
                        
                        print(f"     📷 Image {j+1}: {filename}")
                        print(f"         Alt: {img_alt}")
                        if img_caption:
                            print(f"         Caption: {img_caption}")
            
            # Final analysis
            print(f"\n🔍 DUPLICATE ANALYSIS:")
            print(f"Total image instances: {total_images}")
            print(f"Unique images: {len(image_urls)}")
            print(f"Duplicates detected: {'YES' if total_images > len(image_urls) else 'NO'}")
            
            # Section placement accuracy
            print(f"\n📍 PLACEMENT ACCURACY CHECK:")
            for i, section in enumerate(result.sections):
                heading = getattr(section, 'heading', '').lower()
                images = getattr(section, 'images', [])
                
                if images:
                    for img in images:
                        if hasattr(img, 'src'):
                            img_url = img.src
                        else:
                            img_url = img.get('src', '') if isinstance(img, dict) else ''
                        
                        filename = img_url.split('/')[-1].lower() if img_url else ''
                        
                        print(f"Section: '{heading}' -> Image: {filename}")
                        
                        # Check for obvious misplacements
                        if 'glasses' in filename and 'donation' not in heading:
                            print(f"   ⚠️  POTENTIAL MISPLACEMENT: Glasses image not in donation section")
                        elif 'card' in filename and 'card' not in heading and 'travel' not in heading:
                            print(f"   ⚠️  POTENTIAL MISPLACEMENT: Card image not in card/travel section")
                        elif 'rollup' in filename and 'recipe' not in heading and 'lasagna' not in heading:
                            print(f"   ⚠️  POTENTIAL MISPLACEMENT: Recipe image not in recipe section")
                        else:
                            print(f"   ✅ Placement looks correct")
            
        else:
            print(f"❌ Failed to process or no sections found")
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    test_lifestyle_image_placement()