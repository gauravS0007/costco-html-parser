"""
Test suite for processor modules.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from src.processors.html_processor import HTMLProcessor
from src.processors.costco_processor import CostcoProcessor
from src.models.components import PageStructure


class TestHTMLProcessor:
    """Test cases for HTMLProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.processor = HTMLProcessor()

    def test_find_files_existing_directory(self):
        """Test finding HTML files in existing directory."""
        with patch('pathlib.Path.exists') as mock_exists, \
             patch('pathlib.Path.glob') as mock_glob:
            
            mock_exists.return_value = True
            mock_glob.return_value = [Path('test1.html'), Path('test2.html')]
            
            files = self.processor.find_files('test_dir')
            assert len(files) == 2

    def test_find_files_non_existing_directory(self):
        """Test finding files in non-existing directory."""
        with patch('pathlib.Path.exists') as mock_exists:
            mock_exists.return_value = False
            
            files = self.processor.find_files('nonexistent')
            assert len(files) == 0

    def test_extract_url(self):
        """Test URL extraction from filename."""
        file_path = Path('test_article_name.html')
        url = self.processor.extract_url(file_path)
        expected = "https://www.costco.com/test-article-name.html"
        assert url == expected

    def test_process_file_success(self):
        """Test successful file processing."""
        with patch.object(self.processor, '_read_file') as mock_read, \
             patch.object(self.processor, '_process_with_ai') as mock_ai, \
             patch.object(self.processor, '_build_page_structure') as mock_build:
            
            mock_read.return_value = "<html>content</html>"
            mock_ai.return_value = {"banner": {}, "headlines": [], "teasers": []}
            mock_build.return_value = Mock(spec=PageStructure)
            
            result = self.processor.process_file(Path('test.html'))
            assert result is not None

    def test_process_file_read_failure(self):
        """Test file processing with read failure."""
        with patch.object(self.processor, '_read_file') as mock_read:
            mock_read.return_value = None
            
            result = self.processor.process_file(Path('test.html'))
            assert result is None


class TestCostcoProcessor:
    """Test cases for CostcoProcessor."""

    def setup_method(self):
        """Set up test fixtures."""
        with patch('boto3.client'):
            self.processor = CostcoProcessor()

    def test_find_article_area_with_selector(self):
        """Test finding article area using CSS selectors."""
        html = '''
        <html>
            <body>
                <div class="article-content">
                    <p>This is a long article content with more than 500 characters. 
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod 
                    tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, 
                    quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo 
                    consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse 
                    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat 
                    non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
                </div>
            </body>
        </html>
        '''
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        area = self.processor.find_article_area(soup)
        assert area is not None
        assert 'article-content' in area.get('class', [])

    @patch('src.processors.costco_processor.detect_content_type')
    @patch('src.processors.costco_processor.fix_image_urls')
    def test_create_ai_prompt(self, mock_fix_images, mock_detect):
        """Test AI prompt creation."""
        mock_fix_images.return_value = "<html>fixed</html>"
        mock_detect.return_value = {
            'content_type': 'recipe',
            'byline': 'By Costco Kitchen Team'
        }
        
        prompt = self.processor.create_ai_prompt(
            "<html>test</html>", 
            "https://test.com", 
            "test.html"
        )
        
        assert "recipe" in prompt.lower()
        assert "By Costco Kitchen Team" in prompt

    def test_call_ai_no_bedrock(self):
        """Test AI call without Bedrock client."""
        self.processor.bedrock = None
        result = self.processor.call_ai("test prompt")
        assert result is None


if __name__ == '__main__':
    pytest.main([__file__])