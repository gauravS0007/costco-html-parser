#!/usr/bin/env python3
import sys
import json
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.processors.super_enhanced_costco_processor import FixedSuperEnhancedCostcoProcessor

def test_duplicates_check():
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
        print("🔍 DUPLICATE CHECK REPORT")
        print("=" * 80)
        
        # Check article categories for duplicates
        article_categories = getattr(result.content, 'article_categories', {})
        all_titles = []
        all_links = []
        
        for category, articles in article_categories.items():
            for article in articles:
                title = article.get('title', '')
                link = article.get('link', '')
                all_titles.append(title)
                all_links.append(link)
        
        # Check for duplicate titles
        title_counts = {}
        for title in all_titles:
            title_counts[title] = title_counts.get(title, 0) + 1
        
        duplicated_titles = {title: count for title, count in title_counts.items() if count > 1}
        
        # Check for duplicate links
        link_counts = {}
        for link in all_links:
            link_counts[link] = link_counts.get(link, 0) + 1
        
        duplicated_links = {link: count for link, count in link_counts.items() if count > 1}
        
        print(f"📊 TOTAL ARTICLES: {len(all_titles)}")
        print(f"📊 UNIQUE TITLES: {len(set(all_titles))}")
        print(f"📊 UNIQUE LINKS: {len(set(all_links))}")
        
        if duplicated_titles:
            print(f"\n❌ DUPLICATE TITLES FOUND:")
            for title, count in duplicated_titles.items():
                print(f"   '{title}': {count} times")
        else:
            print(f"\n✅ NO DUPLICATE TITLES FOUND")
        
        if duplicated_links:
            print(f"\n❌ DUPLICATE LINKS FOUND:")
            for link, count in duplicated_links.items():
                print(f"   '{link}': {count} times")
        else:
            print(f"\n✅ NO DUPLICATE LINKS FOUND")
        
        # Check Featured Sections for duplicates
        featured_sections = getattr(result.content, 'featured_sections', [])
        featured_titles = [item.get('title', '') for item in featured_sections]
        featured_links = [item.get('link', '') for item in featured_sections]
        
        featured_title_counts = {}
        for title in featured_titles:
            featured_title_counts[title] = featured_title_counts.get(title, 0) + 1
        
        featured_duplicated_titles = {title: count for title, count in featured_title_counts.items() if count > 1}
        
        print(f"\n📊 FEATURED SECTIONS: {len(featured_sections)} items")
        print(f"📊 UNIQUE FEATURED TITLES: {len(set(featured_titles))}")
        
        if featured_duplicated_titles:
            print(f"\n❌ DUPLICATE FEATURED TITLES:")
            for title, count in featured_duplicated_titles.items():
                print(f"   '{title}': {count} times")
        else:
            print(f"\n✅ NO DUPLICATE FEATURED TITLES")
        
        # Overall duplicate assessment
        total_duplicates = len(duplicated_titles) + len(duplicated_links) + len(featured_duplicated_titles)
        if total_duplicates == 0:
            print(f"\n🎉 ZERO DUPLICATES DETECTED - PERFECT!")
        else:
            print(f"\n⚠️  {total_duplicates} DUPLICATE ISSUES FOUND")
        
        return total_duplicates == 0
    else:
        print("❌ Processing failed")
        return False

if __name__ == "__main__":
    test_duplicates_check()