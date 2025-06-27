#!/usr/bin/env python3
"""
Costco Connection HTML Parser - Main Entry Point
Processes Costco Connection HTML files with AI intelligence
"""

import logging
from pathlib import Path

from src.processors.html_processor import HTMLProcessor
from src.config.settings import HTML_DIRECTORY, OUTPUT_DIRECTORY, LOGGING_CONFIG


def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=getattr(logging, LOGGING_CONFIG['level']),
        format=LOGGING_CONFIG['format']
    )


def main():
    """Main function to orchestrate HTML processing."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🏪 Costco Connection HTML Parser")
    print("=" * 40)

    # Check input directory
    if not Path(HTML_DIRECTORY).exists():
        print(f"❌ Directory '{HTML_DIRECTORY}' not found!")
        print(f"Please create the directory and add your HTML files.")
        return

    # Initialize processor
    processor = HTMLProcessor()
    html_files = processor.find_files(HTML_DIRECTORY)

    if not html_files:
        print(f"❌ No HTML files found in {HTML_DIRECTORY}")
        return

    print(f"📁 Found {len(html_files)} HTML files")

    # Show sample files
    for i, file_path in enumerate(html_files[:3]):
        print(f"   {i+1}. {file_path.name}")
    if len(html_files) > 3:
        print(f"   ... and {len(html_files) - 3} more files")

    # Confirm processing
    confirm = input(f"\nProcess {len(html_files)} files? (y/n): ").lower()
    if confirm != 'y':
        print("❌ Processing cancelled")
        return

    # Process files
    try:
        print("🚀 Starting processing...")
        results = processor.process_all(html_files)
        
        if results:
            processor.save_results(results, OUTPUT_DIRECTORY)
            
            # Display final statistics
            stats = processor.get_processing_stats()
            print(f"\n📊 Processing Complete!")
            print(f"✅ Successful: {stats['successful']}/{stats['processed']}")
            if 'average_quality' in stats:
                print(f"📈 Average quality: {stats['average_quality']:.1f}/100")
            
            if stats['failed_files']:
                print(f"⚠️ Failed files: {len(stats['failed_files'])}")
        else:
            print("❌ No files were processed successfully")

    except KeyboardInterrupt:
        print("\n⚠️ Processing interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        logger.exception("Unexpected error during processing")


if __name__ == "__main__":
    main()