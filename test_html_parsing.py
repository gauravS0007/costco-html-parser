#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/apple/Desktop/Python/costco-html-parser')

from src.utils.universal_content_extractor import FixedUniversalContentExtractor
from bs4 import BeautifulSoup

# Test HTML from user's paste
html_snippet = '''
<div class="col-xs-12 col-md-8">
    <h1 style="font-size: 4em;">Upgrade your space</h1>
    <h2>Transform your kitchen (or bathroom) with Costco's Countertop Installation program</h2>
    <p style="font-size: 1.2em;"><span style="font-size: 0.8em;">by <span style="text-transform: uppercase;">Andrea Tomkins</span></span></p>
    <p>The kitchen is often called the heart of the home due to its central role in our daily lives. Food is prepared, shared and consumed here, but it's also a place for everyday living. Kitchens are versatile, multipurpose spaces that also serve as workstations for chores, crafting, schoolwork and working from home.</p>
    <p>The team behind Costco's Countertop Installation program keenly understands that if the kitchen counter is where you are rolling out the cookie dough and helping the kids with their homework, that counter needs to be a durable, high-quality product that enhances your home's aesthetics, functionality and value.</p>
    <p>Through Costco's Countertop Installation program, the process for members who want to upgrade their countertops is remarkably easy and convenient. "All of the big decisions are made in one appointment in the comfort of your own home," says Kelly Martin, Cosentino's national account director. "It's truly white-glove service."</p>
    <p>When the job is completed, not only is there a gorgeous counter to enjoy for years to come, you'll also receive a Costco Shop Card for 10% of its cost.</p>
    <h3><b>A cut above</b></h3>
    <p>"Costco does the heavy lifting for our members to make sure they're getting the best quality and the best value," says Eric Strasik, assistant buyer in Costco's Home &amp; Installation department.</p>
    <h3><strong>Sustainability matters</strong></h3>
    <p>Sustainability is a core value at Cosentino. The company has many green initiatives, but here are a few worth mentioning: One-third of its production includes reused and recycled materials, making it the only company in the industry with its own waste management and treatment plants; all products are manufactured with 100% certified renewable electric energy and its solar park produces the equivalent of the energy usage of 42,000 households.</p>
</div>
'''

print("🔍 TESTING HTML PARSING")
print("=" * 40)

# Create extractor
extractor = FixedUniversalContentExtractor()

# Test the HTML snippet
soup = BeautifulSoup(html_snippet, 'html.parser')
print(f"1. Found {len(soup.find_all('p'))} paragraph tags")

# Show each paragraph
for i, p in enumerate(soup.find_all('p')):
    text = p.get_text().strip()
    print(f"   {i+1}. {text[:80]}...")
    
    # Check for target content
    if 'Through Costco' in text:
        print(f"      ✅ FOUND: Through Costco paragraph")
    if 'When the job is completed' in text:
        print(f"      ✅ FOUND: When the job is completed paragraph")

print(f"\n2. Testing extraction:")
extracted = extractor.extract_all_content(html_snippet, 'https://www.costco.com/test')
print(f"   Extracted {len(extracted.main_content)} paragraphs")

# Check specific content
target_phrases = [
    "Through Costco's Countertop Installation program",
    "When the job is completed, not only is there a gorgeous counter"
]

for phrase in target_phrases:
    found = any(phrase in content for content in extracted.main_content)
    status = "✅ FOUND" if found else "❌ MISSING"
    print(f"   {status}: {phrase[:50]}...")

print(f"\n3. Extracted content:")
for i, content in enumerate(extracted.main_content):
    print(f"   {i+1}. {content[:80]}...")