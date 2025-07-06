#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_complete_sections():
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
        print("🎯 SHOPPING SECTIONS - COMPLETE CONTENT CHECK")
        print("=" * 60)
        
        # Check specific sections mentioned by user
        target_sections = [
            "Transform your kitchen (or bathroom) with Costco's Countertop Installation program",
            "Getting started", 
            "Installation, done right",
            "More about Dekton"
        ]
        
        for section in result.sections:
            heading = section.get('heading', '')
            if any(target in heading for target in target_sections):
                print(f"\n📄 SECTION: {heading}")
                print(f"   Level: {section.get('level', 'N/A')}")
                
                content = section.get('content', [])
                print(f"   Content: {len(content)} paragraphs")
                
                for i, para in enumerate(content):
                    print(f"      {i+1}. {para[:100]}...")
                    
                    # Check for specific missing content
                    if 'white-glove service' in para:
                        print("         ✅ FOUND: white-glove service paragraph")
                    if 'During your appointment' in para:
                        print("         ✅ FOUND: During your appointment paragraph") 
                    if 'Costco Shop Card for 10%' in para:
                        print("         ✅ FOUND: Costco Shop Card paragraph")
                
                images = section.get('images', [])
                print(f"   Images: {len(images)}")
                for i, img in enumerate(images):
                    print(f"      {i+1}. {img.get('alt', 'No alt')} (score: {img.get('relevance_score', 0)})")
                    if 'rock' in img.get('alt', '').lower() and 'dekton' in heading.lower():
                        print("         ✅ CORRECT: Rock image in Dekton section")
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total sections: {len(result.sections)}")
        print(f"   Author: {result.content.author.get('name', 'N/A')}")
        
    else:
        print("❌ Processing failed")

if __name__ == "__main__":
    test_complete_sections()