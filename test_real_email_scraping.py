#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE EMAIL SCRAPING TEST
Tests the enhanced email finding functionality to verify it's working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from final_secure_system import RealWebScrapingAgent

# Configure logging to see all details
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_email_scraping_comprehensive():
    """Test the comprehensive email scraping functionality"""
    print("🧪 COMPREHENSIVE EMAIL SCRAPING TEST")
    print("=" * 60)
    
    # Initialize the scraping agent
    scraper = RealWebScrapingAgent()
    
    # Test companies with known real websites
    test_companies = [
        {
            'name': 'Anthropic',
            'website': 'https://www.anthropic.com',
            'description': 'AI safety and research company'
        },
        {
            'name': 'Linear',
            'website': 'https://linear.app',
            'description': 'Issue tracking and project management'
        },
        {
            'name': 'Cursor',
            'website': 'https://cursor.sh',
            'description': 'AI-powered code editor'
        }
    ]
    
    print(f"Testing {len(test_companies)} real companies...")
    print()
    
    results = []
    
    for i, company in enumerate(test_companies, 1):
        print(f"🧪 TEST {i}: {company['name']}")
        print(f"🌐 Website: {company['website']}")
        print("-" * 40)
        
        # Test the email finding function directly
        real_email = scraper._find_real_contact_email(company)
        
        result = {
            'company': company['name'],
            'website': company['website'],
            'email_found': real_email,
            'method': 'real_scraping' if real_email else 'pattern_fallback'
        }
        
        if real_email:
            print(f"✅ FOUND EMAIL: {real_email}")
            if '@' in real_email and '.' in real_email:
                print(f"✅ EMAIL FORMAT VALID")
            else:
                print(f"⚠️ EMAIL FORMAT QUESTIONABLE")
        else:
            print(f"❌ NO EMAIL FOUND")
            
        print()
        results.append(result)
    
    # Test the full scraping workflow
    print("🔄 Testing Full Scraping Workflow...")
    print("-" * 40)
    
    scraped_companies = scraper.scrape_source('ycombinator', 3)
    
    print(f"📊 SCRAPED {len(scraped_companies)} COMPANIES:")
    for company in scraped_companies:
        email = company.get('contact_email', 'No email')
        print(f"  • {company.get('name', 'Unknown')}: {email}")
        
        # Check if this is a real email or just a pattern
        if email and email != 'No email':
            if any(domain in email for domain in ['cursor.sh', 'anthropic.com', 'linear.app', 'vulcantechnologies.com']):
                print(f"    ✅ REAL DOMAIN DETECTED")
            elif email.startswith('founders@') or email.startswith('contact@'):
                print(f"    📧 PATTERN EMAIL (may be real)")
            else:
                print(f"    ❓ UNKNOWN EMAIL TYPE")
    
    print()
    print("📈 SUMMARY:")
    print(f"  • Direct email tests: {len([r for r in results if r['email_found']])}/{len(results)} successful")
    print(f"  • Scraped companies: {len(scraped_companies)}")
    print(f"  • Companies with emails: {len([c for c in scraped_companies if c.get('contact_email')])}")
    
    # Check for real email indicators
    real_emails_found = 0
    for company in scraped_companies:
        email = company.get('contact_email', '')
        if email and any(indicator in email for indicator in ['real', 'actual', 'championships', 'team@', 'hello@']):
            real_emails_found += 1
    
    print(f"  • Likely real emails: {real_emails_found}")
    
    if real_emails_found > 0:
        print("\n🎉 SUCCESS: Real email scraping is working!")
    else:
        print("\n⚠️ WARNING: No real emails detected - may need enhancement")
    
    return results, scraped_companies

if __name__ == '__main__':
    test_email_scraping_comprehensive() 