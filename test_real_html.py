#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'

with open(file_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("🔍 TESTING REAL HTML FILE")
print("=" * 40)

soup = BeautifulSoup(html_content, 'html.parser')

# Find all paragraphs
paragraphs = soup.find_all('p')
print(f"1. Found {len(paragraphs)} paragraph tags total")

# Look for our target paragraphs
target_phrases = [
    "Through Costco's Countertop Installation program",
    "When the job is completed, not only is there a gorgeous counter"
]

print("\n2. Searching for target content:")
for phrase in target_phrases:
    found = False
    for i, p in enumerate(paragraphs):
        text = p.get_text().strip()
        if phrase in text:
            print(f"   ✅ FOUND in paragraph {i+1}: {phrase}")
            print(f"      Full text: {text}")
            found = True
            break
    if not found:
        print(f"   ❌ NOT FOUND: {phrase}")

# Test the extractor
print(f"\n3. Testing extractor:")
extractor = FixedUniversalContentExtractor()
extracted = extractor.extract_all_content(html_content, 'https://www.costco.com/buying-smart')

print(f"   Extracted {len(extracted.main_content)} paragraphs")

# Check if target content is in extracted
for phrase in target_phrases:
    found = any(phrase in content for content in extracted.main_content)
    status = "✅ FOUND" if found else "❌ MISSING"
    print(f"   {status}: {phrase[:50]}...")

# Show first few extracted paragraphs
print(f"\n4. First 10 extracted paragraphs:")
for i, content in enumerate(extracted.main_content[:10]):
    print(f"   {i+1}. {content[:80]}...")