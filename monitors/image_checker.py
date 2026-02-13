"""
Image Checker - Validates images on web pages.
Checks for broken images, slow loading, and missing alt attributes.
"""
import time
import requests
from typing import Any, Dict, List, Set
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .base_monitor import BaseMonitor, MonitorResult


class ImageChecker(BaseMonitor):
    """Crawls pages and validates all images."""
    
    @property
    def name(self) -> str:
        return "images"
    
    def __init__(self, config: Dict[str, Any], base_url: str):
        super().__init__(config, base_url)
        self.image_config = config.get('image_checker', {})
        self.timeout = self.image_config.get('timeout', 15)
        self.slow_threshold_ms = self.image_config.get('slow_threshold_ms', 3000)
        self.max_images_per_page = self.image_config.get('max_images_per_page', 0)  # 0 = unlimited
        self.check_alt_tags = self.image_config.get('check_alt_tags', True)
        
        # Header/Footer exclusion options
        self.ignore_header = config.get('ignore_header', False)
        self.ignore_footer = config.get('ignore_footer', False)
        self.main_content_only = config.get('main_content_only', False)
        
        # Browser mode settings
        self.use_browser = config.get('use_browser', False)
        self.headless = config.get('headless', True)
        self.browser = None
        
        self.checked_images: Set[str] = set()
        self.broken_images: List[Dict] = []
        self.slow_images: List[Dict] = []
        self.missing_alt_images: List[Dict] = []
        self.all_images: List[Dict] = []
    
    def run(self) -> List[MonitorResult]:
        """Run image checks on all critical pages."""
        self.results = []
        self.checked_images = set()
        self.broken_images = []
        self.slow_images = []
        self.missing_alt_images = []
        self.all_images = []
        
        self.logger.info("Starting image checker")
        
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
            # Check images on each critical page
            self._check_images_per_page()
            
            # Generate summary results
            self._generate_summary()
        finally:
            # Cleanup browser
            if self.browser:
                self.browser.stop()
                self.browser = None
        
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
                return main_content, "main content only"
        
        # Remove header/footer if requested
        if self.ignore_header or self.ignore_footer:
            from copy import copy
            soup_copy = copy(soup)
            
            if self.ignore_header:
                for tag in ['header', 'nav']:
                    for elem in soup_copy.find_all(tag):
                        elem.decompose()
                for selector in ['.header', '.nav', '.navbar', '.navigation', '#header', '#nav', '#navbar']:
                    for elem in soup_copy.select(selector):
                        elem.decompose()
                        
            if self.ignore_footer:
                for elem in soup_copy.find_all('footer'):
                    elem.decompose()
                for selector in ['.footer', '#footer', '.site-footer']:
                    for elem in soup_copy.select(selector):
                        elem.decompose()
            
            scope = []
            if self.ignore_header:
                scope.append("no header")
            if self.ignore_footer:
                scope.append("no footer")
            if scope:
                return soup_copy, ", ".join(scope)
        
        return soup, "full page"
    
    def _check_images_per_page(self):
        """Check all images on each critical page."""
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages:
            # Check for cancellation
            if self.is_cancelled():
                self.logger.warning("Image check cancelled by user")
                break
            
            url = self.get_full_url(page)
            page_broken = []
            page_slow = []
            page_missing_alt = []
            page_images = []
            total_time = 0
            
            try:
                self.logger.info(f"Fetching page: {page}")
                
                # Fetch page content - use browser if available
                if self.browser:
                    success, status, load_time = self.browser.navigate(url)
                    if not success:
                        self.logger.warning(f"Page {page} failed to load in browser")
                        continue
                    
                    # Get images using browser (more accurate for JS-rendered pages)
                    browser_images = self.browser.get_all_images()
                    images = []
                    for img in browser_images:
                        if img['src'] and not img['src'].startswith('data:'):
                            images.append({
                                'src': img['src'],
                                'alt': img['alt'],
                                'tag': 'img',
                                'is_loaded': img.get('is_loaded', False),
                                'natural_width': img.get('natural_width', 0),
                                'natural_height': img.get('natural_height', 0)
                            })
                else:
                    response = requests.get(url, timeout=15,
                        headers={'User-Agent': 'WordPress-Monitor/1.0'})
                    
                    if response.status_code != 200:
                        self.logger.warning(f"Page {page} returned status {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Apply content scope filtering (ignore header/footer if requested)
                    filtered_soup, scope_desc = self._get_content_scope(soup)
                    if scope_desc != "full page":
                        self.logger.info(f"Scope: {scope_desc}")
                    
                    # Extract all images from the filtered page content
                    images = self._extract_images(filtered_soup, url)
                
                # Apply per-page limit if set
                total_images = len(images)
                if self.max_images_per_page > 0 and len(images) > self.max_images_per_page:
                    images = images[:self.max_images_per_page]
                    self.logger.info(f"Limiting to {self.max_images_per_page} of {total_images} images on {page}")
                
                self.logger.info(f"Checking {len(images)} images on {page}")
                
                for img_info in images:
                    # Check for cancellation
                    if self.is_cancelled():
                        self.logger.warning("Image check cancelled by user")
                        break
                    
                    img_url = img_info['src']
                    alt_text = img_info['alt']
                    
                    # Skip already checked images
                    if img_url in self.checked_images:
                        continue
                    self.checked_images.add(img_url)
                    
                    # Check for missing alt text
                    if self.check_alt_tags and not alt_text:
                        missing_alt_detail = {
                            'image_url': img_url,
                            'alt_text': '',
                            'issue': 'Missing alt attribute',
                            'found_on_page': page,
                            'page_url': url
                        }
                        page_missing_alt.append(missing_alt_detail)
                        self.missing_alt_images.append(missing_alt_detail)
                    
                    # Try to load the image
                    try:
                        start_time = time.time()
                        img_response = requests.get(img_url, timeout=self.timeout,
                            stream=True,  # Use stream to get headers without downloading full content
                            headers={'User-Agent': 'WordPress-Monitor/1.0'})
                        load_time = (time.time() - start_time) * 1000
                        total_time += load_time
                        
                        # Check if image loaded successfully
                        if img_response.status_code >= 400:
                            error_detail = {
                                'image_url': img_url,
                                'alt_text': alt_text or 'N/A',
                                'status_code': img_response.status_code,
                                'status_message': self._get_status_message(img_response.status_code),
                                'found_on_page': page,
                                'page_url': url,
                                'load_time_ms': round(load_time, 0)
                            }
                            page_broken.append(error_detail)
                            self.broken_images.append(error_detail)
                        else:
                            # Check content type
                            content_type = img_response.headers.get('Content-Type', '')
                            is_image = 'image' in content_type.lower()
                            
                            if not is_image and content_type:
                                # Not an image content type
                                error_detail = {
                                    'image_url': img_url,
                                    'alt_text': alt_text or 'N/A',
                                    'status_code': 'INVALID_TYPE',
                                    'status_message': f'Not an image: {content_type}',
                                    'found_on_page': page,
                                    'page_url': url,
                                    'load_time_ms': round(load_time, 0)
                                }
                                page_broken.append(error_detail)
                                self.broken_images.append(error_detail)
                            else:
                                # Image loaded successfully
                                img_detail = {
                                    'image_url': img_url,
                                    'alt_text': alt_text or 'N/A',
                                    'status_code': img_response.status_code,
                                    'load_time_ms': round(load_time, 0),
                                    'content_type': content_type,
                                    'found_on_page': page
                                }
                                page_images.append(img_detail)
                                self.all_images.append(img_detail)
                                
                                # Check if slow
                                if load_time > self.slow_threshold_ms:
                                    slow_detail = {
                                        'image_url': img_url,
                                        'alt_text': alt_text or 'N/A',
                                        'load_time_ms': round(load_time, 0),
                                        'found_on_page': page,
                                        'page_url': url
                                    }
                                    page_slow.append(slow_detail)
                                    self.slow_images.append(slow_detail)
                        
                    except requests.exceptions.Timeout:
                        error_detail = {
                            'image_url': img_url,
                            'alt_text': alt_text or 'N/A',
                            'status_code': 'TIMEOUT',
                            'status_message': 'Request timed out - image may be unreachable',
                            'found_on_page': page,
                            'page_url': url,
                            'load_time_ms': self.timeout * 1000
                        }
                        page_broken.append(error_detail)
                        self.broken_images.append(error_detail)
                        
                    except requests.exceptions.SSLError as e:
                        error_detail = {
                            'image_url': img_url,
                            'alt_text': alt_text or 'N/A',
                            'status_code': 'SSL_ERROR',
                            'status_message': f'SSL Certificate error',
                            'found_on_page': page,
                            'page_url': url,
                            'load_time_ms': 0
                        }
                        page_broken.append(error_detail)
                        self.broken_images.append(error_detail)
                        
                    except requests.exceptions.ConnectionError as e:
                        error_detail = {
                            'image_url': img_url,
                            'alt_text': alt_text or 'N/A',
                            'status_code': 'CONNECTION_ERROR',
                            'status_message': 'Connection failed',
                            'found_on_page': page,
                            'page_url': url,
                            'load_time_ms': 0
                        }
                        page_broken.append(error_detail)
                        self.broken_images.append(error_detail)
                        
                    except Exception as e:
                        error_detail = {
                            'image_url': img_url,
                            'alt_text': alt_text or 'N/A',
                            'status_code': 'ERROR',
                            'status_message': str(e)[:100],
                            'found_on_page': page,
                            'page_url': url,
                            'load_time_ms': 0
                        }
                        page_broken.append(error_detail)
                        self.broken_images.append(error_detail)
                
                avg_time = round(total_time / len(page_images), 0) if page_images else 0
                
                # Report broken images on this page
                if page_broken:
                    self.add_result('error',
                        f'{len(page_broken)} broken images on {page}',
                        severity='high', url=url,
                        details={
                            'error_summary': f'Found {len(page_broken)} broken/unreachable images',
                            'broken_images': page_broken,
                            'total_images': total_images
                        })
                
                # Report slow images on this page
                if page_slow:
                    self.add_result('warning',
                        f'{len(page_slow)} slow images on {page} (>{self.slow_threshold_ms/1000}s)',
                        severity='medium', url=url,
                        details={
                            'slow_images': page_slow,
                            'avg_load_time_ms': avg_time,
                            'threshold_ms': self.slow_threshold_ms
                        })
                
                # Report missing alt attributes
                if page_missing_alt:
                    self.add_result('warning',
                        f'{len(page_missing_alt)} images missing alt text on {page}',
                        severity='low', url=url,
                        details={
                            'missing_alt_images': page_missing_alt,
                            'seo_impact': 'Missing alt text hurts SEO and accessibility'
                        })
                
                # Success summary for this page
                if not page_broken and not page_slow:
                    self.add_result('success',
                        f'All {len(images)} images valid on {page} (avg: {avg_time}ms)',
                        url=url,
                        response_time=avg_time,
                        details={
                            'total_images': len(images),
                            'checked': len(page_images),
                            'avg_load_time_ms': avg_time
                        })
                    
            except Exception as e:
                self.logger.error(f"Error checking images on {page}: {e}")
                self.add_result('error',
                    f'Failed to check images on {page}: {str(e)[:100]}',
                    severity='high', url=url)
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract all image URLs from the page."""
        images = []
        seen_urls = set()
        
        # Find all <img> tags
        for img in soup.find_all('img'):
            src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
            if src:
                # Skip data URIs and empty sources
                if src.startswith('data:'):
                    continue
                
                # Convert to absolute URL
                full_url = urljoin(base_url, src)
                
                # Skip duplicates
                if full_url in seen_urls:
                    continue
                seen_urls.add(full_url)
                
                alt_text = img.get('alt', '')
                
                images.append({
                    'src': full_url,
                    'alt': alt_text.strip() if alt_text else '',
                    'tag': 'img'
                })
        
        # Also find background images in style attributes
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            if 'background-image' in style or 'background:' in style:
                # Extract URL from style
                import re
                urls = re.findall(r'url\(["\']?([^"\')\s]+)["\']?\)', style)
                for url in urls:
                    if url.startswith('data:'):
                        continue
                    full_url = urljoin(base_url, url)
                    if full_url not in seen_urls:
                        seen_urls.add(full_url)
                        images.append({
                            'src': full_url,
                            'alt': '',  # Background images don't have alt
                            'tag': 'background'
                        })
        
        return images
    
    def _generate_summary(self):
        """Generate overall summary results."""
        if self.broken_images:
            self.add_result('error',
                f'Found {len(self.broken_images)} broken images across site',
                severity='high',
                details={
                    'summary': f'Checked {len(self.checked_images)} images, found {len(self.broken_images)} broken',
                    'broken_images': self.broken_images[:20],  # Limit to first 20
                    'total_checked': len(self.checked_images)
                })
        
        if self.slow_images:
            self.add_result('warning',
                f'{len(self.slow_images)} slow-loading images across site (>{self.slow_threshold_ms/1000}s)',
                severity='medium',
                details={
                    'slow_images': self.slow_images[:20],
                    'threshold_ms': self.slow_threshold_ms
                })
        
        if self.missing_alt_images:
            self.add_result('warning',
                f'{len(self.missing_alt_images)} images missing alt text (SEO/accessibility issue)',
                severity='low',
                details={
                    'missing_alt_images': self.missing_alt_images[:20],
                    'seo_impact': 'Alt text is important for SEO and screen readers'
                })
        
        if not self.broken_images and not self.slow_images:
            self.add_result('success',
                f'All {len(self.checked_images)} images are valid and loading properly',
                details={
                    'summary': 'All images loaded successfully',
                    'total_checked': len(self.checked_images),
                    'missing_alt_count': len(self.missing_alt_images)
                })
    
    def _get_status_message(self, status_code: int) -> str:
        """Get human-readable status message."""
        messages = {
            400: 'Bad Request',
            401: 'Unauthorized',
            403: 'Forbidden - Access Denied',
            404: 'Not Found - Image does not exist',
            405: 'Method Not Allowed',
            408: 'Request Timeout',
            410: 'Gone - Image permanently removed',
            500: 'Internal Server Error',
            502: 'Bad Gateway',
            503: 'Service Unavailable',
            504: 'Gateway Timeout'
        }
        return messages.get(status_code, f'HTTP Error {status_code}')
