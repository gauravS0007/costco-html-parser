#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_magazine_extraction():
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
        print("🏆 MAGAZINE FRONT COVER EXTRACTION TEST")
        print("=" * 80)
        
        # Check content type
        print(f"📄 Content Type: {result.content.content_type}")
        print(f"📄 Title: {result.content.title}")
        print(f"📄 Issue Date: {getattr(result.content, 'issue_date', 'N/A')}")
        
        # Check cover story
        cover_story = getattr(result.content, 'cover_story', {})
        print(f"\n📖 COVER STORY:")
        print(f"   Title: {cover_story.get('title', 'N/A')}")
        print(f"   Description: {cover_story.get('description', 'N/A')}")
        print(f"   Link: {cover_story.get('link', 'N/A')}")
        
        # Check cover image
        cover_image = getattr(result.content, 'cover_image', '')
        print(f"\n🖼️  COVER IMAGE:")
        print(f"   URL: {cover_image}")
        print(f"   Alt: {getattr(result.content, 'cover_image_alt', 'N/A')}")
        print(f"   Featured Image: {result.content.featured_image}")
        
        # Check in this issue
        in_this_issue = getattr(result.content, 'in_this_issue', [])
        print(f"\n📋 IN THIS ISSUE ({len(in_this_issue)} items):")
        for i, item in enumerate(in_this_issue[:5]):  # Show first 5
            print(f"   {i+1}. {item.get('title', 'No title')}")
            if item.get('link'):
                print(f"      Link: {item['link']}")
        
        # Check special sections
        special_sections = getattr(result.content, 'special_sections', [])
        print(f"\n⭐ SPECIAL SECTIONS ({len(special_sections)} items):")
        for i, item in enumerate(special_sections[:3]):  # Show first 3
            print(f"   {i+1}. {item.get('title', 'No title')}")
        
        # Check featured sections
        featured_sections = getattr(result.content, 'featured_sections', [])
        print(f"\n🌟 FEATURED SECTIONS ({len(featured_sections)} items):")
        for i, item in enumerate(featured_sections[:3]):  # Show first 3
            print(f"   {i+1}. {item.get('title', 'No title')} ({item.get('category', 'No category')})")
        
        # Check article categories
        article_categories = getattr(result.content, 'article_categories', {})
        print(f"\n📚 ARTICLE CATEGORIES ({len(article_categories)} categories):")
        for category, articles in article_categories.items():
            print(f"   {category}: {len(articles)} articles")
            if articles:
                first_article = articles[0]
                print(f"      - {first_article.get('title', 'No title')}")
                if first_article.get('image'):
                    print(f"        🖼️  {first_article.get('image_alt', 'No alt')} - {first_article.get('image', '')[:50]}...")
        
        # Check PDF download
        pdf_link = getattr(result.content, 'pdf_download_link', '')
        print(f"\n📱 PDF DOWNLOAD: {pdf_link if pdf_link else 'Not found'}")
        
        # Check sections
        print(f"\n📄 SECTIONS: {len(result.sections)} sections")
        for i, section in enumerate(result.sections[:3]):  # Show first 3
            print(f"   {i+1}. {section.get('heading', 'No heading')} (Level {section.get('level', 'Unknown')})")
        
        # Overall assessment
        print(f"\n🎯 ASSESSMENT:")
        
        accuracy_score = 0
        total_checks = 7
        
        # Check content type
        if result.content.content_type.value == 'magazine_front_cover':
            print(f"   ✅ Content type correct: magazine_front_cover")
            accuracy_score += 1
        else:
            print(f"   ❌ Content type wrong: {result.content.content_type.value}")
        
        # Check cover story
        if cover_story and (cover_story.get('title') or cover_story.get('description')):
            print(f"   ✅ Cover story extracted")
            accuracy_score += 1
        else:
            print(f"   ❌ Cover story missing")
        
        # Check cover image
        if cover_image and cover_image.startswith('https://'):
            print(f"   ✅ Cover image found")
            accuracy_score += 1
        elif cover_image:
            print(f"   ⚠️  Cover image found but may be wrong")
        else:
            print(f"   ❌ Cover image missing")
        
        # Check article extraction
        total_articles = sum(len(articles) for articles in article_categories.values())
        if total_articles > 10:
            print(f"   ✅ Articles extracted: {total_articles}")
            accuracy_score += 1
        else:
            print(f"   ❌ Few articles extracted: {total_articles}")
        
        # Check PDF link
        if pdf_link:
            print(f"   ✅ PDF download link found")
            accuracy_score += 1
        else:
            print(f"   ❌ PDF download link missing")
        
        # Check issue date
        issue_date = getattr(result.content, 'issue_date', '')
        if issue_date and len(issue_date) > 3:  # Generic check for any valid date
            print(f"   ✅ Issue date found: {issue_date}")
            accuracy_score += 1
        else:
            print(f"   ❌ Issue date missing or invalid: {issue_date}")
        
        # Check categories
        if len(article_categories) >= 5:
            print(f"   ✅ Multiple categories found: {len(article_categories)}")
            accuracy_score += 1
        else:
            print(f"   ❌ Few categories found: {len(article_categories)}")
        
        print(f"\n📊 ACCURACY SCORE: {accuracy_score}/{total_checks} ({accuracy_score/total_checks*100:.1f}%)")
        
        if accuracy_score >= 5:
            print(f"🎉 EXTRACTION SUCCESS!")
        else:
            print(f"⚠️  EXTRACTION NEEDS IMPROVEMENT")
        
        return True
    else:
        print("❌ Processing failed")
        return False

if __name__ == "__main__":
    test_magazine_extraction()