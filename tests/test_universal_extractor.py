"""
Test suite for universal content extractor.
"""

import pytest
from unittest.mock import Mock
from src.utils.universal_content_extractor import UniversalContentExtractor, extract_content_from_html


class TestUniversalContentExtractor:
    """Test cases for UniversalContentExtractor."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = UniversalContentExtractor()

    def test_extract_recipe_content(self):
        """Test recipe content extraction."""
        html = '''
        <html>
            <body>
                <article>
                    <h1>Spinach Lasagna Roll Ups</h1>
                    <p class="byline">By Costco Kitchen Team</p>
                    <p>Delicious recipe instructions...</p>
                    <ul>
                        <li>2 cups ricotta cheese</li>
                        <li>1 tablespoon olive oil</li>
                    </ul>
                    <img src="/recipe.jpg" alt="Delicious lasagna" />
                </article>
            </body>
        </html>
        '''
        
        result = self.extractor.extract_all_content(html, "https://test.com")
        
        assert result.title == "Spinach Lasagna Roll Ups"
        assert result.content_type == "recipe"
        assert len(result.images) > 0
        assert len(result.lists) > 0

    def test_content_filtering(self):
        """Test that navigation and ads are filtered out."""
        html = '''
        <html>
            <body>
                <nav>Navigation menu</nav>
                <div class="cookie-banner">Accept cookies</div>
                <article>
                    <h1>Main Article</h1>
                    <p>This is the main content.</p>
                </article>
                <footer>Footer content</footer>
            </body>
        </html>
        '''
        
        result = self.extractor.extract_all_content(html, "https://test.com")
        
        # Should extract main content but not navigation
        assert "main content" in result.main_content[0].lower()
        assert not any("navigation" in content.lower() for content in result.main_content)
        assert not any("cookie" in content.lower() for content in result.main_content)

    def test_image_scoring(self):
        """Test enhanced image scoring."""
        html = '''
        <html>
            <body>
                <img src="https://mobilecontent.costco.com/recipe.jpg" alt="Recipe photo" width="800" height="600" />
                <img src="/nav-icon.png" alt="Menu" width="20" height="20" />
            </body>
        </html>
        '''
        
        result = self.extractor.extract_all_content(html, "https://test.com")
        
        # Recipe image should score higher than nav icon
        assert len(result.images) == 2
        assert result.images[0]['score'] > result.images[1]['score']


if __name__ == '__main__':
    pytest.main([__file__])