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

print("🎯 FINAL ACCURACY VERIFICATION")
print("=" * 50)

# User's specific requirements from the conversation
required_content = [
    "Through Costco's Countertop Installation program, the process for members who want to upgrade their countertops is remarkably easy and convenient",
    "It's truly white-glove service",
    "During your appointment, the design specialist will take detailed measurements",
    "When the job is completed, not only is there a gorgeous counter to enjoy for years to come, you'll also receive a Costco Shop Card for 10% of its cost",
    "Costco does the heavy lifting for our members",
    "Sustainability is a core value at Cosentino"
]

print(f"📊 EXTRACTION RESULTS:")
print(f"   Total paragraphs extracted: {len(extracted.main_content)}")
print(f"   Full text length: {len(extracted.full_text)}")
print(f"   Author: {extracted.byline}")

print(f"\n✅ CONTENT VERIFICATION:")
all_found = True
for i, content in enumerate(required_content):
    found = any(content in para for para in extracted.main_content)
    status = "✅ FOUND" if found else "❌ MISSING"
    print(f"   {i+1}. {status}: {content[:60]}...")
    if not found:
        all_found = False

print(f"\n📝 SUCCESS RATE: {sum(1 for content in required_content if any(content in para for para in extracted.main_content))}/{len(required_content)} = {(sum(1 for content in required_content if any(content in para for para in extracted.main_content))/len(required_content)*100):.1f}%")

if all_found:
    print("\n🎉 ALL CONTENT SUCCESSFULLY EXTRACTED!")
    print("   ✅ Navigation filtering fixed")
    print("   ✅ Paragraph parsing improved")
    print("   ✅ Missing content now captured")
else:
    print("\n⚠️  Some content still missing - needs further investigation")

print(f"\n📋 COMPLETE EXTRACTED CONTENT:")
for i, para in enumerate(extracted.main_content):
    print(f"{i+1:2d}. {para}")