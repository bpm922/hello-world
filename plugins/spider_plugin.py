"""
Spider Plugin - Web Crawling and Link Discovery

This plugin provides comprehensive web crawling capabilities:
- Website structure mapping
- Link discovery and categorization
- Endpoint enumeration
- Technology stack detection
"""

import logging
import re
import requests
import time
from typing import Dict, List, Any, Set
from urllib.parse import urljoin, urlparse
from collections import defaultdict
from bs4 import BeautifulSoup
from .base_plugin import BasePlugin, PluginResult


class SpiderPlugin(BasePlugin):
    """Plugin for web crawling and website structure mapping"""
    
    @property
    def description(self) -> str:
        return "Web crawling and link discovery for website structure mapping"
    
    @property
    def search_types(self) -> List[str]:
        return ['url', 'domain']
    
    def search(self, query: str, search_type: str = 'url', **kwargs) -> PluginResult:
        """
        Crawl a website and map its structure
        
        Args:
            query: Target URL or domain
            search_type: Type of search ('url' or 'domain')
            **kwargs: Additional parameters (max_depth, max_pages, timeout, follow_redirects)
            
        Returns:
            PluginResult with crawled data and structure
        """
        start_time = time.time()
        
        try:
            # Normalize URL
            url = self._normalize_url(query, search_type)
            
            # Get parameters
            max_depth = kwargs.get('max_depth', 3)
            max_pages = kwargs.get('max_pages', 200)
            timeout = kwargs.get('timeout', 10)
            follow_redirects = kwargs.get('follow_redirects', True)
            
            self.log_info(f"Starting Spider crawl on {url} (max_depth: {max_depth}, max_pages: {max_pages})")
            
            # Results storage
            crawled_pages = {}
            url_tree = defaultdict(list)
            link_categories = {
                'internal': set(),
                'external': set(),
                'javascript': set(),
                'forms': set(),
                'api_endpoints': set(),
                'assets': set()
            }
            
            # Technology stack indicators
            technologies = set()
            
            # Crawling
            visited: Set[str] = set()
            to_visit = [(url, None, 0)]  # (url, parent_url, depth)
            pages_crawled = 0
            
            while to_visit and pages_crawled < max_pages:
                current_url, parent_url, depth = to_visit.pop(0)
                
                if current_url in visited or depth > max_depth:
                    continue
                
                try:
                    self.log_info(f"Crawling: {current_url} (depth: {depth}, pages: {pages_crawled})")
                    
                    response = requests.get(
                        current_url,
                        timeout=timeout,
                        allow_redirects=follow_redirects
                    )
                    response.raise_for_status()
                    
                    visited.add(current_url)
                    pages_crawled += 1
                    
                    # Parse HTML
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract page information
                    page_info = {
                        'url': current_url,
                        'status_code': response.status_code,
                        'title': self._extract_title(soup),
                        'description': self._extract_description(soup),
                        'depth': depth,
                        'links': {
                            'total': 0,
                            'internal': 0,
                            'external': 0
                        },
                        'forms': [],
                        'scripts': [],
                        'technologies': []
                    }
                    
                    # Detect technologies
                    detected_techs = self._detect_technologies(soup, response.headers, response.text)
                    technologies.update(detected_techs)
                    page_info['technologies'] = list(detected_techs)
                    
                    # Extract and categorize links
                    links = self._extract_all_links(soup, current_url, visited)
                    
                    for link_info in links:
                        link_url = link_info['url']
                        link_type = link_info['type']
                        
                        # Update page info
                        page_info['links']['total'] += 1
                        if link_type == 'internal':
                            page_info['links']['internal'] += 1
                            link_categories['internal'].add(link_url)
                            # Add to crawl queue if within depth limit
                            if depth < max_depth and link_url not in visited:
                                to_visit.append((link_url, current_url, depth + 1))
                        elif link_type == 'external':
                            page_info['links']['external'] += 1
                            link_categories['external'].add(link_url)
                        elif link_type == 'javascript':
                            link_categories['javascript'].add(link_url)
                        elif link_type == 'api_endpoint':
                            link_categories['api_endpoints'].add(link_url)
                        elif link_type == 'asset':
                            link_categories['assets'].add(link_url)
                    
                    # Build URL tree
                    if parent_url:
                        url_tree[parent_url].append(current_url)
                    else:
                        url_tree['root'].append(current_url)
                    
                    # Extract forms
                    forms = self._extract_forms(soup, current_url)
                    page_info['forms'] = forms
                    link_categories['forms'].update([f['action'] for f in forms if f['action']])
                    
                    # Extract scripts
                    scripts = self._extract_scripts(soup, current_url)
                    page_info['scripts'] = scripts
                    
                    # Store page info
                    crawled_pages[current_url] = page_info
                    
                    # Be respectful to the server
                    time.sleep(0.5)
                    
                except requests.RequestException as e:
                    self.log_warning(f"Failed to crawl {current_url}: {str(e)}")
                    visited.add(current_url)
                    continue
                except Exception as e:
                    self.log_error(f"Error processing {current_url}: {str(e)}")
                    continue
            
            # Prepare final results
            data = {
                'target_url': url,
                'pages_crawled': pages_crawled,
                'total_links': sum(len(s) for s in link_categories.values()),
                'link_categories': {
                    'internal': sorted(list(link_categories['internal'])),
                    'external': sorted(list(link_categories['external'])),
                    'javascript': sorted(list(link_categories['javascript'])),
                    'forms': sorted(list(link_categories['forms'])),
                    'api_endpoints': sorted(list(link_categories['api_endpoints'])),
                    'assets': sorted(list(link_categories['assets']))
                },
                'technologies_detected': sorted(list(technologies)),
                'url_tree': dict(url_tree),
                'pages': crawled_pages
            }
            
            execution_time = time.time() - start_time
            
            self.log_info(f"Spider crawl completed. Pages: {pages_crawled}, "
                         f"Internal links: {len(data['link_categories']['internal'])}, "
                         f"Technologies: {len(data['technologies_detected'])}")
            
            return PluginResult(
                source=self.name,
                search_type=search_type,
                query=query,
                data=[data],
                metadata={
                    'pages_crawled': pages_crawled,
                    'max_depth': max_depth,
                    'technologies_count': len(technologies)
                },
                success=True,
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.log_error(f"Spider search failed: {str(e)}")
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
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        if soup.title:
            return soup.title.string.strip() if soup.title.string else ''
        return ''
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            return meta['content'].strip()
        return ''
    
    def _extract_all_links(self, soup: BeautifulSoup, base_url: str, visited: Set[str]) -> List[Dict[str, Any]]:
        """Extract and categorize all links from the page"""
        links = []
        base_domain = urlparse(base_url).netloc
        
        # Extract from <a> tags
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:', 'data:')):
                continue
            
            full_url = urljoin(base_url, href)
            
            # Determine link type
            parsed = urlparse(full_url)
            
            if parsed.netloc == base_domain:
                link_type = 'internal'
            else:
                link_type = 'external'
            
            links.append({
                'url': full_url,
                'type': link_type,
                'text': a_tag.get_text().strip()[:100],
                'tag': 'a'
            })
        
        # Extract JavaScript links
        for script in soup.find_all('script', src=True):
            src = urljoin(base_url, script['src'])
            links.append({
                'url': src,
                'type': 'javascript',
                'tag': 'script'
            })
        
        # Extract API endpoints from inline JavaScript
        for script in soup.find_all('script'):
            if script.string:
                # Look for fetch/axios calls
                api_pattern = r'(?:fetch|axios\.get|axios\.post|ajax)\s*\(\s*["\']([^"\']+)["\']'
                matches = re.findall(api_pattern, script.string)
                for match in matches:
                    full_url = urljoin(base_url, match)
                    links.append({
                        'url': full_url,
                        'type': 'api_endpoint',
                        'tag': 'inline_js'
                    })
        
        # Extract assets (images, stylesheets, etc.)
        asset_tags = {
            'img': 'src',
            'link': 'href',
            'video': 'src',
            'audio': 'src'
        }
        
        for tag, attr in asset_tags.items():
            for element in soup.find_all(tag, {attr: True}):
                src = element[attr]
                if src and not src.startswith(('data:', '#')):
                    full_url = urljoin(base_url, src)
                    links.append({
                        'url': full_url,
                        'type': 'asset',
                        'tag': tag
                    })
        
        return links
    
    def _extract_forms(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract form information"""
        forms = []
        
        for form in soup.find_all('form'):
            action = form.get('action', '')
            if action:
                action = urljoin(base_url, action)
            
            method = form.get('method', 'GET').upper()
            
            # Extract form fields
            fields = []
            for input_tag in form.find_all('input'):
                fields.append({
                    'type': input_tag.get('type', 'text'),
                    'name': input_tag.get('name', ''),
                    'id': input_tag.get('id', '')
                })
            
            for select in form.find_all('select'):
                fields.append({
                    'type': 'select',
                    'name': select.get('name', ''),
                    'id': select.get('id', '')
                })
            
            forms.append({
                'action': action,
                'method': method,
                'fields': fields
            })
        
        return forms
    
    def _extract_scripts(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
        """Extract JavaScript file information"""
        scripts = []
        
        for script in soup.find_all('script', src=True):
            scripts.append({
                'url': urljoin(base_url, script['src']),
                'async': script.get('async') is not None,
                'defer': script.get('defer') is not None
            })
        
        return scripts
    
    def _detect_technologies(self, soup: BeautifulSoup, headers: Dict[str, str], html: str) -> List[str]:
        """Detect technologies used by the website"""
        technologies = []
        
        # Check HTTP headers
        server = headers.get('Server', '').lower()
        if 'nginx' in server:
            technologies.append('Nginx')
        if 'apache' in server:
            technologies.append('Apache')
        if 'cloudflare' in server:
            technologies.append('Cloudflare')
        if 'iis' in server or 'microsoft-iis' in server:
            technologies.append('IIS')
        
        # Check meta tags
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator:
            content = generator.get('content', '').lower()
            if 'wordpress' in content:
                technologies.append('WordPress')
            if 'drupal' in content:
                technologies.append('Drupal')
            if 'joomla' in content:
                technologies.append('Joomla')
        
        # Check for common JavaScript libraries
        html_lower = html.lower()
        
        if 'jquery' in html_lower:
            technologies.append('jQuery')
        if 'react' in html_lower or 'reactjs' in html_lower:
            technologies.append('React')
        if 'vue.js' in html_lower or 'vuejs' in html_lower:
            technologies.append('Vue.js')
        if 'angular' in html_lower:
            technologies.append('Angular')
        if 'bootstrap' in html_lower:
            technologies.append('Bootstrap')
        if 'tailwind' in html_lower:
            technologies.append('Tailwind CSS')
        if 'lodash' in html_lower:
            technologies.append('Lodash')
        if 'moment.js' in html_lower:
            technologies.append('Moment.js')
        
        # Check for analytics
        if 'google-analytics' in html_lower or 'googletagmanager' in html_lower:
            technologies.append('Google Analytics')
        if 'hotjar' in html_lower:
            technologies.append('Hotjar')
        
        # Check for CDN
        if 'cloudflare.com/ajax' in html_lower or 'cdnjs.cloudflare.com' in html_lower:
            technologies.append('CDN')
        if 'ajax.googleapis.com' in html_lower:
            technologies.append('Google CDN')
        
        return list(set(technologies))
