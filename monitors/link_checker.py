"""
Link Checker - Crawls and validates all links on the website.
"""
import asyncio
import aiohttp
from typing import Any, Dict, List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
import re
from .base_monitor import BaseMonitor, MonitorResult

class LinkChecker(BaseMonitor):
    """Crawls and validates internal and external links."""
    
    @property
    def name(self) -> str:
        return "links"
    
    def __init__(self, config: Dict[str, Any], base_url: str):
        super().__init__(config, base_url)
        self.link_config = config.get('link_checker', {})
        self.max_depth = self.link_config.get('max_depth', 3)
        self.max_links = self.link_config.get('max_links', 500)
        self.max_links_per_page = self.link_config.get('max_links_per_page', 0)  # 0 = unlimited
        self.timeout = self.link_config.get('timeout', 10)
        self.check_external = self.link_config.get('check_external', True)
        self.ignore_patterns = self.link_config.get('ignore_patterns', [])
        
        # Header/Footer exclusion options
        self.ignore_header = config.get('ignore_header', False)
        self.ignore_footer = config.get('ignore_footer', False)
        self.main_content_only = config.get('main_content_only', False)
        
        # Browser mode settings
        self.use_browser = config.get('use_browser', False)
        self.headless = config.get('headless', True)
        self.browser = None
        
        self.checked_urls: Set[str] = set()
        self.broken_links: List[Dict] = []
        self.redirect_chains: List[Dict] = []
    
    def run(self) -> List[MonitorResult]:
        """Run link checks."""
        self.results = []
        self.checked_urls = set()
        self.broken_links = []
        self.all_links_per_page = {}  # Store all links per page for verification
        
        self.logger.info(f"Starting link checker (max depth: {self.max_depth})")
        
        # Initialize browser if needed
        if self.use_browser:
            try:
                from utils.browser import BrowserManager
                self.browser = BrowserManager(headless=self.headless)
                if not self.browser.start():
                    self.logger.warning("Browser failed to start, falling back to HTTP requests")
                    self.use_browser = False
                    self.browser = None
                else:
                    mode = "visible" if not self.headless else "headless"
                    self.logger.info(f"Browser started in {mode} mode")
            except Exception as e:
                self.logger.warning(f"Browser init failed: {e}, falling back to HTTP requests")
                self.use_browser = False
                self.browser = None
        
        try:
            # First, check links on each critical page individually
            self._check_links_per_page()
            
            # Then run the full site crawl (only if not in browser mode - browser mode is slower)
            if not self.use_browser:
                try:
                    asyncio.run(self._crawl_site())
                except Exception as e:
                    self.logger.error(f"Async crawl failed, using sync: {e}")
                    self._crawl_site_sync()
        finally:
            # Cleanup browser
            if self.browser:
                self.browser.stop()
                self.browser = None
        
        # Summarize results with detailed broken link info
        if self.broken_links:
            # Create a detailed summary of broken links
            broken_link_details = []
            for bl in self.broken_links:
                detail = {
                    'url': bl.get('url', 'Unknown'),
                    'link_text': bl.get('text', 'N/A'),
                    'status': bl.get('status', 'Unknown'),
                    'status_message': bl.get('status_message', 'Unknown error'),
                    'found_on_page': bl.get('source', 'Unknown')
                }
                broken_link_details.append(detail)
            
            self.add_result('error', 
                f'Found {len(self.broken_links)} broken anchor links across site',
                severity='high',
                details={
                    'summary': f'Clicked {len(self.checked_urls)} anchor links, found {len(self.broken_links)} broken',
                    'broken_links': broken_link_details,
                    'total_checked': len(self.checked_urls)
                })
        else:
            self.add_result('success',
                f'All {len(self.checked_urls)} anchor links are valid',
                details={
                    'summary': 'All anchor tag links were clicked and validated successfully',
                    'total_checked': len(self.checked_urls)
                })
        
        return self.results
    
    def _get_content_scope(self, soup):
        """Get the soup content based on header/footer exclusion settings.
        
        Returns: (soup_to_search, scope_description)
        """
        if self.main_content_only:
            # Try to find main content area
            main_content = (
                soup.find('main') or 
                soup.find('article') or 
                soup.find(class_='content') or
                soup.find(class_='main-content') or
                soup.find(id='content') or
                soup.find(id='main')
            )
            if main_content:
                self.logger.info("Checking main content area only")
                return main_content, "main content only"
        
        # Remove header/footer if requested
        if self.ignore_header or self.ignore_footer:
            # Make a copy to avoid modifying original
            from copy import copy
            soup_copy = copy(soup)
            
            removed = []
            if self.ignore_header:
                # Remove header elements
                for tag in ['header', 'nav']:
                    for elem in soup_copy.find_all(tag):
                        elem.decompose()
                        removed.append(tag)
                # Remove by class/id
                for selector in ['.header', '.nav', '.navbar', '.navigation', '#header', '#nav', '#navbar']:
                    for elem in soup_copy.select(selector):
                        elem.decompose()
                        removed.append(selector)
                        
            if self.ignore_footer:
                # Remove footer elements
                for elem in soup_copy.find_all('footer'):
                    elem.decompose()
                    removed.append('footer')
                for selector in ['.footer', '#footer', '.site-footer']:
                    for elem in soup_copy.select(selector):
                        elem.decompose()
                        removed.append(selector)
            
            if removed:
                scope = []
                if self.ignore_header:
                    scope.append("no header")
                if self.ignore_footer:
                    scope.append("no footer")
                return soup_copy, ", ".join(scope)
        
        return soup, "full page"
    
    def _check_links_per_page(self):
        """Check all anchor tag links on each critical page by clicking (GET request) and report per-page results."""
        import time
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages:
            url = self.get_full_url(page)
            page_broken = []
            page_slow = []
            page_links = []
            total_time = 0
            
            # Check for cancellation
            if self.is_cancelled():
                self.logger.warning("Link check cancelled by user")
                break
            
            try:
                # Fetch page content - use browser if available
                if self.browser:
                    success, status, load_time = self.browser.navigate(url)
                    if not success:
                        continue
                    html_content = self.browser.get_page_source()
                    soup = BeautifulSoup(html_content, 'html.parser')
                else:
                    response = requests.get(url, timeout=15,
                        headers={'User-Agent': 'WordPress-Monitor/1.0'})
                    
                    if response.status_code != 200:
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                
                # Apply content scope filtering (ignore header/footer if requested)
                filtered_soup, scope_desc = self._get_content_scope(soup)
                if scope_desc != "full page":
                    self.logger.info(f"Scope: {scope_desc}")
                
                # Get only anchor tag (<a>) links on this page
                links = []
                if self.browser:
                    # Use browser to get links (more accurate for JS-rendered pages)
                    browser_links = self.browser.get_all_links()
                    for link in browser_links:
                        full_url = link['url'].split('#')[0]
                        if full_url and not full_url.startswith(('javascript:', 'mailto:', 'tel:')):
                            if full_url not in [l['url'] for l in links]:
                                links.append({'url': full_url, 'text': link['text'][:50]})
                else:
                    for tag in filtered_soup.find_all('a'):
                        href = tag.get('href')
                        if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                            full_url = urljoin(url, href).split('#')[0]
                            link_text = tag.get_text(strip=True)[:50] or href[:50]
                            if full_url not in [l['url'] for l in links]:  # Dedupe
                                links.append({'url': full_url, 'text': link_text})
                
                # Apply per-page limit if set
                total_links = len(links)
                if self.max_links_per_page > 0 and len(links) > self.max_links_per_page:
                    links = links[:self.max_links_per_page]
                    self.logger.info(f"Limiting to {self.max_links_per_page} of {total_links} links on {page}")
                
                self.logger.info(f"Checking {len(links)} anchor links on {page}")
                
                for link_info in links:
                    # Check for cancellation
                    if self.is_cancelled():
                        self.logger.warning("Link check cancelled by user")
                        break
                    
                    link_url = link_info['url']
                    link_text = link_info['text']
                    
                    if link_url in self.checked_urls:
                        continue
                    
                    try:
                        start_time = time.time()
                        # Use GET request to simulate actually clicking the link
                        link_response = requests.get(link_url, timeout=10,
                            allow_redirects=True,
                            headers={'User-Agent': 'WordPress-Monitor/1.0'})
                        load_time = (time.time() - start_time) * 1000
                        
                        self.checked_urls.add(link_url)
                        total_time += load_time
                        
                        if link_response.status_code >= 400:
                            # Detailed error for broken link
                            error_detail = {
                                'link_url': link_url,
                                'link_text': link_text,
                                'status_code': link_response.status_code,
                                'status_message': self._get_status_message(link_response.status_code),
                                'found_on_page': page,
                                'page_url': url
                            }
                            page_broken.append(error_detail)
                            self.broken_links.append({
                                'url': link_url,
                                'text': link_text,
                                'status': link_response.status_code,
                                'status_message': self._get_status_message(link_response.status_code),
                                'source': page
                            })
                        else:
                            # Track slow links (> 3 seconds)
                            if load_time > 3000:
                                page_slow.append({
                                    'url': link_url,
                                    'text': link_text,
                                    'response_time_ms': round(load_time, 0)
                                })
                            
                            page_links.append({
                                'url': link_url,
                                'text': link_text,
                                'status_code': link_response.status_code,
                                'response_time_ms': round(load_time, 0)
                            })
                            
                    except requests.exceptions.Timeout:
                        error_detail = {
                            'link_url': link_url,
                            'link_text': link_text,
                            'status_code': 'timeout',
                            'status_message': 'Request timed out - link may be unreachable',
                            'found_on_page': page,
                            'page_url': url
                        }
                        page_broken.append(error_detail)
                        self.broken_links.append({
                            'url': link_url,
                            'text': link_text,
                            'status': 'timeout',
                            'status_message': 'Request timed out',
                            'source': page
                        })
                    except requests.exceptions.SSLError as e:
                        error_detail = {
                            'link_url': link_url,
                            'link_text': link_text,
                            'status_code': 'SSL_ERROR',
                            'status_message': f'SSL Certificate error: {str(e)[:100]}',
                            'found_on_page': page,
                            'page_url': url
                        }
                        page_broken.append(error_detail)
                        self.broken_links.append({
                            'url': link_url,
                            'text': link_text,
                            'status': 'SSL_ERROR',
                            'status_message': 'SSL Certificate error',
                            'source': page
                        })
                    except requests.exceptions.ConnectionError as e:
                        error_detail = {
                            'link_url': link_url,
                            'link_text': link_text,
                            'status_code': 'CONNECTION_ERROR',
                            'status_message': f'Connection failed: {str(e)[:100]}',
                            'found_on_page': page,
                            'page_url': url
                        }
                        page_broken.append(error_detail)
                        self.broken_links.append({
                            'url': link_url,
                            'text': link_text,
                            'status': 'CONNECTION_ERROR',
                            'status_message': 'Connection failed',
                            'source': page
                        })
                    except Exception as e:
                        # Log all errors with details
                        if not self._is_internal(link_url):
                            self.logger.debug(f"External link check failed: {link_url[:50]}: {e}")
                        else:
                            error_detail = {
                                'link_url': link_url,
                                'link_text': link_text,
                                'status_code': 'ERROR',
                                'status_message': f'Unknown error: {str(e)[:100]}',
                                'found_on_page': page,
                                'page_url': url
                            }
                            page_broken.append(error_detail)
                            self.broken_links.append({
                                'url': link_url,
                                'text': link_text,
                                'status': 'ERROR',
                                'status_message': str(e)[:100],
                                'source': page
                            })
                
                avg_time = round(total_time / len(page_links), 0) if page_links else 0
                
                # Report broken links on this page with detailed error info
                if page_broken:
                    self.add_result('error', 
                        f'{len(page_broken)} broken anchor links on {page}',
                        severity='high', url=url,
                        details={
                            'error_summary': f'Found {len(page_broken)} broken links by clicking each anchor tag',
                            'broken_links': page_broken,  # Full details for all broken links
                            'total_anchor_links': len(links)
                        })
                
                # Report slow links on this page
                if page_slow:
                    self.add_result('warning',
                        f'{len(page_slow)} slow anchor links on {page} (>3s)',
                        severity='medium', url=url,
                        details={
                            'slow_links': page_slow,
                            'avg_response_time_ms': avg_time
                        })
                
                # Store all checked links for this page (for verification report)
                all_page_links = page_links + page_broken
                self.all_links_per_page[page] = {
                    'page_url': url,
                    'total_found': len(links),
                    'checked_count': len(all_page_links),
                    'valid_count': len(page_links),
                    'broken_count': len(page_broken),
                    'slow_count': len(page_slow),
                    'avg_response_time_ms': avg_time,
                    'all_links': sorted(all_page_links, key=lambda x: x.get('url', x.get('link_url', '')))
                }
                
                # Success summary for this page
                if not page_broken:
                    self.add_result('success',
                        f'All {len(links)} anchor links valid on {page} (avg: {avg_time}ms)',
                        url=url,
                        response_time=avg_time,
                        details={
                            'total_anchor_links': len(links),
                            'checked': len(page_links),
                            'avg_response_time_ms': avg_time,
                            'slowest_links': sorted(page_links, key=lambda x: x['response_time_ms'], reverse=True)[:5],
                            'all_checked_links': all_page_links  # Include all links for verification
                        })
                        
            except Exception as e:
                self.add_result('error', f'Link check failed for {page}: {str(e)[:50]}',
                               severity='medium', url=url)
    
    def _get_status_message(self, status_code: int) -> str:
        """Return a human-readable message for HTTP status codes."""
        status_messages = {
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden - Access Denied',
            404: 'Not Found - Page does not exist',
            405: 'Method Not Allowed',
            408: 'Request Timeout',
            410: 'Gone - Resource permanently removed',
            429: 'Too Many Requests',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
            504: 'Gateway Timeout'
        }
        return status_messages.get(status_code, f'HTTP Error {status_code}')
    
    async def _crawl_site(self):
        """Async crawl the site for links."""
        to_crawl = [(self.base_url, 0)]  # (url, depth)
        crawled = set()
        
        connector = aiohttp.TCPConnector(limit=10)
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            while to_crawl and len(self.checked_urls) < self.max_links:
                url, depth = to_crawl.pop(0)
                
                if url in crawled or depth > self.max_depth:
                    continue
                
                if self._should_ignore(url):
                    continue
                
                crawled.add(url)
                
                try:
                    async with session.get(url, allow_redirects=True,
                        headers={'User-Agent': 'WordPress-Monitor/1.0'}) as response:
                        
                        self.checked_urls.add(url)
                        
                        # Check for redirects
                        if len(response.history) > 2:
                            self.redirect_chains.append({
                                'url': url,
                                'chain_length': len(response.history)
                            })
                        
                        if response.status >= 400:
                            self.broken_links.append({
                                'url': url,
                                'status': response.status,
                                'status_message': self._get_status_message(response.status),
                                'source': 'crawl'
                            })
                            continue
                        
                        if 'text/html' in response.headers.get('content-type', ''):
                            html = await response.text()
                            links = self._extract_links(html, url)
                            
                            for link in links:
                                if self._is_internal(link) and link not in crawled:
                                    to_crawl.append((link, depth + 1))
                                elif self.check_external and not self._is_internal(link):
                                    await self._check_external_link(session, link, url)
                                    
                except asyncio.TimeoutError:
                    self.broken_links.append({
                        'url': url,
                        'status': 'timeout',
                        'status_message': 'Request timed out - link may be unreachable',
                        'source': 'crawl'
                    })
                except Exception as e:
                    self.logger.debug(f"Failed to check {url}: {e}")
    
    def _crawl_site_sync(self):
        """Synchronous fallback for crawling."""
        to_crawl = [(self.base_url, 0)]
        crawled = set()
        
        while to_crawl and len(self.checked_urls) < self.max_links:
            url, depth = to_crawl.pop(0)
            
            if url in crawled or depth > self.max_depth:
                continue
            
            if self._should_ignore(url):
                continue
            
            crawled.add(url)
            
            try:
                response = requests.get(url, timeout=self.timeout, allow_redirects=True,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                
                self.checked_urls.add(url)
                
                if response.status_code >= 400:
                    self.broken_links.append({
                        'url': url,
                        'status': response.status_code,
                        'status_message': self._get_status_message(response.status_code),
                        'source': 'crawl'
                    })
                    continue
                
                if 'text/html' in response.headers.get('content-type', ''):
                    links = self._extract_links(response.text, url)
                    for link in links:
                        if self._is_internal(link) and link not in crawled:
                            to_crawl.append((link, depth + 1))
                            
            except requests.exceptions.Timeout:
                self.broken_links.append({
                    'url': url,
                    'status': 'timeout',
                    'status_message': 'Request timed out - link may be unreachable',
                    'source': 'crawl'
                })
            except Exception as e:
                self.logger.debug(f"Sync check failed for {url}: {e}")
    
    async def _check_external_link(self, session, url: str, source: str):
        """Check an external link."""
        if url in self.checked_urls:
            return
        
        try:
            async with session.head(url, allow_redirects=True) as response:
                self.checked_urls.add(url)
                if response.status >= 400:
                    self.broken_links.append({
                        'url': url,
                        'status': response.status,
                        'status_message': self._get_status_message(response.status),
                        'source': source,
                        'is_external': True
                    })
        except:
            pass  # Don't fail on external links
    
    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract only anchor tag (<a>) links from HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        
        # Only extract anchor tags - no images, videos, link tags, etc.
        for tag in soup.find_all('a'):
            href = tag.get('href')
            if href and not href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                full_url = urljoin(base_url, href)
                links.append(full_url.split('#')[0])  # Remove fragment
        
        return list(set(links))
    
    def _is_internal(self, url: str) -> bool:
        """Check if URL is internal."""
        parsed = urlparse(url)
        base_parsed = urlparse(self.base_url)
        return parsed.netloc == base_parsed.netloc or not parsed.netloc
    
    def _should_ignore(self, url: str) -> bool:
        """Check if URL should be ignored."""
        for pattern in self.ignore_patterns:
            if re.match(pattern, url):
                return True
        return False
