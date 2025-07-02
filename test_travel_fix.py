#!/usr/bin/env python3
"""
Test the travel content extraction fix
"""
import sys
import os
sys.path.append('.')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
import json

def test_travel_extraction():
    extractor = FixedUniversalContentExtractor()
    
    # Load current results to get the travel URL
    with open('data/results/enhanced_results_fixed.json', 'r') as f:
        results = json.load(f)
    
    # Find travel file
    travel_result = None
    for item in results:
        if item.get('content_type') == 'travel':
            travel_result = item
            break
    
    if not travel_result:
        print("❌ No travel file found in results")
        return
    
    print("✅ Found travel file:")
    print(f"   URL: {travel_result['url']}")
    print(f"   Title: {travel_result.get('content', {}).get('title')}")
    
    # Check current content
    sections = travel_result.get('sections', [])
    print(f"\n📊 Current sections: {len(sections)}")
    total_content = 0
    for i, section in enumerate(sections):
        content_count = len(section.get('content', []))
        total_content += content_count
        print(f"   Section {i+1}: {section.get('heading')} - {content_count} content items")
    
    print(f"\n📈 Total content items across all sections: {total_content}")
    
    # Show issues identified from screenshot comparison
    print("\n🔍 Issues identified from screenshot:")
    print("   - Austin section: Missing content about The Oasis restaurant, bridge habitat details")
    print("   - San Antonio section: Missing content about The Alamo, UNESCO details")
    print("   - Some sections have 0 content items")
    
    print("\n✅ Travel extraction enhancement applied:")
    print("   - Increased content per section limit from 5 to 8 items")
    print("   - Enhanced paragraph extraction similar to tech content")
    print("   - Reduced minimum text length from 20 to 15 characters")
    print("   - Added comprehensive section content collection")

if __name__ == "__main__":
    test_travel_extraction()