#!/usr/bin/env python3

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor
import os

def test_strong_women_fixes():
    """Test the fixes for Strong Women content extraction"""
    
    # Get the file
    files_dir = "data/html_files/"
    strong_women_file = None
    
    # Find the file with correct spacing
    for filename in os.listdir(files_dir):
        if "strong women" in filename.lower():
            strong_women_file = os.path.join(files_dir, filename)
            break
    
    if not strong_women_file or not os.path.exists(strong_women_file):
        print("❌ Strong women file not found")
        print("Available files:")
        for f in os.listdir(files_dir):
            if 'fye' in f.lower():
                print(f"  {f}")
        return
    
    # Read the file
    with open(strong_women_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    print(f"📄 Processing {strong_women_file}")
    print(f"   File size: {len(html_content)} characters")
    
    # Process it
    processor = FixedSuperEnhancedCostcoProcessor()
    result = processor.process_content(
        html_content, 
        'https://www.costco.com/FYE---Strong-women- --Costco.html', 
        'strong_women.html'
    )
    
    if not result:
        print("❌ No result returned from processor")
        return
    
    # Test fixes
    print("\n🔍 TESTING FIXES:")
    
    # Test 1: Title Extraction
    content = result.content
    title = getattr(content, 'title', 'Not found')
    print(f"\n1️⃣ TITLE TEST:")
    print(f"   Extracted title: '{title}'")
    
    # Debug: Check if title enhancement was attempted
    import re
    has_spotlight_pattern = bool(re.match(r'.*//.*spotlight', title.lower()))
    print(f"   Debug: Has spotlight pattern: {has_spotlight_pattern}")
    
    if 'Strong women' in title:
        print("   ✅ TITLE FIX WORKING - Contains 'Strong women'")
    elif 'For Your Entertainment' in title:
        print("   ❌ TITLE FIX FAILED - Still showing section header")
    else:
        print(f"   ⚠️  TITLE UNCLEAR - Got: {title}")
    
    # Test 2: Q&A Formatting
    sections = result.sections
    print(f"\n2️⃣ Q&A FORMATTING TEST:")
    qa_found = False
    qa_properly_formatted = False
    
    for i, section in enumerate(sections):
        heading = section.get('heading', '')
        content_items = section.get('content', [])
        
        for content_item in content_items:
            if 'Costco Connection' in content_item and 'Karin Smirnoff' in content_item:
                qa_found = True
                print(f"   Found Q&A in section {i}: '{heading}'")
                print(f"   Q&A preview: {content_item[:100]}...")
                
                # Debug: Check Q&A pattern detection
                import re
                qa_patterns = [
                    r'Costco Connection\s+[A-Z]',
                    r'\bCC\s+[A-Z]',  
                    r'[A-Z][a-z]+ [A-Z][a-z]+\s+[A-Z]'
                ]
                pattern_found = any(re.search(pattern, content_item) for pattern in qa_patterns)
                print(f"   Debug: Q&A pattern detected: {pattern_found}")
                
                # Check if properly formatted with Q: and A: structure
                if 'Q: ' in content_item and 'A: ' in content_item:
                    qa_properly_formatted = True
                    print("   ✅ Q&A FORMATTING FIX WORKING")
                    print(f"   Formatted content preview: {content_item[:200]}...")
                else:
                    print("   ❌ Q&A FORMATTING STILL BROKEN")
                    print(f"   Raw content: {content_item[:200]}...")
                
                # Check all content items for formatted Q&A
                print(f"   \nChecking all {len(content_items)} content items for Q&A formatting...")
                for idx, item in enumerate(content_items):
                    if 'Q: ' in str(item) and 'A: ' in str(item):
                        print(f"   Found formatted Q&A in content item {idx}:")
                        print(f"   {str(item)[:300]}...")
                        qa_properly_formatted = True
                break
    
    if not qa_found:
        print("   ⚠️  Q&A content not found")
    
    # Test 3: Image Distribution  
    print(f"\n3️⃣ IMAGE DISTRIBUTION TEST:")
    total_images = 0
    book_images_distributed = False
    
    for i, section in enumerate(sections):
        heading = section.get('heading', '')
        images = section.get('images', [])
        total_images += len(images)
        
        if images:
            print(f"   Section {i} '{heading}': {len(images)} images")
            for img in images:
                src = img.get('src', '')
                alt = img.get('alt', '')
                print(f"     - {alt}: {src.split('/')[-1] if src else 'no src'}")
                
                # Check if book images are in appropriate sections
                if 'book' in alt.lower() or 'bookpick' in src:
                    if 'online book pick' in heading.lower() or 'pick' in heading.lower():
                        book_images_distributed = True
                        print("       ✅ Book image in appropriate section")
    
    print(f"   Total images found: {total_images}")
    
    if book_images_distributed:
        print("   ✅ IMAGE DISTRIBUTION FIX WORKING")
    else:
        print("   ❌ IMAGE DISTRIBUTION STILL NEEDS WORK")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    title_fixed = 'Strong women' in title
    qa_fixed = qa_properly_formatted
    img_fixed = book_images_distributed
    
    fixes_working = sum([title_fixed, qa_fixed, img_fixed])
    print(f"   Fixes working: {fixes_working}/3")
    
    if fixes_working == 3:
        print("   🎉 ALL FIXES WORKING!")
    elif fixes_working >= 2:
        print("   👍 MOST FIXES WORKING")  
    else:
        print("   ⚠️  MORE WORK NEEDED")
    
    return result

if __name__ == "__main__":
    test_strong_women_fixes()