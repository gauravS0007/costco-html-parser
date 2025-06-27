"""
HTML file processor for batch processing of Costco HTML files.
"""

import json
import time
import hashlib
import logging
from pathlib import Path
from typing import List, Optional
from dataclasses import asdict

from ..models.components import BannerComponent, HeadlineComponent, TeaserComponent, PageStructure
from ..processors.costco_processor import CostcoProcessor
from ..config.settings import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class HTMLProcessor:
    """Main HTML file processor for batch operations."""

    def __init__(self):
        """Initialize processor with statistics tracking."""
        self.processor = CostcoProcessor()
        self.stats = {
            'processed': 0,
            'successful': 0,
            'quality_scores': [],
            'failed_files': []
        }

    def find_files(self, directory: str) -> List[Path]:
        """
        Find HTML files in the specified directory.
        
        Args:
            directory: Directory path to search
            
        Returns:
            List of Path objects for HTML files
        """
        html_files = []
        path = Path(directory)
        
        if not path.exists():
            logger.error(f"Directory does not exist: {directory}")
            return html_files
            
        for pattern in SUPPORTED_EXTENSIONS:
            html_files.extend(path.glob(pattern))
            
        logger.info(f"Found {len(html_files)} HTML files in {directory}")
        return html_files

    def extract_url(self, file_path: Path) -> str:
        """
        Extract URL from filename.
        
        Args:
            file_path: Path to the HTML file
            
        Returns:
            Constructed URL
        """
        filename = file_path.stem
        clean_name = filename.replace('_', '-').replace(' ', '-')
        return f"https://www.costco.com/{clean_name}.html"

    def process_file(self, file_path: Path) -> Optional[PageStructure]:
        """
        Process a single HTML file.
        
        Args:
            file_path: Path to the HTML file to process
            
        Returns:
            PageStructure object or None if processing failed
        """
        try:
            logger.info(f"Processing: {file_path.name}")

            # Read and validate file
            html_content = self._read_file(file_path)
            if not html_content:
                return None

            # Process with AI
            url = self.extract_url(file_path)
            ai_result = self._process_with_ai(html_content, url, file_path.name)
            if not ai_result:
                return None

            # Build page structure
            page_structure = self._build_page_structure(ai_result, url)
            
            # Update statistics
            self._update_stats(page_structure, file_path.name)
            
            return page_structure

        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {e}")
            self.stats['failed_files'].append(file_path.name)
            return None
        finally:
            self.stats['processed'] += 1

    def _read_file(self, file_path: Path) -> Optional[str]:
        """Read and validate HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            if len(html_content) < 500:
                logger.warning(f"File too small: {file_path.name}")
                return None
                
            return html_content
            
        except Exception as e:
            logger.error(f"Failed to read file {file_path.name}: {e}")
            return None

    def _process_with_ai(self, html_content: str, url: str, filename: str) -> Optional[dict]:
        """Process content with AI."""
        prompt = self.processor.create_ai_prompt(html_content, url, filename)
        ai_result = self.processor.call_ai(prompt)

        if not ai_result:
            logger.error(f"AI processing failed for {filename}")
            return None
            
        return ai_result

    def _build_page_structure(self, ai_result: dict, url: str) -> PageStructure:
        """Build PageStructure from AI result."""
        # Build banner component
        banner_data = ai_result.get('banner', {})
        banner = BannerComponent(
            title=banner_data.get('title', ''),
            url=banner_data.get('url', ''),
            alt=banner_data.get('alt', ''),
            headline=banner_data.get('headline', ''),
            byline=banner_data.get('byline', ''),
            description=banner_data.get('description', '')
        )

        # Build headlines
        headlines = []
        for h in ai_result.get('headlines', []):
            headlines.append(HeadlineComponent(
                headline_text=h.get('headline_text', ''),
                level=h.get('level', 1),
                color="black"
            ))

        # Build teasers
        teasers = []
        for t in ai_result.get('teasers', []):
            teasers.append(TeaserComponent(
                title=t.get('title', ''),
                description=t.get('description', ''),
                image=t.get('image', ''),
                alt_text=t.get('alt_text', ''),
                display_type="compact"
            ))

        # Calculate quality score
        quality = self._calculate_quality_score(banner, headlines)

        # Build metadata
        metadata = {
            'extraction_timestamp': time.time(),
            'url_hash': hashlib.md5(url.encode()).hexdigest(),
            'component_counts': {
                'headlines': len(headlines), 
                'teasers': len(teasers)
            },
            'quality_score': quality,
            'extraction_method': 'costco_ai'
        }

        return PageStructure(
            url=url,
            banner=banner,
            headlines=headlines,
            teasers=teasers,
            metadata=metadata
        )

    def _calculate_quality_score(self, banner: BannerComponent, headlines: List[HeadlineComponent]) -> int:
        """Calculate quality score for the extraction."""
        quality = 30  # Base score
        
        if banner.url and 'mobilecontent.costco.com' in banner.url:
            quality += 40
        if banner.headline:
            quality += 20
        if headlines:
            quality += 10
            
        return quality

    def _update_stats(self, page_structure: PageStructure, filename: str):
        """Update processing statistics."""
        self.stats['successful'] += 1
        quality = page_structure.metadata['quality_score']
        self.stats['quality_scores'].append(quality)
        logger.info(f"✅ {filename} - Quality: {quality}/100")

    def process_all(self, html_files: List[Path]) -> List[PageStructure]:
        """
        Process all HTML files.
        
        Args:
            html_files: List of HTML file paths
            
        Returns:
            List of successfully processed PageStructure objects
        """
        results = []

        for i, file_path in enumerate(html_files):
            logger.info(f"Processing {i+1}/{len(html_files)}")
            result = self.process_file(file_path)
            if result:
                results.append(result)
            
            # Small delay to be respectful to AI service
            time.sleep(1)

        self._log_final_stats()
        return results

    def _log_final_stats(self):
        """Log final processing statistics."""
        if self.stats['quality_scores']:
            avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            logger.info(f"Processing complete! Average quality: {avg_quality:.1f}/100")
        
        if self.stats['failed_files']:
            logger.warning(f"Failed files: {', '.join(self.stats['failed_files'])}")

    def save_results(self, results: List[PageStructure], output_dir: str):
        """
        Save processing results to JSON file.
        
        Args:
            results: List of PageStructure objects
            output_dir: Output directory path
        """
        if not results:
            logger.warning("No results to save")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Convert to JSON-serializable format
        json_data = [
            {
                'url': r.url,
                'banner': asdict(r.banner),
                'headlines': [asdict(h) for h in r.headlines],
                'teasers': [asdict(t) for t in r.teasers],
                'metadata': r.metadata
            }
            for r in results
        ]

        # Save to file
        json_file = output_path / "final_results.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Results saved to {json_file}")

    def get_processing_stats(self) -> dict:
        """Get current processing statistics."""
        stats = self.stats.copy()
        if stats['quality_scores']:
            stats['average_quality'] = sum(stats['quality_scores']) / len(stats['quality_scores'])
        return stats