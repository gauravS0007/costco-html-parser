#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.universal_content_extractor import FixedUniversalContentExtractor

def debug_fun_times_content():
    """Debug the full content of Fun times for all section"""
    
    html_file = "data/html_files/Costco Life - Celebrate, your way.html"
    
    if os.path.exists(html_file):
        print(f"🔍 Debugging Fun times for all content: {html_file}")
        
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        extractor = FixedUniversalContentExtractor()
        
        # Run the actual extraction process 
        result = extractor.extract_all_content(html_content, html_file)
        
        print(f"\n📊 'FUN TIMES FOR ALL' SECTION CONTENT:")
        
        fun_times_section = None
        for heading in result.headings:
            if heading.get('text') == 'Fun times for all':
                fun_times_section = heading
                break
        
        if fun_times_section:
            content = fun_times_section.get('content', [])
            print(f"Content items: {len(content)}")
            
            for i, text in enumerate(content):
                print(f"\nContent {i+1}:")
                print(f"  {text}")
                
                # Check if this content mentions other sections
                if 'glasses' in text.lower():
                    print("  ⚠️  CONTAINS GLASSES CONTENT!")
                if 'card' in text.lower():
                    print("  ⚠️  CONTAINS CARD CONTENT!")  
                if 'rollup' in text.lower() or 'lasagna' in text.lower():
                    print("  ⚠️  CONTAINS ROLLUPS CONTENT!")
        else:
            print("❌ Fun times for all section not found")
    
    else:
        print(f"❌ File not found: {html_file}")

if __name__ == "__main__":
    debug_fun_times_content()