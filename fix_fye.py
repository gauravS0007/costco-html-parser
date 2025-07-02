#!/usr/bin/env python3
"""
Fix FYE file processing with improved lifestyle detection
"""
import sys
import os
sys.path.append('.')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor
import json

def fix_fye_processing():
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Load the original files to re-process
    input_files = [
        'data/results/For Your Entertainment // AUTHOR SPOTLIGHT - Strong women.html',
        'data/results/Inside Costco - Supplier Spotlight_Pets and the planet.html',
        'data/results/Costco Life - Celebrate, your way.html'
    ]
    
    results = []
    
    for file_path in input_files:
        if os.path.exists(file_path):
            print(f"Processing {file_path}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Create URL based on filename
            filename = os.path.basename(file_path)
            if 'Strong women' in filename:
                url = "https://www.costco.com/October-Edition- --Costco.html"
            elif 'Pets and the planet' in filename:
                url = "https://www.costco.com/Inside-Costco---Supplier-Spotlight-Pets-and-the-planet.html"
            else:
                url = "https://www.costco.com/Costco-Life---Celebrate-your-way.html"
            
            # Process with enhanced processor
            result = processor.process_content(html_content, url, filename)
            
            if result:
                results.append(result.to_dict())
                print(f"✅ Processed {filename}: {result.content_type}")
                
                # Check sections and images
                sections = result.to_dict().get('sections', [])
                total_images = sum(len(s.get('images', [])) for s in sections)
                print(f"   Sections: {len(sections)}, Images in sections: {total_images}")
            else:
                print(f"❌ Failed to process {filename}")
    
    # Save updated results
    if results:
        with open('data/results/lifestyle_fixes.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"✅ Saved {len(results)} fixed results to lifestyle_fixes.json")

if __name__ == "__main__":
    fix_fye_processing()