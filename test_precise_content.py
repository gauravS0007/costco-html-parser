#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'

with open(file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

extractor = FixedUniversalContentExtractor()
extracted = extractor.extract_all_content(html_content, 'https://www.costco.com/buying-smart')

print("🔍 PRECISE CONTENT CHECK")
print("=" * 40)

# Test the specific missing content
expected_missing = [
    "Through Costco's Countertop Installation program, the process for members who want to upgrade their countertops is remarkably easy and convenient",
    "When the job is completed, not only is there a gorgeous counter to enjoy for years to come, you'll also receive a Costco Shop Card for 10% of its cost"
]

print(f"Total extracted paragraphs: {len(extracted.main_content)}")
print(f"Total full text length: {len(extracted.full_text)}")

for i, expected in enumerate(expected_missing):
    print(f"\n{i+1}. SEARCHING FOR: {expected}")
    
    # Check in main_content
    found_in_main = False
    for j, content in enumerate(extracted.main_content):
        if expected.lower() in content.lower():
            print(f"   ✅ FOUND in main_content[{j}]")
            print(f"   Full paragraph: {content}")
            found_in_main = True
            break
    
    if not found_in_main:
        print(f"   ❌ NOT FOUND in main_content")
        
        # Check in full text
        if expected.lower() in extracted.full_text.lower():
            print(f"   ✅ FOUND in full_text")
        else:
            print(f"   ❌ NOT FOUND in full_text")
            
        # Look for partial matches
        words = expected.lower().split()[:5]  # First 5 words
        partial_search = " ".join(words)
        print(f"   Searching for partial: {partial_search}")
        
        for j, content in enumerate(extracted.main_content):
            if partial_search in content.lower():
                print(f"   🔍 PARTIAL MATCH in main_content[{j}]: {content[:100]}...")
                break

print(f"\n📝 ALL EXTRACTED CONTENT:")
for i, content in enumerate(extracted.main_content):
    print(f"{i+1:2d}. {content[:120]}...")