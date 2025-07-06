#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_magazine_images_full():
    processor = FixedSuperEnhancedCostcoProcessor()
    
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    result = processor.process_content(
        html_content=html_content,
        url='https://www.costco.com/October-Edition-',
        filename=filename
    )
    
    if result:
        print("🖼️  MAGAZINE ARTICLE IMAGES TEST")
        print("=" * 80)
        
        # Check article categories for images
        article_categories = getattr(result.content, 'article_categories', {})
        
        for category, articles in article_categories.items():
            print(f"\n📚 {category}:")
            for article in articles:
                title = article.get('title', 'No title')
                image = article.get('image', '')
                image_alt = article.get('image_alt', '')
                
                print(f"   📄 {title}")
                if image:
                    print(f"      🖼️  {image_alt}")
                    print(f"      🔗 {image}")
                else:
                    print(f"      ❌ No image")

if __name__ == "__main__":
    test_magazine_images_full()