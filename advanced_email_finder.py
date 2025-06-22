#!/usr/bin/env python3
"""
🔍 ADVANCED EMAIL FINDER
Professional email discovery using multiple real sources - NO GUESSING!
"""

import requests
import re
import time
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class AdvancedEmailFinder:
    """Professional email discovery using multiple real sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        
    def find_real_emails(self, company_name, website, description=""):
        """Find real email addresses using multiple professional sources"""
        logger.info(f"🔍 ADVANCED EMAIL DISCOVERY: {company_name}")
        
        emails_found = []
        
        # Method 1: Deep website scraping
        website_emails = self._deep_website_scraping(website, company_name)
        emails_found.extend(website_emails)
        
        # Method 2: LinkedIn search
        linkedin_emails = self._search_linkedin(company_name)
        emails_found.extend(linkedin_emails)
        
        # Method 3: GitHub search
        github_emails = self._search_github(company_name, website)
        emails_found.extend(github_emails)
        
        # Method 4: News and press mentions
        news_emails = self._search_news_mentions(company_name)
        emails_found.extend(news_emails)
        
        # Clean and prioritize emails
        cleaned_emails = self._clean_and_validate_emails(emails_found, website)
        
        if cleaned_emails:
            logger.info(f"✅ FOUND {len(cleaned_emails)} REAL EMAILS: {cleaned_emails}")
            return cleaned_emails[0]  # Return best email
        else:
            logger.warning(f"❌ NO REAL EMAILS FOUND for {company_name}")
            return None
    
    def _deep_website_scraping(self, website, company_name):
        """Deep scraping of company website for email addresses"""
        emails = []
        
        if not website:
            return emails
        
        try:
            pages_to_check = [
                '', '/contact', '/contact-us', '/about', '/about-us',
                '/team', '/leadership', '/founders', '/careers', '/jobs',
                '/press', '/media', '/support', '/help'
            ]
            
            for page in pages_to_check:
                try:
                    url = urljoin(website, page)
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Extract emails from page content
                        page_emails = self._extract_emails_from_content(response.text)
                        emails.extend(page_emails)
                        
                        # Check for mailto links
                        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.I))
                        for link in mailto_links:
                            email = link['href'].replace('mailto:', '').split('?')[0]
                            if self._is_valid_email(email):
                                emails.append(email)
                        
                        time.sleep(0.5)  # Be respectful
                        
                except Exception as e:
                    logger.debug(f"Error scraping {url}: {e}")
                    continue
                    
        except Exception as e:
            logger.debug(f"Error in deep website scraping: {e}")
        
        return emails
    
    def _search_linkedin(self, company_name):
        """Search for company LinkedIn and extract contact info"""
        emails = []
        
        try:
            search_query = f'"{company_name}" site:linkedin.com contact email'
            search_url = f"https://www.google.com/search?q={search_query}"
            
            response = self.session.get(search_url, timeout=10)
            if response.status_code == 200:
                emails.extend(self._extract_emails_from_content(response.text))
                
        except Exception as e:
            logger.debug(f"Error searching LinkedIn: {e}")
        
        return emails
    
    def _search_github(self, company_name, website):
        """Search GitHub for organization contact info"""
        emails = []
        
        try:
            domain = urlparse(website).netloc if website else ""
            search_queries = [
                f'"{company_name}" site:github.com email',
                f'{domain} site:github.com contact' if domain else ""
            ]
            
            for query in search_queries:
                if not query:
                    continue
                    
                search_url = f"https://www.google.com/search?q={query}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    emails.extend(self._extract_emails_from_content(response.text))
                    
        except Exception as e:
            logger.debug(f"Error searching GitHub: {e}")
        
        return emails
    
    def _search_news_mentions(self, company_name):
        """Search news and press releases for contact info"""
        emails = []
        
        try:
            search_queries = [
                f'"{company_name}" contact email press',
                f'"{company_name}" media contact',
                f'"{company_name}" founder email'
            ]
            
            for query in search_queries:
                search_url = f"https://www.google.com/search?q={query}"
                response = self.session.get(search_url, timeout=10)
                
                if response.status_code == 200:
                    emails.extend(self._extract_emails_from_content(response.text))
                    
        except Exception as e:
            logger.debug(f"Error searching news mentions: {e}")
        
        return emails
    
    def _extract_emails_from_content(self, content):
        """Extract valid email addresses from text content"""
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
        potential_emails = email_pattern.findall(content)
        
        valid_emails = []
        for email in potential_emails:
            if self._is_valid_email(email):
                valid_emails.append(email.lower())
        
        return valid_emails
    
    def _is_valid_email(self, email):
        """Validate email address and filter unwanted patterns"""
        if not email or '@' not in email:
            return False
        
        unwanted_patterns = [
            'noreply', 'no-reply', 'donotreply', 'example.com', 'test.com',
            'privacy', 'legal', 'unsubscribe', 'marketing', 'spam',
            'abuse', 'postmaster', 'webmaster', 'hostmaster'
        ]
        
        email_lower = email.lower()
        if any(pattern in email_lower for pattern in unwanted_patterns):
            return False
        
        if len(email) > 254:
            return False
            
        local, domain = email.split('@', 1)
        if len(local) > 64:
            return False
        
        return True
    
    def _clean_and_validate_emails(self, emails, website):
        """Clean, deduplicate, and prioritize emails"""
        if not emails:
            return []
        
        unique_emails = list(set(email.lower().strip() for email in emails if email))
        valid_emails = [email for email in unique_emails if self._is_valid_email(email)]
        
        if not valid_emails:
            return []
        
        domain = urlparse(website).netloc if website else ""
        
        def email_priority(email):
            email_lower = email.lower()
            local_part = email.split('@')[0].lower()
            email_domain = email.split('@')[1].lower()
            
            # Highest priority: emails from company domain
            if domain and email_domain == domain:
                if local_part in ['contact', 'info', 'hello']:
                    return 1
                elif local_part in ['team', 'support', 'careers']:
                    return 2
                else:
                    return 3
            
            # Medium priority: professional email patterns
            if local_part in ['contact', 'info', 'hello', 'team']:
                return 4
            
            return 5
        
        sorted_emails = sorted(valid_emails, key=email_priority)
        logger.info(f"📧 PRIORITIZED EMAILS: {sorted_emails}")
        return sorted_emails 