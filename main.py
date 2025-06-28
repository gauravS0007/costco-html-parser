#!/usr/bin/env python3
"""
FIXED: Enhanced Costco Connection HTML Parser - Main Entry Point
Processes Costco Connection HTML files with AI intelligence and rich schema support
"""

import logging
import json
import time
from pathlib import Path
from dataclasses import asdict

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor
from src.config.settings import HTML_DIRECTORY, OUTPUT_DIRECTORY, LOGGING_CONFIG


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format']
    )


def find_html_files(directory: str):
    """Find HTML files in the specified directory."""
    html_files = []
    path = Path(directory)
    
    if not path.exists():
        print(f"❌ Directory '{directory}' not found!")
        return html_files
        
    for pattern in ['*.html', '*.htm']:
        html_files.extend(path.glob(pattern))
        
    print(f"📁 Found {len(html_files)} HTML files in {directory}")
    return html_files


def extract_url(file_path: Path) -> str:
    """Extract URL from filename."""
    filename = file_path.stem
    clean_name = filename.replace('_', '-').replace(' ', '-')
    return f"https://www.costco.com/{clean_name}.html"


def predict_content_type_from_filename(filename: str) -> str:
    """Predict content type from filename for preview."""
    filename_lower = filename.lower()
    
    if 'recipe' in filename_lower:
        return "🍳 RECIPE"
    elif 'travel' in filename_lower:
        return "✈️ TRAVEL"
    elif 'tech' in filename_lower or 'power-up' in filename_lower:
        return "💻 TECH"
    elif 'costco-life' in filename_lower or 'lifestyle' in filename_lower:
        return "🏠 LIFESTYLE"
    elif 'publisher' in filename_lower or 'editorial' in filename_lower:
        return "📝 EDITORIAL"
    elif 'buying' in filename_lower or 'treasure' in filename_lower:
        return "🛍️ SHOPPING"
    elif 'member' in filename_lower or 'poll' in filename_lower:
        return "👥 MEMBER"
    else:
        return "📄 GENERAL"


def process_single_file(processor, file_path: Path, file_num: int, total_files: int):
    """Process a single HTML file."""
    try:
        print(f"\n🔄 Processing {file_num}/{total_files}: {file_path.name}")

        # Read file
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        if len(html_content) < 500:
            print(f"⚠️ File too small: {file_path.name}")
            return None

        # Process with fixed processor
        url = extract_url(file_path)
        result = processor.process_content(html_content, url, file_path.name)
        
        if result:
            print(f"✅ Success: {result.content.title}")
            print(f"   Type: {result.content.content_type.value}")
            print(f"   Quality: {result.content_quality_score}/100")
            print(f"   Image: {'✅' if result.content.featured_image else '❌'}")
            
            # Show recipe-specific details
            if result.content.content_type.value == 'recipe':
                ingredients_count = len(result.content.ingredients) if result.content.ingredients else 0
                instructions_count = len(result.content.instructions) if result.content.instructions else 0
                print(f"   🍳 Ingredients: {ingredients_count}")
                print(f"   📝 Instructions: {instructions_count}")
                print(f"   👤 Byline: {result.content.byline}")
                
                # Show first few ingredients for verification
                if result.content.ingredients and len(result.content.ingredients) > 0:
                    print(f"   📋 Sample ingredients:")
                    for i, ing in enumerate(result.content.ingredients[:3]):
                        if not ing.startswith('==='):  # Skip section headers
                            print(f"      • {ing}")
                        if i >= 2:  # Only show first 3
                            break
            
            return result
        else:
            print(f"❌ Failed to process {file_path.name}")
            return None
            
    except Exception as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return None


