#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_enhanced_magazine_features():
    processor = FixedSuperEnhancedCostcoProcessor()
    
    filename = 'October Edition \xa0_ Costco.html'
    file_path = f'/Users/apple/Desktop/Python/costco-html-parser/data/html_files/{filename}'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    result = processor.process_content(
        html_content=html_content,
        url='https://www.costco.com/October-Edition-',
        filename=filename
    )
    
    if result:
        print("🎯 ENHANCED MAGAZINE FEATURES TEST")
        print("=" * 80)
        
        # Test Cover Story
        cover_story = getattr(result.content, 'cover_story', {})
        print(f"📖 COVER STORY:")
        print(f"   Title: {cover_story.get('title', 'N/A')}")
        print(f"   Description: {cover_story.get('description', 'N/A')}")
        print(f"   Link: {cover_story.get('link', 'N/A')}")
        
        # Test In This Issue
        in_this_issue = getattr(result.content, 'in_this_issue', [])
        print(f"\n📋 IN THIS ISSUE ({len(in_this_issue)} items):")
        for i, item in enumerate(in_this_issue):
            print(f"   {i+1}. {item.get('title', 'No title')}")
            if item.get('description'):
                print(f"      📝 {item.get('description')}")
            print(f"      🔗 {item.get('link', 'No link')}")
        
        # Test Featured Sections
        featured_sections = getattr(result.content, 'featured_sections', [])
        print(f"\n🌟 FEATURED SECTIONS ({len(featured_sections)} items):")
        for i, item in enumerate(featured_sections):
            print(f"   {i+1}. {item.get('title', 'No title')} ({item.get('category', 'No category')})")
            if item.get('image'):
                print(f"      🖼️  {item.get('image_alt', 'No alt')} - {item.get('image', '')[:50]}...")
            print(f"      🔗 {item.get('link', 'No link')}")
        
        # Test Article Descriptions
        article_categories = getattr(result.content, 'article_categories', {})
        print(f"\n📚 ARTICLE DESCRIPTIONS CHECK:")
        articles_with_descriptions = 0
        total_articles = 0
        
        for category, articles in article_categories.items():
            for article in articles:
                total_articles += 1
                description = article.get('description', '')
                if description:
                    articles_with_descriptions += 1
                    print(f"   ✅ {article.get('title', 'No title')}: {description}")
        
        print(f"\n📊 DESCRIPTION COVERAGE: {articles_with_descriptions}/{total_articles} articles have descriptions ({articles_with_descriptions/total_articles*100:.1f}%)")
        
        # Overall Enhanced Features Assessment
        print(f"\n🎯 ENHANCED FEATURES ASSESSMENT:")
        
        features_score = 0
        total_features = 4
        
        # Check Cover Story
        if cover_story.get('title') or cover_story.get('description'):
            print(f"   ✅ Cover Story extracted")
            features_score += 1
        else:
            print(f"   ❌ Cover Story missing")
        
        # Check In This Issue
        if len(in_this_issue) > 0:
            print(f"   ✅ In This Issue extracted: {len(in_this_issue)} items")
            features_score += 1
        else:
            print(f"   ❌ In This Issue missing")
        
        # Check Featured Sections
        if len(featured_sections) > 0:
            print(f"   ✅ Featured Sections extracted: {len(featured_sections)} items")
            features_score += 1
        else:
            print(f"   ❌ Featured Sections missing")
        
        # Check Article Descriptions
        if articles_with_descriptions > 0:
            print(f"   ✅ Article Descriptions: {articles_with_descriptions} articles")
            features_score += 1
        else:
            print(f"   ❌ Article Descriptions missing")
        
        print(f"\n📊 ENHANCED FEATURES SCORE: {features_score}/{total_features} ({features_score/total_features*100:.1f}%)")
        
        return True
    else:
        print("❌ Processing failed")
        return False

if __name__ == "__main__":
    test_enhanced_magazine_features()