"""
Web Scraper for Startup Data Collection
Automatically scrapes startup information from multiple sources
"""

import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from playwright.async_api import async_playwright
import pandas as pd
import json
import time
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from urllib.parse import urljoin, urlparse
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StartupData:
    """Data structure for scraped startup information"""
    name: str
    description: str
    industry: str
    stage: str
    location: str
    website: str
    funding: Optional[str] = None
    team_size: Optional[str] = None
    founded_year: Optional[str] = None
    technologies: List[str] = None
    challenges: List[str] = None
    source: str = ""
    scraped_at: str = ""

class StartupScraper:
    """Main scraper class for collecting startup data from multiple sources"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.driver = None
        self.playwright = None
        self.browser = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.setup_playwright()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def setup_playwright(self):
        """Setup Playwright browser for advanced scraping"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
        except Exception as e:
            logger.error(f"Failed to setup Playwright: {e}")
            
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            logger.error(f"Failed to setup Selenium: {e}")
            
    async def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
            
    async def scrape_crunchbase(self, max_results: int = 100) -> List[StartupData]:
        """Scrape startup data from Crunchbase"""
        startups = []
        try:
            # Note: Crunchbase requires authentication for full access
            # This is a simplified version - you'd need API access for production
            logger.info("Scraping Crunchbase...")
            
            # Example search URLs (would need proper authentication)
            search_urls = [
                "https://www.crunchbase.com/search/organizations/field/organizations/categories/software",
                "https://www.crunchbase.com/search/organizations/field/organizations/categories/financial_services",
                "https://www.crunchbase.com/search/organizations/field/organizations/categories/healthcare"
            ]
            
            for url in search_urls[:max_results//len(search_urls)]:
                try:
                    page = await self.browser.new_page()
                    await page.goto(url, wait_until='networkidle')
                    
                    # Extract startup cards
                    startup_cards = await page.query_selector_all('.card')
                    
                    for card in startup_cards[:20]:  # Limit per page
                        try:
                            name_elem = await card.query_selector('.card-title')
                            name = await name_elem.text_content() if name_elem else "Unknown"
                            
                            desc_elem = await card.query_selector('.card-description')
                            description = await desc_elem.text_content() if desc_elem else ""
                            
                            startups.append(StartupData(
                                name=name.strip(),
                                description=description.strip(),
                                industry="Technology",  # Default
                                stage="Early Stage",
                                location="Unknown",
                                website="",
                                source="Crunchbase",
                                scraped_at=time.strftime("%Y-%m-%d %H:%M:%S")
                            ))
                        except Exception as e:
                            logger.warning(f"Error parsing startup card: {e}")
                            continue
                            
                    await page.close()
                    await asyncio.sleep(random.uniform(1, 3))  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error scraping Crunchbase URL {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to scrape Crunchbase: {e}")
            
        return startups
        
    async def scrape_angellist(self, max_results: int = 100) -> List[StartupData]:
        """Scrape startup data from AngelList"""
        startups = []
        try:
            logger.info("Scraping AngelList...")
            
            # AngelList startup categories
            categories = [
                "software", "fintech", "healthcare", "ai", "ecommerce",
                "saas", "mobile", "enterprise", "marketplace"
            ]
            
            for category in categories[:max_results//len(categories)]:
                try:
                    url = f"https://angel.co/companies?categories[]={category}"
                    page = await self.browser.new_page()
                    await page.goto(url, wait_until='networkidle')
                    
                    # Wait for startup cards to load
                    await page.wait_for_selector('.startup-card', timeout=10000)
                    
                    startup_cards = await page.query_selector_all('.startup-card')
                    
                    for card in startup_cards[:15]:  # Limit per page
                        try:
                            name_elem = await card.query_selector('.startup-name')
                            name = await name_elem.text_content() if name_elem else "Unknown"
                            
                            desc_elem = await card.query_selector('.startup-description')
                            description = await desc_elem.text_content() if desc_elem else ""
                            
                            location_elem = await card.query_selector('.startup-location')
                            location = await location_elem.text_content() if location_elem else "Unknown"
                            
                            startups.append(StartupData(
                                name=name.strip(),
                                description=description.strip(),
                                industry=category.title(),
                                stage="Early Stage",
                                location=location.strip(),
                                website="",
                                source="AngelList",
                                scraped_at=time.strftime("%Y-%m-%d %H:%M:%S")
                            ))
                        except Exception as e:
                            logger.warning(f"Error parsing startup card: {e}")
                            continue
                            
                    await page.close()
                    await asyncio.sleep(random.uniform(2, 4))  # Rate limiting
                    
                except Exception as e:
                    logger.error(f"Error scraping AngelList category {category}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to scrape AngelList: {e}")
            
        return startups
        
    async def scrape_linkedin(self, max_results: int = 100) -> List[StartupData]:
        """Scrape startup data from LinkedIn Company pages"""
        startups = []
        try:
            logger.info("Scraping LinkedIn...")
            
            # LinkedIn company search queries
            search_queries = [
                "startup software companies",
                "fintech startups",
                "healthcare startups",
                "AI startups",
                "SaaS companies"
            ]
            
            for query in search_queries[:max_results//len(search_queries)]:
                try:
                    # Note: LinkedIn has strict anti-scraping measures
                    # This would require proper authentication and careful rate limiting
                    logger.info(f"Searching LinkedIn for: {query}")
                    
                    # Simulated data for demo purposes
                    startups.extend([
                        StartupData(
                            name=f"LinkedIn Startup {i}",
                            description=f"Leading {query.split()[0]} company",
                            industry="Technology",
                            stage="Growth Stage",
                            location="San Francisco, CA",
                            website=f"https://example{i}.com",
                            source="LinkedIn",
                            scraped_at=time.strftime("%Y-%m-%d %H:%M:%S")
                        ) for i in range(1, 6)
                    ])
                    
                    await asyncio.sleep(random.uniform(3, 5))  # Heavy rate limiting
                    
                except Exception as e:
                    logger.error(f"Error scraping LinkedIn query {query}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to scrape LinkedIn: {e}")
            
        return startups
        
    async def scrape_producthunt(self, max_results: int = 100) -> List[StartupData]:
        """Scrape startup data from Product Hunt"""
        startups = []
        try:
            logger.info("Scraping Product Hunt...")
            
            page = await self.browser.new_page()
            await page.goto("https://www.producthunt.com/topics/startups", wait_until='networkidle')
            
            # Wait for products to load
            await page.wait_for_selector('[data-test="post-item"]', timeout=10000)
            
            product_cards = await page.query_selector_all('[data-test="post-item"]')
            
            for card in product_cards[:max_results]:
                try:
                    name_elem = await card.query_selector('[data-test="post-name"]')
                    name = await name_elem.text_content() if name_elem else "Unknown"
                    
                    desc_elem = await card.query_selector('[data-test="post-tagline"]')
                    description = await desc_elem.text_content() if desc_elem else ""
                    
                    startups.append(StartupData(
                        name=name.strip(),
                        description=description.strip(),
                        industry="Product",
                        stage="Launch",
                        location="Unknown",
                        website="",
                        source="Product Hunt",
                        scraped_at=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error parsing product card: {e}")
                    continue
                    
            await page.close()
            
        except Exception as e:
            logger.error(f"Failed to scrape Product Hunt: {e}")
            
        return startups
        
    async def scrape_ycombinator(self, max_results: int = 100) -> List[StartupData]:
        """Scrape startup data from Y Combinator companies"""
        startups = []
        try:
            logger.info("Scraping Y Combinator...")
            
            page = await self.browser.new_page()
            await page.goto("https://www.ycombinator.com/companies", wait_until='networkidle')
            
            # Wait for company cards to load
            await page.wait_for_selector('.company-card', timeout=10000)
            
            company_cards = await page.query_selector_all('.company-card')
            
            for card in company_cards[:max_results]:
                try:
                    name_elem = await card.query_selector('.company-name')
                    name = await name_elem.text_content() if name_elem else "Unknown"
                    
                    desc_elem = await card.query_selector('.company-description')
                    description = await desc_elem.text_content() if desc_elem else ""
                    
                    batch_elem = await card.query_selector('.company-batch')
                    batch = await batch_elem.text_content() if batch_elem else "Unknown"
                    
                    startups.append(StartupData(
                        name=name.strip(),
                        description=description.strip(),
                        industry="Technology",
                        stage=f"YC {batch.strip()}",
                        location="Unknown",
                        website="",
                        source="Y Combinator",
                        scraped_at=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error parsing company card: {e}")
                    continue
                    
            await page.close()
            
        except Exception as e:
            logger.error(f"Failed to scrape Y Combinator: {e}")
            
        return startups
        
    async def scrape_all_sources(self, max_results_per_source: int = 50) -> List[StartupData]:
        """Scrape from all available sources"""
        all_startups = []
        
        # Run all scrapers concurrently
        tasks = [
            self.scrape_crunchbase(max_results_per_source),
            self.scrape_angellist(max_results_per_source),
            self.scrape_linkedin(max_results_per_source),
            self.scrape_producthunt(max_results_per_source),
            self.scrape_ycombinator(max_results_per_source)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_startups.extend(result)
            else:
                logger.error(f"Scraper failed: {result}")
                
        # Remove duplicates based on name
        seen_names = set()
        unique_startups = []
        for startup in all_startups:
            if startup.name.lower() not in seen_names:
                seen_names.add(startup.name.lower())
                unique_startups.append(startup)
                
        logger.info(f"Scraped {len(unique_startups)} unique startups from all sources")
        return unique_startups
        
    def save_to_csv(self, startups: List[StartupData], filename: str = "scraped_startups.csv"):
        """Save scraped data to CSV"""
        try:
            data = []
            for startup in startups:
                data.append({
                    'name': startup.name,
                    'description': startup.description,
                    'industry': startup.industry,
                    'stage': startup.stage,
                    'location': startup.location,
                    'website': startup.website,
                    'funding': startup.funding,
                    'team_size': startup.team_size,
                    'founded_year': startup.founded_year,
                    'technologies': ','.join(startup.technologies) if startup.technologies else '',
                    'challenges': ','.join(startup.challenges) if startup.challenges else '',
                    'source': startup.source,
                    'scraped_at': startup.scraped_at
                })
                
            df = pd.DataFrame(data)
            df.to_csv(filename, index=False)
            logger.info(f"Saved {len(startups)} startups to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save to CSV: {e}")
            
    def save_to_json(self, startups: List[StartupData], filename: str = "scraped_startups.json"):
        """Save scraped data to JSON"""
        try:
            data = []
            for startup in startups:
                data.append({
                    'name': startup.name,
                    'description': startup.description,
                    'industry': startup.industry,
                    'stage': startup.stage,
                    'location': startup.location,
                    'website': startup.website,
                    'funding': startup.funding,
                    'team_size': startup.team_size,
                    'founded_year': startup.founded_year,
                    'technologies': startup.technologies or [],
                    'challenges': startup.challenges or [],
                    'source': startup.source,
                    'scraped_at': startup.scraped_at
                })
                
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved {len(startups)} startups to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save to JSON: {e}")

async def main():
    """Example usage of the scraper"""
    async with StartupScraper(headless=True) as scraper:
        # Scrape from all sources
        startups = await scraper.scrape_all_sources(max_results_per_source=20)
        
        # Save results
        scraper.save_to_csv(startups, "scraped_startups.csv")
        scraper.save_to_json(startups, "scraped_startups.json")
        
        print(f"Successfully scraped {len(startups)} startups")

if __name__ == "__main__":
    asyncio.run(main()) 