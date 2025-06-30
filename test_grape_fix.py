#!/usr/bin/env python3

import sys
import os
import json
sys.path.append('/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_grape_crumble():
    # Create processor
    processor = FixedSuperEnhancedCostcoProcessor()
    
    # Read grape crumble HTML 
    html_files_dir = '/Users/apple/Desktop/Python/costco-html-parser/data/html_files'
    
    # Find the grape crumble file
    for filename in os.listdir(html_files_dir):
        if 'grape' in filename.lower() and 'crumble' in filename.lower():
            filepath = os.path.join(html_files_dir, filename)
            print(f"Processing: {filename}")
            
            with open(filepath, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Process it
            result = processor.process_content(html_content, 'grape-crumble-test', filename)
            
            if result and hasattr(result.content, 'instructions'):
                instructions = result.content.instructions
                print(f'\nGrape Crumble - Instructions count: {len(instructions)}')
                for i, instruction in enumerate(instructions, 1):
                    if len(instruction) > 400:
                        print(f'⚠️  MEGA-INSTRUCTION STILL FOUND:')
                        print(f'Instruction {i} (length: {len(instruction)}): {instruction[:200]}...')
                        return False
                    else:
                        print(f'✅ Instruction {i}: {instruction}')
                print("\n🎉 SUCCESS: No mega-instruction found!")
                return True
            else:
                print('❌ No instructions found or processing failed')
                return False
    
    print('❌ Grape Crumble file not found')
    return False

if __name__ == "__main__":
    test_grape_crumble()