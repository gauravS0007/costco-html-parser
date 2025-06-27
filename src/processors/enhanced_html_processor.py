"""
Enhanced HTML processor with rich schema export capabilities.
FIXED: JSON serialization for ContentType enums
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict
from dataclasses import asdict
from enum import Enum

from ..processors.enhanced_costco_processor import EnhancedCostcoProcessor
from ..models.content_schemas import EnhancedPageStructure, ContentType
from ..config.settings import SUPPORTED_EXTENSIONS

logger = logging.getLogger(__name__)


class EnhancedJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle ContentType enums."""
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


def convert_content_to_serializable(content_dict):
    """Convert content dict with enums to JSON serializable format."""
    serializable_dict = {}
    for key, value in content_dict.items():
        if isinstance(value, Enum):
            serializable_dict[key] = value.value
        elif isinstance(value, list):
            serializable_dict[key] = [item.value if isinstance(item, Enum) else item for item in value]
        elif isinstance(value, dict):
            serializable_dict[key] = convert_content_to_serializable(value)
        else:
            serializable_dict[key] = value
    return serializable_dict


class EnhancedHTMLProcessor:
    """Enhanced HTML processor with schema-aware content extraction."""

    def __init__(self):
        """Initialize enhanced processor with statistics tracking."""
        self.processor = EnhancedCostcoProcessor()
        self.stats = {
            'processed': 0,
            'successful': 0,
            'quality_scores': [],
            'failed_files': [],
            'content_types': {},
            'schema_completeness': []
        }

    def find_files(self, directory: str) -> List[Path]:
        """Find HTML files in the specified directory."""
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
        """Extract URL from filename."""
        filename = file_path.stem
        clean_name = filename.replace('_', '-').replace(' ', '-')
        return f"https://www.costco.com/{clean_name}.html"

    def process_file(self, file_path: Path) -> Optional[EnhancedPageStructure]:
        """
        Process a single HTML file with enhanced schema extraction.
        
        Args:
            file_path: Path to the HTML file to process
            
        Returns:
            EnhancedPageStructure object or None if processing failed
        """
        try:
            logger.info(f"📄 Processing: {file_path.name}")

            # Read and validate file
            html_content = self._read_file(file_path)
            if not html_content:
                return None

            # Process with enhanced processor
            url = self.extract_url(file_path)
            page_structure = self.processor.process_content(html_content, url, file_path.name)
            
            if not page_structure:
                logger.error(f"❌ Enhanced processing failed for {file_path.name}")
                return None

            # Update statistics
            self._update_enhanced_stats(page_structure, file_path.name)
            
            logger.info(f"✅ {file_path.name} - Type: {page_structure.content.content_type.value} - Quality: {page_structure.content_quality_score}/100")
            return page_structure

        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")
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
                logger.warning(f"⚠️ File too small: {file_path.name}")
                return None
                
            return html_content
            
        except Exception as e:
            logger.error(f"❌ Failed to read file {file_path.name}: {e}")
            return None

    def _update_enhanced_stats(self, page_structure: EnhancedPageStructure, filename: str):
        """Update enhanced processing statistics."""
        self.stats['successful'] += 1
        
        # Quality scores
        quality = page_structure.content_quality_score
        self.stats['quality_scores'].append(quality)
        
        # Content type distribution - store as string
        content_type = page_structure.content.content_type.value
        self.stats['content_types'][content_type] = self.stats['content_types'].get(content_type, 0) + 1
        
        # Schema completeness
        completeness = self._calculate_schema_completeness(page_structure.content)
        self.stats['schema_completeness'].append(completeness)

    def _calculate_schema_completeness(self, content) -> Dict[str, bool]:
        """Calculate schema completeness for different content types."""
        completeness = {
            'has_title': bool(content.title),
            'has_description': bool(content.description),
            'has_featured_image': bool(content.featured_image),
            'has_byline': bool(content.byline)
        }
        
        # Content-type specific completeness
        if content.content_type == ContentType.RECIPE:
            completeness.update({
                'has_ingredients': bool(getattr(content, 'ingredients', [])),
                'has_instructions': bool(getattr(content, 'instructions', [])),
                'has_timing': bool(getattr(content, 'prep_time', '') or getattr(content, 'cook_time', ''))
            })
        elif content.content_type == ContentType.TRAVEL:
            completeness.update({
                'has_destinations': bool(getattr(content, 'destinations', [])),
                'has_attractions': bool(getattr(content, 'attractions', [])),
                'has_travel_tips': bool(getattr(content, 'travel_tips', []))
            })
        elif content.content_type == ContentType.TECH:
            completeness.update({
                'has_products': bool(getattr(content, 'products', [])),
                'has_features': bool(getattr(content, 'features', [])),
                'has_specs': bool(getattr(content, 'specifications', {}))
            })
            
        return completeness

    def process_all(self, html_files: List[Path]) -> List[EnhancedPageStructure]:
        """Process all HTML files with enhanced extraction."""
        results = []

        for i, file_path in enumerate(html_files):
            logger.info(f"📊 Processing {i+1}/{len(html_files)}: {file_path.name}")
            result = self.process_file(file_path)
            if result:
                results.append(result)
            
            # Small delay to be respectful to AI service
            __import__('time').sleep(1)

        self._log_enhanced_final_stats()
        return results

    def _log_enhanced_final_stats(self):
        """Log enhanced final processing statistics."""
        print(f"\n📊 ENHANCED PROCESSING COMPLETE!")
        print("=" * 50)
        
        if self.stats['quality_scores']:
            avg_quality = sum(self.stats['quality_scores']) / len(self.stats['quality_scores'])
            print(f"✅ Success Rate: {self.stats['successful']}/{self.stats['processed']} ({(self.stats['successful']/self.stats['processed']*100):.1f}%)")
            print(f"📈 Average Quality: {avg_quality:.1f}/100")
            
        # Content type distribution
        if self.stats['content_types']:
            print(f"\n📋 CONTENT TYPE DISTRIBUTION:")
            for content_type, count in sorted(self.stats['content_types'].items()):
                percentage = (count / self.stats['successful'] * 100) if self.stats['successful'] > 0 else 0
                print(f"   {content_type.upper()}: {count} articles ({percentage:.1f}%)")
                
        # Schema completeness
        if self.stats['schema_completeness']:
            print(f"\n🎯 SCHEMA COMPLETENESS:")
            all_fields = set()
            for completeness in self.stats['schema_completeness']:
                all_fields.update(completeness.keys())
                
            for field in sorted(all_fields):
                completed = sum(1 for c in self.stats['schema_completeness'] if c.get(field, False))
                percentage = (completed / len(self.stats['schema_completeness']) * 100)
                print(f"   {field}: {completed}/{len(self.stats['schema_completeness'])} ({percentage:.1f}%)")
        
        if self.stats['failed_files']:
            print(f"\n⚠️ Failed Files ({len(self.stats['failed_files'])}):")
            for failed_file in self.stats['failed_files'][:5]:  # Show first 5
                print(f"   - {failed_file}")
            if len(self.stats['failed_files']) > 5:
                print(f"   ... and {len(self.stats['failed_files']) - 5} more")

    def save_enhanced_results(self, results: List[EnhancedPageStructure], output_dir: str):
        """Save enhanced results with schema-aware JSON export."""
        if not results:
            logger.warning("⚠️ No results to save")
            return

        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Save main results file
        self._save_main_results(results, output_path)
        
        # Save content-type specific files
        self._save_by_content_type(results, output_path)
        
        # Save processing statistics
        self._save_processing_stats(output_path)

    def _save_main_results(self, results: List[EnhancedPageStructure], output_path: Path):
        """Save main enhanced results file."""
        json_data = []
        
        for result in results:
            # Convert content schema to dict
            content_dict = asdict(result.content)
            
            # Convert enums to serializable format
            content_dict = convert_content_to_serializable(content_dict)
            
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
        main_file = output_path / "enhanced_results.json"
        with open(main_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, cls=EnhancedJSONEncoder)

        logger.info(f"✅ Enhanced results saved to {main_file}")

    def _save_by_content_type(self, results: List[EnhancedPageStructure], output_path: Path):
        """Save results grouped by content type."""
        content_type_groups = {}
        
        for result in results:
            content_type = result.content.content_type.value  # Convert enum to string
            if content_type not in content_type_groups:
                content_type_groups[content_type] = []
            content_type_groups[content_type].append(result)

        # Save each content type separately
        for content_type, type_results in content_type_groups.items():
            type_data = []
            
            for result in type_results:
                content_dict = asdict(result.content)
                
                # Convert enums to serializable format
                content_dict = convert_content_to_serializable(content_dict)
                
                type_data.append({
                    'url': result.url,
                    'content': content_dict,
                    'quality_score': result.content_quality_score
                })
            
            type_file = output_path / f"{content_type}_articles.json"
            with open(type_file, 'w', encoding='utf-8') as f:
                json.dump(type_data, f, indent=2, ensure_ascii=False, cls=EnhancedJSONEncoder)
                
            logger.info(f"📄 {content_type.upper()} articles saved to {type_file}")

    def _save_processing_stats(self, output_path: Path):
        """Save detailed processing statistics."""
        # Content types are already strings in self.stats['content_types']
        stats_data = {
            'processing_summary': {
                'total_processed': self.stats['processed'],
                'successful': self.stats['successful'],
                'failed': len(self.stats['failed_files']),
                'success_rate': (self.stats['successful'] / self.stats['processed'] * 100) if self.stats['processed'] > 0 else 0
            },
            'quality_metrics': {
                'average_quality': sum(self.stats['quality_scores']) / len(self.stats['quality_scores']) if self.stats['quality_scores'] else 0,
                'quality_distribution': self._get_quality_distribution(),
                'quality_scores': self.stats['quality_scores']
            },
            'content_type_distribution': self.stats['content_types'],  # Already strings
            'schema_completeness_summary': self._get_schema_completeness_summary(),
            'failed_files': self.stats['failed_files']
        }
        
        stats_file = output_path / "processing_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_data, f, indent=2, ensure_ascii=False)
            
        logger.info(f"📊 Processing statistics saved to {stats_file}")

    def _get_quality_distribution(self) -> Dict[str, int]:
        """Get quality score distribution."""
        distribution = {'excellent (90-100)': 0, 'good (70-89)': 0, 'fair (50-69)': 0, 'poor (0-49)': 0}
        
        for score in self.stats['quality_scores']:
            if score >= 90:
                distribution['excellent (90-100)'] += 1
            elif score >= 70:
                distribution['good (70-89)'] += 1
            elif score >= 50:
                distribution['fair (50-69)'] += 1
            else:
                distribution['poor (0-49)'] += 1
                
        return distribution

    def _get_schema_completeness_summary(self) -> Dict[str, float]:
        """Get schema completeness summary."""
        if not self.stats['schema_completeness']:
            return {}
            
        all_fields = set()
        for completeness in self.stats['schema_completeness']:
            all_fields.update(completeness.keys())
            
        summary = {}
        for field in all_fields:
            completed = sum(1 for c in self.stats['schema_completeness'] if c.get(field, False))
            percentage = (completed / len(self.stats['schema_completeness']) * 100)
            summary[field] = round(percentage, 1)
            
        return summary

    def get_enhanced_processing_stats(self) -> Dict:
        """Get enhanced processing statistics."""
        stats = self.stats.copy()
        
        if stats['quality_scores']:
            stats['average_quality'] = sum(stats['quality_scores']) / len(stats['quality_scores'])
            stats['quality_distribution'] = self._get_quality_distribution()
            
        if stats['schema_completeness']:
            stats['schema_completeness_summary'] = self._get_schema_completeness_summary()
            
        return stats