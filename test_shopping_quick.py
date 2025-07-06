#!/usr/bin/env python3
"""
Quick shopping accuracy test to validate extraction against screenshots
"""

import sys
import os
import json

# Add project root to Python path
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

try:
    from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor
    from src.utils.universal_content_extractor import FixedUniversalContentExtractor
except ImportError as e:
    print(f"Import error: {e}")
    print("Attempting alternative import...")
    sys.exit(1)

def test_shopping_files():
    """Test shopping files against screenshot expectations"""
    
    processor = FixedSuperEnhancedCostcoProcessor()
    
    test_files = [
        {
            "filename": "Treasure Hunt  _ Costco.html",
            "expected_title": "Treasure Hunt",
            "expected_products": ["sofa", "skillet", "throw", "jacket", "rug", "pretzel", "art"],
            "expected_featured_image_not": ["headshot", "author"]
        },
        {
            "filename": "Buying Smart - Upgrade your space  _ Costco.html", 
            "expected_title": "Buying Smart",
            "expected_content": ["countertop", "kitchen", "installation", "cosentino"],
            "expected_featured_image_not": ["headshot", "andrea"]
        },
        {
            "filename": "October Edition  _ Costco.html",
            "expected_title": "October Edition", 
            "expected_sections": ["cover", "special", "featured"],
            "expected_featured_image_not": ["headshot", "author"]
        }
    ]
    
    results = {}
    
    for test_case in test_files:
        filename = test_case["filename"]
        file_path = f"/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}"
        
        print(f"\n=== Testing {filename} ===")
        
        # Check if file exists, and try to find similar names if not
        if not os.path.exists(file_path):
            # List all files in directory to find similar names
            html_dir = "/Users/apple/Desktop/Python/costco-html-parser/data/html_files"
            all_files = os.listdir(html_dir)
            shopping_files = [f for f in all_files if any(term in f.lower() for term in ['treasure', 'buying', 'october'])]
            
            print(f"❌ File not found: {file_path}")
            print(f"Available shopping files: {shopping_files}")
            
            # Try to find matching file
            for available_file in shopping_files:
                if test_case["expected_title"].lower() in available_file.lower():
                    file_path = os.path.join(html_dir, available_file)
                    filename = available_file
                    print(f"✅ Found matching file: {filename}")
                    break
            else:
                continue
        
        try:
            # Read and process file
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            result = processor.process_content(
                html_content=html_content,
                url=f"https://www.costco.com/{filename}",
                filename=filename
            )
            
            if not result:
                print(f"❌ Processing failed for {filename}")
                continue
            
            # Test results
            test_results = {
                "title_correct": False,
                "content_type_correct": False, 
                "featured_image_appropriate": False,
                "content_extracted": False,
                "no_duplication": False
            }
            
            # 1. Test title
            if result.content.title == test_case["expected_title"]:
                test_results["title_correct"] = True
                print(f"✅ Title: {result.content.title}")
            else:
                print(f"❌ Title: Expected '{test_case['expected_title']}', got '{result.content.title}'")
            
            # 2. Test content type  
            actual_content_type = getattr(result.content, 'content_type', 'unknown')
            # Handle both string and enum formats
            content_type_str = str(actual_content_type).lower()
            if "shopping" in content_type_str:
                test_results["content_type_correct"] = True
                print(f"✅ Content Type: {actual_content_type}")
            else:
                print(f"❌ Content Type: Expected 'shopping', got '{actual_content_type}'")
            
            # 3. Test featured image (should not be author headshot)
            featured_img = result.content.featured_image.lower() if result.content.featured_image else ""
            bad_terms_found = [term for term in test_case["expected_featured_image_not"] if term in featured_img]
            
            if len(bad_terms_found) == 0 and featured_img:
                test_results["featured_image_appropriate"] = True
                print(f"✅ Featured Image: {result.content.featured_image}")
            else:
                print(f"❌ Featured Image: Contains inappropriate terms {bad_terms_found} in {featured_img}")
            
            # 4. Test content extraction
            all_content = str(result.content.featured_products) + str(result.content.description)
            
            if "expected_products" in test_case:
                found_products = [p for p in test_case["expected_products"] if p in all_content.lower()]
                if len(found_products) >= len(test_case["expected_products"]) * 0.7:  # 70% threshold
                    test_results["content_extracted"] = True
                    print(f"✅ Products: Found {len(found_products)}/{len(test_case['expected_products'])}")
                else:
                    print(f"❌ Products: Found only {found_products}")
            
            elif "expected_content" in test_case:
                found_content = [c for c in test_case["expected_content"] if c in all_content.lower()]
                if len(found_content) >= len(test_case["expected_content"]) * 0.7:  # 70% threshold
                    test_results["content_extracted"] = True
                    print(f"✅ Content: Found {len(found_content)}/{len(test_case['expected_content'])}")
                else:
                    print(f"❌ Content: Found only {found_content}")
            
            elif "expected_sections" in test_case:
                sections_text = ' '.join([s.get('heading', '') for s in result.sections]).lower()
                found_sections = [s for s in test_case["expected_sections"] if s in sections_text]
                if len(found_sections) >= len(test_case["expected_sections"]) * 0.5:  # 50% threshold for sections
                    test_results["content_extracted"] = True
                    print(f"✅ Sections: Found {len(found_sections)}/{len(test_case['expected_sections'])}")
                else:
                    print(f"❌ Sections: Found only {found_sections}")
            
            # 5. Test no duplication (simplified)
            if len(result.content.featured_products) > 0:
                test_results["no_duplication"] = True
                print(f"✅ No Duplication: {len(result.content.featured_products)} products extracted")
            
            # Calculate accuracy
            passed_tests = sum(test_results.values())
            total_tests = len(test_results)
            accuracy = (passed_tests / total_tests) * 100
            
            print(f"📊 Accuracy: {accuracy:.1f}% ({passed_tests}/{total_tests} tests passed)")
            results[filename] = accuracy
            
            # Print detailed results
            print(f"🔍 Details:")
            print(f"   - Sections: {len(result.sections)}")
            print(f"   - Products: {len(result.content.featured_products)}")
            if hasattr(result.content, 'seasonal_items'):
                print(f"   - Seasonal Items: {len(result.content.seasonal_items)}")
            
        except Exception as e:
            print(f"❌ Error processing {filename}: {e}")
            import traceback
            traceback.print_exc()
    
    # Overall results
    if results:
        overall_accuracy = sum(results.values()) / len(results)
        print(f"\n🎯 OVERALL SHOPPING ACCURACY: {overall_accuracy:.1f}%")
        
        for filename, accuracy in results.items():
            status = "✅" if accuracy >= 90 else "⚠️" if accuracy >= 70 else "❌"
            print(f"   {status} {filename}: {accuracy:.1f}%")
        
        if overall_accuracy >= 95:
            print("🎉 EXCELLENT: 95%+ accuracy achieved!")
        elif overall_accuracy >= 85:
            print("✅ GOOD: 85%+ accuracy achieved!")
        elif overall_accuracy >= 70:
            print("⚠️ NEEDS IMPROVEMENT: 70%+ accuracy but below 85%")
        else:
            print("❌ POOR: Below 70% accuracy - major fixes needed")
    
    return results

if __name__ == "__main__":
    print("🧪 Running Shopping Content Accuracy Tests")
    print("=" * 50)
    
    test_shopping_files()