def save_results(results, output_dir: str):
    """Save processing results to JSON file."""
    if not results:
        print("⚠️ No results to save")
        return

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Convert to JSON-serializable format
    json_data = []
    
    for result in results:
        # Convert content schema to dict
        content_dict = asdict(result.content)
        
        # Convert enums to strings
        if 'content_type' in content_dict:
            content_dict['content_type'] = content_dict['content_type'].value
        
        # Build enhanced JSON structure
        enhanced_data = {
            'url': result.url,
            'content_type': result.content.content_type.value,
            'meta_title': result.meta_title,
            'meta_description': result.meta_description,
            'content': content_dict,
            'sections': result.sections,
            'related_articles': result.related_articles,
            'quality_score': result.content_quality_score,
            'extraction_metadata': result.extraction_metadata
        }
        
        json_data.append(enhanced_data)

    # Save main file
    main_file = output_path / "enhanced_results_fixed.json"
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"💾 Results saved to {main_file}")

    # Save statistics
    stats = calculate_processing_stats(results)
    stats_file = output_path / "processing_statistics_fixed.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    print(f"📊 Statistics saved to {stats_file}")


def calculate_processing_stats(results):
    """Calculate processing statistics."""
    
    stats = {
        'total_processed': len(results),
        'average_quality': sum(r.content_quality_score for r in results) / len(results) if results else 0,
        'content_type_distribution': {},
        'quality_distribution': {'excellent (90-100)': 0, 'good (70-89)': 0, 'fair (50-69)': 0, 'poor (0-49)': 0},
        'recipe_analysis': {
            'total_recipes': 0,
            'recipes_with_ingredients': 0,
            'recipes_with_instructions': 0,
            'average_ingredients_count': 0,
            'average_instructions_count': 0
        }
    }
    
    # Content type distribution
    for result in results:
        content_type = result.content.content_type.value
        stats['content_type_distribution'][content_type] = stats['content_type_distribution'].get(content_type, 0) + 1
    
    # Quality distribution
    for result in results:
        score = result.content_quality_score
        if score >= 90:
            stats['quality_distribution']['excellent (90-100)'] += 1
        elif score >= 70:
            stats['quality_distribution']['good (70-89)'] += 1
        elif score >= 50:
            stats['quality_distribution']['fair (50-69)'] += 1
        else:
            stats['quality_distribution']['poor (0-49)'] += 1
    
    # Recipe-specific analysis
    recipe_results = [r for r in results if r.content.content_type.value == 'recipe']
    stats['recipe_analysis']['total_recipes'] = len(recipe_results)
    
    if recipe_results:
        ingredients_counts = []
        instructions_counts = []
        
        for result in recipe_results:
            if hasattr(result.content, 'ingredients') and result.content.ingredients:
                stats['recipe_analysis']['recipes_with_ingredients'] += 1
                # Count non-section-header ingredients
                ingredient_count = len([ing for ing in result.content.ingredients if not ing.startswith('===')])
                ingredients_counts.append(ingredient_count)
            
            if hasattr(result.content, 'instructions') and result.content.instructions:
                stats['recipe_analysis']['recipes_with_instructions'] += 1
                instruction_count = len([inst for inst in result.content.instructions if not inst.startswith('===')])
                instructions_counts.append(instruction_count)
        
        if ingredients_counts:
            stats['recipe_analysis']['average_ingredients_count'] = sum(ingredients_counts) / len(ingredients_counts)
        if instructions_counts:
            stats['recipe_analysis']['average_instructions_count'] = sum(instructions_counts) / len(instructions_counts)
    
    return stats


def print_banner():
    """Print enhanced application banner."""
    print("🔧 FIXED Costco Connection HTML Parser")
    print("=" * 60)
    print("🎯 Section-Aware Recipe Extraction")
    print("🔍 Content Types: Recipe, Travel, Tech, Lifestyle, Editorial, Shopping, Member")
    print("🚀 Conservative AI Enhancement with AWS Bedrock Claude")
    print("✨ Proper Ingredient/Instruction Detection")
    print("🛡️ Smart Filtering (removes nav, footer, ads, cookies)")
    print("=" * 60)


