#!/usr/bin/env python3
"""
Enhanced Costco Connection HTML Parser - Main Entry Point
Processes Costco Connection HTML files with AI intelligence and rich schema support
"""

import logging
from pathlib import Path

from src.processors.enhanced_html_processor import EnhancedHTMLProcessor
from src.config.settings import HTML_DIRECTORY, OUTPUT_DIRECTORY, LOGGING_CONFIG


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format']
    )


def print_banner():
    """Print enhanced application banner."""
    print("🏪 Enhanced Costco Connection HTML Parser")
    print("=" * 50)
    print("🎯 Schema-Aware Content Extraction")
    print("🔍 Content Types: Recipe, Travel, Tech, Lifestyle, Editorial, Shopping, Member")
    print("🚀 AI-Powered Enhancement with AWS Bedrock Claude")
    print("=" * 50)


def main():
    """Main function to orchestrate enhanced HTML processing."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print_banner()

    # Check input directory
    if not Path(HTML_DIRECTORY).exists():
        print(f"❌ Directory '{HTML_DIRECTORY}' not found!")
        print(f"📁 Please create the directory and add your HTML files.")
        print(f"💡 Expected structure:")
        print(f"   {HTML_DIRECTORY}/")
        print(f"   ├── connection-recipe-*.html")
        print(f"   ├── connection-travel-*.html") 
        print(f"   ├── connection-tech-*.html")
        print(f"   └── ...")
        return

    # Initialize enhanced processor
    processor = EnhancedHTMLProcessor()
    html_files = processor.find_files(HTML_DIRECTORY)

    if not html_files:
        print(f"❌ No HTML files found in {HTML_DIRECTORY}")
        print(f"💡 Make sure your files have .html or .htm extensions")
        return

    print(f"📁 Found {len(html_files)} HTML files")

    # Show sample files with content type prediction
    print(f"\n📋 Sample Files Preview:")
    for i, file_path in enumerate(html_files[:5]):
        content_type_hint = _predict_content_type_from_filename(file_path.name)
        print(f"   {i+1}. {file_path.name} → {content_type_hint}")
    if len(html_files) > 5:
        print(f"   ... and {len(html_files) - 5} more files")

    print(f"\n🎯 Enhanced Processing Features:")
    print(f"   ✅ Schema-aware content extraction")
    print(f"   ✅ Content type auto-detection") 
    print(f"   ✅ AI-powered enhancement")
    print(f"   ✅ Quality scoring")
    print(f"   ✅ Multi-format JSON export")

    # Confirm processing
    print(f"\n" + "="*50)
    confirm = input(f"🚀 Process {len(html_files)} files with enhanced extraction? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Processing cancelled")
        return

    # Process files with enhanced extraction
    try:
        print("🔄 Starting enhanced processing...")
        print("⏳ This may take a while due to AI enhancement...")
        
        results = processor.process_all(html_files)
        
        if results:
            print(f"\n💾 Saving enhanced results...")
            processor.save_enhanced_results(results, OUTPUT_DIRECTORY)
            
            # Display enhanced final statistics
            stats = processor.get_enhanced_processing_stats()
            print(f"\n🎉 PROCESSING COMPLETE!")
            print("=" * 50)
            print(f"✅ Success Rate: {stats['successful']}/{stats['processed']} ({(stats['successful']/stats['processed']*100):.1f}%)")
            
            if 'average_quality' in stats:
                print(f"📈 Average Quality: {stats['average_quality']:.1f}/100")
                
            if 'content_types' in stats:
                print(f"📊 Content Types Found:")
                for content_type, count in stats['content_types'].items():
                    print(f"   {content_type.upper()}: {count} articles")
            
            if stats['failed_files']:
                print(f"⚠️ Failed Files: {len(stats['failed_files'])}")
                
            print(f"\n📁 Results saved to:")
            print(f"   📄 Main: {OUTPUT_DIRECTORY}/enhanced_results.json")
            print(f"   📊 Stats: {OUTPUT_DIRECTORY}/processing_statistics.json")
            print(f"   📋 By Type: {OUTPUT_DIRECTORY}/*_articles.json")
            
        else:
            print("❌ No files were processed successfully")
            print("💡 Check your AWS credentials and HTML file format")

    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
        print("💾 Partial results may have been saved")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Unexpected error during enhanced processing")
        print("💡 Check logs for detailed error information")


def _predict_content_type_from_filename(filename: str) -> str:
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


if __name__ == "__main__":
    main()