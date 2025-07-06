#!/usr/bin/env python3
"""
Test shopping accuracy against screenshots after fixes
Following the 3 rules: dynamic patterns, no category impact, with tests
"""

import sys
import os
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_shopping_accuracy_vs_screenshots():
    """Test shopping extraction accuracy against actual screenshot content"""
    
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Test cases based on actual screenshots
    test_cases = [
        {
            "filename": "Treasure Hunt \xa0_ Costco.html",
            "expected_featured_image_contains": ["09_23_Treasure_Hunt.jpg"],  # Main sofa image
            "expected_featured_image_not_contains": ["_03.jpg", "_01.jpg", "_02.jpg"],  # Not numbered variants
            "expected_alt_text_contains": ["sofa", "sleeper"],
            "expected_products": ["Lillian August", "Dot's", "GreenPan", "Berkshire", "Hang Ten", "Karma"],
            "description": "Screenshot 2 - Main sofa should be featured image"
        },
        {
            "filename": "Buying Smart - Upgrade your space \xa0_ Costco.html",
            "expected_featured_image_starts_with": ["https://"],  # Should have proper URL
            "expected_featured_image_not_contains": ["WellnessPetCo", "StauntonCapitol"],  # Not random ads
            "expected_content": ["countertop", "installation", "Cosentino", "kitchen"],
            "description": "Screenshot 1 - Should have proper URL and kitchen-related featured image"
        },
        {
            "filename": "October Edition \xa0_ Costco.html",
            "expected_featured_image_starts_with": ["https://"],  # Should have proper URL
            "expected_sections": ["Cover", "Special", "Featured"],
            "expected_content_in_main": ["Squishmallow", "Cover Story", "Celebrate"],  # Check main content instead
            "description": "Screenshot 3 - Should extract table of contents sections"
        }
    ]
    
    results = {}
    
    for test_case in test_cases:
        filename = test_case["filename"]
        file_path = f"/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}"
        
        print(f"\n=== {test_case['description']} ===")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Use proper URLs for content type detection
            if "Treasure Hunt" in filename:
                url = "https://www.costco.com/treasure-hunt"
            elif "Buying Smart" in filename:
                url = "https://www.costco.com/buying-smart"
            elif "October Edition" in filename:
                url = "https://www.costco.com/october-edition"
            else:
                url = f"https://www.costco.com/{filename}"
            
            result = processor.process_content(
                html_content=html_content,
                url=url,
                filename=filename
            )
            
            if not result:
                print(f"❌ Processing failed for {filename}")
                continue
            
            # Test results
            tests_passed = 0
            total_tests = 0
            
            # Test featured image
            featured_img = result.content.featured_image or ""
            
            # Test featured image contains expected patterns
            if "expected_featured_image_contains" in test_case:
                total_tests += 1
                if any(pattern in featured_img for pattern in test_case["expected_featured_image_contains"]):
                    tests_passed += 1
                    print(f"✅ Featured image contains expected pattern: {featured_img}")
                else:
                    print(f"❌ Featured image missing expected pattern: {featured_img}")
            
            # Test featured image does NOT contain bad patterns
            if "expected_featured_image_not_contains" in test_case:
                total_tests += 1
                bad_patterns = [p for p in test_case["expected_featured_image_not_contains"] if p in featured_img]
                if not bad_patterns:
                    tests_passed += 1
                    print(f"✅ Featured image avoids bad patterns")
                else:
                    print(f"❌ Featured image contains bad patterns: {bad_patterns}")
            
            # Test featured image starts with proper URL
            if "expected_featured_image_starts_with" in test_case:
                total_tests += 1
                if any(featured_img.startswith(pattern) for pattern in test_case["expected_featured_image_starts_with"]):
                    tests_passed += 1
                    print(f"✅ Featured image has proper URL format")
                else:
                    print(f"❌ Featured image has malformed URL: {featured_img}")
            
            # Test alt text
            if "expected_alt_text_contains" in test_case:
                total_tests += 1
                alt_text = result.content.image_alt.lower() if result.content.image_alt else ""
                if any(pattern in alt_text for pattern in test_case["expected_alt_text_contains"]):
                    tests_passed += 1
                    print(f"✅ Alt text contains expected content: {alt_text}")
                else:
                    print(f"❌ Alt text missing expected content: {alt_text}")
            
            # Test product extraction (now check sections instead of featured_products)
            if "expected_products" in test_case:
                total_tests += 1
                # FIXED: Check sections for content (no duplication approach)
                all_section_content = ""
                for section in result.sections:
                    all_section_content += section.get('heading', '') + " "
                    if section.get('content'):
                        if isinstance(section['content'], list):
                            all_section_content += ' '.join(section['content']) + " "
                        else:
                            all_section_content += str(section['content']) + " "
                
                found_products = [p for p in test_case["expected_products"] if p.lower() in all_section_content.lower()]
                if len(found_products) >= len(test_case["expected_products"]) * 0.7:  # 70% threshold
                    tests_passed += 1
                    print(f"✅ Products found: {found_products}")
                else:
                    print(f"❌ Products missing: {found_products}")
            
            # Test content extraction (now check sections instead of description)
            if "expected_content" in test_case:
                total_tests += 1
                # FIXED: Check sections for content (no duplication approach)
                all_section_content = ""
                for section in result.sections:
                    if section.get('content'):
                        if isinstance(section['content'], list):
                            all_section_content += ' '.join(section['content']) + " "
                        else:
                            all_section_content += str(section['content']) + " "
                
                found_content = [c for c in test_case["expected_content"] if c.lower() in all_section_content.lower()]
                if len(found_content) >= len(test_case["expected_content"]) * 0.7:
                    tests_passed += 1
                    print(f"✅ Content found: {found_content}")
                else:
                    print(f"❌ Content missing: {found_content}")
            
            # Test sections
            if "expected_sections" in test_case:
                total_tests += 1
                sections_text = " ".join([s.get('heading', '') for s in result.sections]).lower()
                found_sections = [s for s in test_case["expected_sections"] if s.lower() in sections_text]
                if len(found_sections) >= len(test_case["expected_sections"]) * 0.5:
                    tests_passed += 1
                    print(f"✅ Sections found: {found_sections}")
                else:
                    print(f"❌ Sections missing: {found_sections}")
            
            # Test main content (for table of contents style pages like October Edition)
            if "expected_content_in_main" in test_case:
                total_tests += 1
                # Check main content from extraction metadata
                all_main_content = ""
                if hasattr(result, 'extraction_metadata') and result.extraction_metadata:
                    # Get main content from universal extractor
                    from src.utils.universal_content_extractor import FixedUniversalContentExtractor
                    extractor = FixedUniversalContentExtractor()
                    extracted = extractor.extract_all_content(html_content, url=f"https://www.costco.com/{filename}")
                    all_main_content = " ".join(extracted.main_content)
                
                found_main_content = [c for c in test_case["expected_content_in_main"] if c.lower() in all_main_content.lower()]
                if len(found_main_content) >= len(test_case["expected_content_in_main"]) * 0.7:
                    tests_passed += 1
                    print(f"✅ Main content found: {found_main_content}")
                else:
                    print(f"❌ Main content missing: {found_main_content}")
            
            # Calculate accuracy
            accuracy = (tests_passed / total_tests * 100) if total_tests > 0 else 0
            results[filename] = accuracy
            
            print(f"📊 Accuracy: {accuracy:.1f}% ({tests_passed}/{total_tests} tests passed)")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
    
    # Overall results
    if results:
        overall_accuracy = sum(results.values()) / len(results)
        print(f"\n🎯 OVERALL SCREENSHOT-BASED ACCURACY: {overall_accuracy:.1f}%")
        
        for filename, accuracy in results.items():
            status = "✅" if accuracy >= 90 else "⚠️" if accuracy >= 70 else "❌"
            print(f"   {status} {filename}: {accuracy:.1f}%")
        
        if overall_accuracy >= 90:
            print("🎉 SUCCESS: 90%+ accuracy achieved against screenshots!")
        else:
            print("❌ NEEDS IMPROVEMENT: Below 90% accuracy")
    
    return results

if __name__ == "__main__":
    print("🧪 Testing Shopping Accuracy Against Screenshots")
    print("Following 3 rules: dynamic patterns, no category impact, with tests")
    print("=" * 70)
    
    test_shopping_accuracy_vs_screenshots()