def main():
    """Main function to orchestrate FIXED HTML processing."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print_banner()

    # Check input directory
    if not Path(HTML_DIRECTORY).exists():
        print(f"❌ Directory '{HTML_DIRECTORY}' not found!")
        print(f"📁 Please create the directory and add your HTML files.")
        return

    # Initialize FIXED processor
    processor = FixedSuperEnhancedCostcoProcessor()
    html_files = find_html_files(HTML_DIRECTORY)

    if not html_files:
        print(f"❌ No HTML files found in {HTML_DIRECTORY}")
        return

    # Show sample files with content type prediction
    print(f"\n📋 Sample Files Preview:")
    for i, file_path in enumerate(html_files[:5]):
        content_type_hint = predict_content_type_from_filename(file_path.name)
        print(f"   {i+1}. {file_path.name} → {content_type_hint}")
    if len(html_files) > 5:
        print(f"   ... and {len(html_files) - 5} more files")

    print(f"\n🎯 FIXED Processing Features:")
    print(f"   ✅ Section-aware recipe extraction (FILLING, STREUSEL, CAKE)")
    print(f"   ✅ Conservative AI enhancement (only fills gaps)")
    print(f"   ✅ Accurate ingredient/instruction detection") 
    print(f"   ✅ Real byline extraction (no more 'Lotions & Creams')")
    print(f"   ✅ Multi-section recipe support")
    print(f"   ✅ Comprehensive quality scoring")

    # Confirm processing
    print(f"\n" + "="*50)
    confirm = input(f"🚀 Process {len(html_files)} files with FIXED extraction? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Processing cancelled")
        return

    # Process files
    try:
        print("🔄 Starting FIXED processing...")
        
        results = []
        start_time = time.time()
        
        for i, file_path in enumerate(html_files):
            result = process_single_file(processor, file_path, i+1, len(html_files))
            if result:
                results.append(result)
            
            # Small delay to be respectful to AI service
            time.sleep(1)
        
        processing_time = time.time() - start_time
        
        if results:
            print(f"\n💾 Saving FIXED results...")
            save_results(results, OUTPUT_DIRECTORY)
            
            # Display enhanced final statistics
            print(f"\n🎉 FIXED PROCESSING COMPLETE!")
            print("=" * 50)
            print(f"✅ Success Rate: {len(results)}/{len(html_files)} ({(len(results)/len(html_files)*100):.1f}%)")
            print(f"⏱️ Processing Time: {processing_time:.1f} seconds")
            
            if results:
                avg_quality = sum(r.content_quality_score for r in results) / len(results)
                print(f"📈 Average Quality: {avg_quality:.1f}/100")
                
                # Content type breakdown
                content_types = {}
                for result in results:
                    ct = result.content.content_type.value
                    content_types[ct] = content_types.get(ct, 0) + 1
                
                print(f"📊 Content Types Found:")
                for content_type, count in sorted(content_types.items()):
                    print(f"   {content_type.upper()}: {count} articles")
                
                # Recipe-specific stats
                recipe_results = [r for r in results if r.content.content_type.value == 'recipe']
                if recipe_results:
                    print(f"\n🍳 Recipe Extraction Analysis:")
                    print(f"   Total Recipes: {len(recipe_results)}")
                    
                    with_ingredients = sum(1 for r in recipe_results if hasattr(r.content, 'ingredients') and r.content.ingredients)
                    with_instructions = sum(1 for r in recipe_results if hasattr(r.content, 'instructions') and r.content.instructions)
                    
                    print(f"   With Ingredients: {with_ingredients}/{len(recipe_results)}")
                    print(f"   With Instructions: {with_instructions}/{len(recipe_results)}")
                    
                    if with_ingredients > 0:
                        avg_ingredients = sum(len([ing for ing in r.content.ingredients if not ing.startswith('===')]) 
                                            for r in recipe_results if hasattr(r.content, 'ingredients') and r.content.ingredients) / with_ingredients
                        print(f"   Avg Ingredients per Recipe: {avg_ingredients:.1f}")
            
            print(f"\n📁 Results saved to:")
            print(f"   📄 Main: {OUTPUT_DIRECTORY}/enhanced_results_fixed.json")
            print(f"   📊 Stats: {OUTPUT_DIRECTORY}/processing_statistics_fixed.json")
            
        else:
            print("❌ No files were processed successfully")

    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Unexpected error during FIXED processing")


if __name__ == "__main__":
    main()