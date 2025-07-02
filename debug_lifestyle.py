#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

def debug_lifestyle_extraction():
    """Debug the lifestyle extraction step by step"""
    
    extractor = FixedUniversalContentExtractor()
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"\n🔍 Debugging: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Step 1: Check content type detection
        soup = BeautifulSoup(html_content, 'html.parser')
        main_content = soup.find('main') or soup.find('article') or soup
        content_type = extractor._detect_content_type(html_file, soup, main_content)
        print(f"Content type detected: {content_type}")
        
        # Step 2: Extract all content
        extracted = extractor.extract_all_content(html_content, html_file)
        
        print(f"\n📊 EXTRACTION RESULTS:")
        print(f"Content type: {extracted.content_type}")
        print(f"Title: {extracted.title}")
        print(f"Headings found: {len(extracted.headings)}")
        print(f"Images found: {len(extracted.images)}")
        
        # Step 3: Check headings data structure
        if extracted.headings:
            print(f"\n🎯 HEADINGS ANALYSIS:")
            for i, heading in enumerate(extracted.headings):
                print(f"Heading {i+1}: {heading.get('text', 'No text')}")
                print(f"  Level: {heading.get('level', 'No level')}")
                print(f"  Content items: {len(heading.get('content', []))}")
                print(f"  Images: {len(heading.get('images', []))}")
                
                if heading.get('images'):
                    for j, img in enumerate(heading.get('images', [])):
                        filename = img.get('src', '').split('/')[-1] if img.get('src') else 'unknown'
                        print(f"    Image {j+1}: {filename}")
                        print(f"      Alt: {img.get('alt', '')}")
                        print(f"      Caption: {img.get('caption', '')}")
        
        # Step 4: Check main content area for headings
        print(f"\n🔍 RAW HTML HEADINGS CHECK:")
        soup = BeautifulSoup(html_content, 'html.parser')
        main_area = soup.find('main') or soup.find('article') or soup.find(class_=lambda x: x and 'content' in x.lower()) or soup
        
        all_headings = main_area.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        print(f"Raw headings found in HTML: {len(all_headings)}")
        
        for i, h in enumerate(all_headings[:10]):  # Show first 10
            print(f"  {i+1}. {h.name}: {h.get_text().strip()[:50]}...")
        
        # Step 5: Check images in HTML
        all_images = main_area.find_all('img')
        print(f"\nRaw images found in HTML: {len(all_images)}")
        
        for i, img in enumerate(all_images[:5]):  # Show first 5
            src = img.get('src', '')
            filename = src.split('/')[-1] if src else 'no-src'
            alt = img.get('alt', '')
            print(f"  {i+1}. {filename} (alt: {alt[:30]}...)")
        
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    debug_lifestyle_extraction()