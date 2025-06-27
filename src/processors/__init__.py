# ===== src/processors/__init__.py =====
"""
Processing modules for Costco HTML parser.
"""

# Original processors
from .costco_processor import CostcoProcessor
from .html_processor import HTMLProcessor

# Enhanced processors
from .enhanced_costco_processor import EnhancedCostcoProcessor
from .enhanced_html_processor import EnhancedHTMLProcessor

__all__ = [
    # Original processors
    'CostcoProcessor', 'HTMLProcessor',
    # Enhanced processors  
    'EnhancedCostcoProcessor', 'EnhancedHTMLProcessor'
]