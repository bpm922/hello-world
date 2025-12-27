"""
Photon Plugin - Website Reconnaissance and Data Extraction

Photon is a crawler designed for OSINT that extracts:
- URLs from a website
- Emails
- Phone numbers
- Social media accounts
- Important files
- JavaScript files and endpoints
"""

import logging
import re
import requests
import time
from typing import Dict, List, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from .base_plugin import BasePlugin, PluginResult


class PhotonPlugin(BasePlugin):
    """Plugin for website reconnaissance using Photon-style crawling"""
    
    @property
    def description(self) -> str:
        return "Website reconnaissance and data extraction tool"
    
    @property
    def search_types(self) -> List[str]:
        return ['url', 'domain']
    
    def search(self, query: str, search_type: str = 'url', **kwargs) -> PluginResult:
        """
        Crawl a website and extract data
        
        Args:
            query: Target URL or domain
            search_type: Type of search ('url' or 'domain')
            **kwargs: Additional parameters (max_depth, max_pages, timeout)
            
        Returns:
            PluginResult with extracted data
        """
        start_time = time.time()
        
        try:
            # Normalize URL
            url = self._normalize_url(query, search_type)
            
            # Get parameters
            max_depth = kwargs.get('max_depth', 2)
            max_pages = kwargs.get('max_pages', 100)
            timeout = kwargs.get('timeout', 10)
            
            self.log_info(f"Starting Photon crawl on {url}")
            
            # Results storage
            results = {
                'urls': set(),
                'emails': set(),
                'phone_numbers': set(),
                'social_accounts': set(),
                'javascript_files': set(),
                'files': set(),
                'endpoints': set()
            }
            
            # Crawling
            crawled = set()
            to_crawl = [(url, 0)]
            pages_crawled = 0
            
            while to_crawl and pages_crawled < max_pages:
                current_url, depth = to_crawl.pop(0)
                
                if current_url in crawled or depth > max_depth:
                    continue
                
                try:
                    self.log_info(f"Crawling: {current_url} (depth: {depth})")
                    
                    response = requests.get(current_url, timeout=timeout)
                    response.raise_for_status()
                    
                    crawled.add(current_url)
                    pages_crawled += 1
                    results['urls'].add(current_url)
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract data from page
                    self._extract_emails(soup, results['emails'])
                    self._extract_phone_numbers(soup, results['phone_numbers'])
                    self._extract_social_accounts(soup, results['social_accounts'])
                    self._extract_javascript(soup, current_url, results['javascript_files'])
                    self._extract_files(soup, current_url, results['files'])
                    self._extract_endpoints(response.text, results['endpoints'])
                    
                    # Extract links for further crawling
                    if depth < max_depth:
                        new_links = self._extract_links(soup, current_url, crawled)
                        for link in new_links:
                            to_crawl.append((link, depth + 1))
                            
                except requests.RequestException as e:
                    self.log_warning(f"Failed to crawl {current_url}: {str(e)}")
                    continue
                except Exception as e:
                    self.log_error(f"Error processing {current_url}: {str(e)}")
                    continue
            
            # Convert sets to lists
            data = {
                'urls': list(results['urls']),
                'emails': list(results['emails']),
                'phone_numbers': list(results['phone_numbers']),
                'social_accounts': list(results['social_accounts']),
                'javascript_files': list(results['javascript_files']),
                'files': list(results['files']),
                'endpoints': list(results['endpoints']),
                'pages_crawled': pages_crawled,
                'max_depth_reached': max_depth
            }
            
            execution_time = time.time() - start_time
            
            self.log_info(f"Crawl completed. Pages: {pages_crawled}, URLs: {len(data['urls'])}, "
                         f"Emails: {len(data['emails'])}, Endpoints: {len(data['endpoints'])}")
            
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[data],
                metadata={'pages_crawled': pages_crawled, 'max_depth': max_depth},
                success=True,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_error(f"Photon search failed: {str(e)}")
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[],
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def _normalize_url(self, query: str, search_type: str) -> str:
        """Normalize URL to ensure it has a protocol"""
        url = query.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str, crawled: set) -> List[str]:
        """Extract all links from the page"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                continue
            
            # Make absolute URL
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # Only crawl same domain
            if parsed.netloc == base_domain and full_url not in crawled:
                links.append(full_url)
        
        return list(set(links))
    
    def _extract_emails(self, soup: BeautifulSoup, emails: set):
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        text = soup.get_text()
        matches = re.findall(email_pattern, text)
        emails.update(matches)
    
    def _extract_phone_numbers(self, soup: BeautifulSoup, phones: set):
        """Extract phone numbers from text"""
        phone_patterns = [
            r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'  # International
        ]
        text = soup.get_text()
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            phones.update(matches)
    
    def _extract_social_accounts(self, soup: BeautifulSoup, social: set):
        """Extract social media account links"""
        social_domains = [
            'twitter.com', 'facebook.com', 'linkedin.com', 'instagram.com',
            'youtube.com', 'github.com', 'reddit.com', 'tiktok.com'
        ]
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            for domain in social_domains:
                if domain in href:
                    social.add(href)
    
    def _extract_javascript(self, soup: BeautifulSoup, base_url: str, js_files: set):
        """Extract JavaScript file URLs"""
        for script in soup.find_all('script', src=True):
            src = urljoin(base_url, script['src'])
            if src.endswith('.js'):
                js_files.add(src)
    
    def _extract_files(self, soup: BeautifulSoup, base_url: str, files: set):
        """Extract important files"""
        file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                          '.zip', '.rar', '.tar', '.gz', '.sql', '.xml', '.json']
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if any(href.lower().endswith(ext) for ext in file_extensions):
                files.add(urljoin(base_url, href))
    
    def _extract_endpoints(self, html_content: str, endpoints: set):
        """Extract API endpoints from JavaScript content"""
        # Look for API-like patterns in JavaScript
        api_patterns = [
            r'["\'](?:/api/[^"\']+|/v\d+/[^"\']+)[ "\']',
            r'fetch\(["\']([^"\']+)["\']',
            r'ajax\(["\']([^"\']+)["\']'
        ]
        
        for pattern in api_patterns:
            matches = re.findall(pattern, html_content)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                # Clean up the match
                endpoint = match.strip('"\'')
                if endpoint.startswith('/'):
                    endpoints.add(endpoint)
