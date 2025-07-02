#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_all_images():
    """Debug all images found during extraction"""
    
    extractor = FixedUniversalContentExtractor()
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"\n🔍 Debugging all images: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Extract all content to see all images
        extracted = extractor.extract_all_content(html_content, html_file)
        
        print(f"\n📊 ALL EXTRACTED IMAGES ({len(extracted.images)}):")
        
        for i, img in enumerate(extracted.images):
            src = img.get('src', '')
            filename = src.split('/')[-1] if src else 'no-src'
            alt = img.get('alt', '')
            score = img.get('score', 0)
            
            print(f"{i+1:2d}. {filename}")
            print(f"    Alt: {alt}")
            print(f"    Score: {score}")
            print(f"    Full src: {src}")
            print()

if __name__ == "__main__":
    debug_all_images()