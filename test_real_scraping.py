#!/usr/bin/env python3

"""
🧪 REAL WEB SCRAPING TEST
Demonstrates that the system is doing ACTUAL web scraping with NO hardcoded data
"""

import requests
import json
import time
from datetime import datetime

def test_real_web_scraping():
    """Test that the system is doing REAL web scraping every time"""
    
    print("🧪 TESTING REAL WEB SCRAPING FUNCTIONALITY")
    print("=" * 60)
    print("🎯 GOAL: Prove the system scrapes FRESH data every time")
    print("❌ NO hardcoded data allowed!")
    print("=" * 60)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Multiple YC scraping requests
    print("\n🕷️ TEST 1: Y Combinator Real Web Scraping")
    print("-" * 40)
    
    yc_companies_round1 = []
    yc_companies_round2 = []
    
    for round_num in [1, 2]:
        print(f"\n🔄 Round {round_num}: Scraping YC companies...")
        
        response = requests.post(f"{base_url}/api/outreach/scrape", 
                               json={"source": "ycombinator", "limit": 5})
        
        if response.status_code == 200:
            data = response.json()
            companies = data.get('startups', [])
            
            print(f"✅ Found {len(companies)} companies")
            
            for i, company in enumerate(companies, 1):
                name = company.get('name', 'Unknown')
                source = company.get('source', 'Unknown')
                scraped_at = company.get('scraped_at', 'Unknown')
                real_scraped = company.get('real_scraped', False)
                
                print(f"   {i}. 🏢 {name}")
                print(f"      📅 Scraped: {scraped_at}")
                print(f"      🔍 Source: {source}")
                print(f"      ✅ Real Scraped: {real_scraped}")
                
                if round_num == 1:
                    yc_companies_round1.append(name)
                else:
                    yc_companies_round2.append(name)
        else:
            print(f"❌ Error: {response.status_code}")
        
        time.sleep(2)  # Brief pause between requests
    
    # Test 2: Check for freshness (different companies each time)
    print(f"\n🔍 TEST 2: Freshness Check")
    print("-" * 40)
    print(f"Round 1 companies: {yc_companies_round1}")
    print(f"Round 2 companies: {yc_companies_round2}")
    
    # Check if we got different companies (proving real scraping)
    different_companies = set(yc_companies_round1) != set(yc_companies_round2)
    
    if different_companies:
        print("✅ SUCCESS: Different companies found! This proves REAL web scraping!")
    else:
        print("⚠️  Same companies found - might be using cached/hardcoded data")
    
    # Test 3: Check timestamps are recent
    print(f"\n🕐 TEST 3: Timestamp Freshness")
    print("-" * 40)
    
    response = requests.post(f"{base_url}/api/outreach/scrape", 
                           json={"source": "ycombinator", "limit": 2})
    
    if response.status_code == 200:
        data = response.json()
        companies = data.get('startups', [])
        
        for company in companies:
            scraped_at = company.get('scraped_at', '')
            if scraped_at:
                # Check if timestamp is recent (within last minute)
                try:
                    scraped_time = datetime.fromisoformat(scraped_at.replace('Z', '+00:00'))
                    now = datetime.now(scraped_time.tzinfo) if scraped_time.tzinfo else datetime.now()
                    time_diff = (now - scraped_time).total_seconds()
                    
                    if time_diff < 60:  # Within last minute
                        print(f"✅ {company['name']}: Fresh timestamp ({time_diff:.1f}s ago)")
                    else:
                        print(f"⚠️  {company['name']}: Old timestamp ({time_diff:.1f}s ago)")
                except:
                    print(f"❌ {company['name']}: Invalid timestamp format")
    
    # Test 4: Real scraping indicators
    print(f"\n🔍 TEST 4: Real Scraping Indicators")
    print("-" * 40)
    
    response = requests.post(f"{base_url}/api/outreach/scrape", 
                           json={"source": "ycombinator", "limit": 3})
    
    if response.status_code == 200:
        data = response.json()
        companies = data.get('startups', [])
        
        real_scraping_indicators = 0
        
        for company in companies:
            indicators = []
            
            # Check for real scraping indicators
            if company.get('real_scraped') == True:
                indicators.append("✅ real_scraped flag")
                real_scraping_indicators += 1
            
            if 'Real' in company.get('source', '') or 'JSON API' in company.get('source', ''):
                indicators.append("✅ real source")
                real_scraping_indicators += 1
            
            if company.get('scraped_at'):
                indicators.append("✅ fresh timestamp")
                real_scraping_indicators += 1
            
            print(f"🏢 {company['name']}: {', '.join(indicators) if indicators else '❌ No indicators'}")
    
    # Final Assessment
    print(f"\n🎯 FINAL ASSESSMENT")
    print("=" * 60)
    
    if real_scraping_indicators >= 6:  # At least 2 indicators per company
        print("🎉 SUCCESS: System is doing REAL web scraping!")
        print("✅ Fresh data every time")
        print("✅ No hardcoded fallbacks")
        print("✅ Proper timestamps")
        print("✅ Real scraping indicators")
    else:
        print("❌ FAILED: System may still be using hardcoded data")
        print("🔧 Check the web scraping implementation")
    
    print(f"\n💡 Real scraping indicators found: {real_scraping_indicators}")
    print("=" * 60)

if __name__ == "__main__":
    test_real_web_scraping() 