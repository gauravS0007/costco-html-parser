#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor
from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def test_content_accuracy():
    """Compare extracted content with actual content from screenshot"""
    
    # Expected content from the screenshot
    expected_missing = [
        "Through Costco's Countertop Installation program, the process for members who want to upgrade their countertops is remarkably easy and convenient",
        "white-glove service",
        "During your appointment, the design specialist will take detailed measurements",
        "When the job is completed, not only is there a gorgeous counter to enjoy for years to come, you'll also receive a Costco Shop Card for 10% of its cost",
        "A cut above",
        "Costco does the heavy lifting for our members",
        "Sustainability matters",
        "Sustainability is a core value at Cosentino"
    ]
    
    filename = 'Buying Smart - Upgrade your space \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Test both extractor and processor
    print("🔍 CONTENT ACCURACY CHECK")
    print("=" * 50)
    
    extractor = FixedUniversalContentExtractor()
    extracted = extractor.extract_all_content(html_content, 'https://www.costco.com/buying-smart')
    
    print(f"📄 Extracted main_content: {len(extracted.main_content)} paragraphs")
    print(f"📄 Extracted headings: {len(extracted.headings)}")
    
    # Check what's missing
    print("\n❌ MISSING CONTENT CHECK:")
    for i, expected in enumerate(expected_missing):
        found = False
        for content in extracted.main_content:
            if expected.lower() in content.lower():
                print(f"   ✅ {i+1}. Found: {expected[:50]}...")
                found = True
                break
        if not found:
            print(f"   ❌ {i+1}. MISSING: {expected[:50]}...")
    
    # Check full text
    print(f"\n📝 Full text length: {len(extracted.full_text)}")
    print("Full text contains:")
    for expected in expected_missing[:3]:  # Check first 3
        if expected.lower() in extracted.full_text.lower():
            print(f"   ✅ Found in full_text: {expected[:30]}...")
        else:
            print(f"   ❌ Missing from full_text: {expected[:30]}...")
    
    # Test processor
    print("\n🔧 PROCESSOR TEST:")
    processor = FixedSuperEnhancedCostcoProcessor()
    result = processor.process_content(html_content, 'https://www.costco.com/buying-smart', filename)
    
    if result:
        print(f"   Sections: {len(result.sections)}")
        
        # Check specific sections
        expected_sections = ["Transform your kitchen", "Getting started", "Installation, done right", "A cut above", "Sustainability matters", "More about Dekton"]
        
        actual_sections = [s.get('heading', '') for s in result.sections]
        print(f"   Actual sections: {[s[:20] + '...' if len(s) > 20 else s for s in actual_sections]}")
        
        for expected_section in expected_sections:
            found = any(expected_section.lower() in actual.lower() for actual in actual_sections)
            status = "✅" if found else "❌"
            print(f"   {status} {expected_section}")

if __name__ == "__main__":
    test_content_accuracy()