#!/usr/bin/env python3
"""
Test script for enhanced email scraping functionality
Tests real email finding from company websites
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging
from final_secure_system import RealWebScrapingAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

def test_email_scraping():
    """Test the enhanced email scraping functionality"""
    print("🧪 Testing Enhanced Email Scraping Functionality")
    print("=" * 60)
    
    # Initialize the scraping agent
    scraper = RealWebScrapingAgent()
    
    # Test companies with known websites
    test_companies = [
        {
            'name': 'Cursor',
            'website': 'https://cursor.sh'
        },
        {
            'name': 'Anthropic',
            'website': 'https://anthropic.com'
        },
        {
            'name': 'OpenAI',
            'website': 'https://openai.com'
        },
        {
            'name': 'Vercel',
            'website': 'https://vercel.com'
        },
        {
            'name': 'Linear',
            'website': 'https://linear.app'
        }
    ]
    
    results = []
    
    for company in test_companies:
        print(f"\n🔍 Testing email finding for: {company['name']}")
        print(f"🌐 Website: {company['website']}")
        
        try:
            # Test the enhanced email finding
            found_email = scraper._find_real_contact_email(company)
            
            if found_email:
                print(f"✅ FOUND EMAIL: {found_email}")
                results.append({
                    'company': company['name'],
                    'website': company['website'],
                    'email': found_email,
                    'status': 'SUCCESS'
                })
            else:
                print(f"❌ NO EMAIL FOUND")
                results.append({
                    'company': company['name'],
                    'website': company['website'],
                    'email': None,
                    'status': 'FAILED'
                })
                
        except Exception as e:
            print(f"💥 ERROR: {e}")
            results.append({
                'company': company['name'],
                'website': company['website'],
                'email': None,
                'status': f'ERROR: {e}'
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 EMAIL SCRAPING TEST RESULTS")
    print("=" * 60)
    
    successful = 0
    for result in results:
        status_emoji = "✅" if result['status'] == 'SUCCESS' else "❌"
        print(f"{status_emoji} {result['company']:<15} | {result['email'] or 'No email found'}")
        if result['status'] == 'SUCCESS':
            successful += 1
    
    print(f"\n📈 Success Rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    
    if successful > 0:
        print("🎉 Enhanced email scraping is working!")
    else:
        print("⚠️ Enhanced email scraping needs improvement")
    
    return results

def test_web_scraping_with_emails():
    """Test the full web scraping with enhanced email finding"""
    print("\n🕷️ Testing Full Web Scraping with Enhanced Emails")
    print("=" * 60)
    
    scraper = RealWebScrapingAgent()
    
    try:
        # Test scraping YC companies with enhanced email finding
        companies = scraper.scrape_source('ycombinator', 3)
        
        print(f"📊 Scraped {len(companies)} companies")
        
        for i, company in enumerate(companies, 1):
            print(f"\n{i}. {company['name']}")
            print(f"   🌐 Website: {company.get('website', 'N/A')}")
            print(f"   📧 Email: {company.get('contact_email', 'N/A')}")
            print(f"   🏢 Industry: {company.get('industry', 'N/A')}")
            print(f"   📝 Description: {company.get('description', 'N/A')[:100]}...")
            
            # Check if email looks real vs generated
            email = company.get('contact_email', '')
            if email:
                if any(pattern in email for pattern in ['founders@', 'hello@', 'contact@']):
                    if company.get('website', '') in email:
                        print(f"   ✅ Email appears to be from real domain")
                    else:
                        print(f"   ⚠️ Email might be generated")
                else:
                    print(f"   🎯 Email appears to be specifically found")
        
        return companies
        
    except Exception as e:
        print(f"💥 Error in web scraping test: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Starting Enhanced Email Scraping Tests")
    
    # Test 1: Email finding functionality
    email_results = test_email_scraping()
    
    # Test 2: Full web scraping with emails
    scraping_results = test_web_scraping_with_emails()
    
    print("\n🏁 All tests completed!")
    print(f"📧 Email finding tests: {len([r for r in email_results if r['status'] == 'SUCCESS'])}/{len(email_results)} successful")
    print(f"🕷️ Web scraping results: {len(scraping_results)} companies found") 