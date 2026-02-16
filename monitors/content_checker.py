"""
Content Checker - Checks for suspicious content, mixed content, and navigation integrity.
"""
import requests
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from .base_monitor import BaseMonitor, MonitorResult


class ContentChecker(BaseMonitor):
    """Checks for suspicious content and navigation integrity."""
    
    @property
    def name(self) -> str:
        return "content"
    
    def run(self) -> List[MonitorResult]:
        """Run content checks."""
        self.results = []
        self.logger.info("Starting content checks")
        
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages:
            url = self.get_full_url(page)
            self._check_page_content(url, page)
        
        # Check navigation
        self._check_navigation()
        
        return self.results
    
    def _check_page_content(self, url: str, page_path: str):
        """Check page content for suspicious elements."""
        try:
            response = requests.get(url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            if response.status_code != 200:
                self.add_result('error', f'Page returned HTTP {response.status_code}',
                               severity='high', url=url)
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Check for suspicious content
            self._check_suspicious_content(soup, url)
            
            self.add_result('success', f'Content check passed for {page_path}', url=url)
            
        except Exception as e:
            self.add_result('error', f'Content check failed for {page_path}: {str(e)[:50]}',
                           severity='medium', url=url)
    
    def _check_suspicious_content(self, soup: BeautifulSoup, url: str):
        """Check for potentially malicious content."""
        suspicious_patterns = [
            ('base64', 'Base64 encoded content found'),
            ('eval(', 'JavaScript eval() detected'),
            ('document.write', 'document.write detected'),
            ('iframe', 'IFrame detected'),
        ]
        
        page_text = str(soup)
        
        for pattern, message in suspicious_patterns:
            if pattern in page_text.lower():
                if pattern == 'iframe':
                    iframes = soup.find_all('iframe')
                    external_iframes = [f for f in iframes if f.get('src', '').startswith('http')]
                    if external_iframes:
                        self.add_result('warning', f'{len(external_iframes)} external iframes found',
                                       severity='low', url=url)
                elif pattern == 'base64':
                    # Only flag if there's a lot of base64
                    import re
                    base64_matches = re.findall(r'base64,[A-Za-z0-9+/=]{100,}', page_text)
                    if base64_matches:
                        self.add_result('warning', f'{len(base64_matches)} large base64 blocks found',
                                       severity='low', url=url)
    
    def _check_navigation(self):
        """Check navigation menus are working."""
        try:
            response = requests.get(self.base_url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find navigation
            nav = soup.find('nav') or soup.find(class_=lambda x: x and 'nav' in x.lower() if x else False)
            
            if nav:
                links = nav.find_all('a')
                if links:
                    self.add_result('success', f'Navigation found with {len(links)} links',
                                   details={'link_count': len(links)})
                else:
                    self.add_result('warning', 'Navigation found but no links',
                                   severity='medium')
            else:
                self.add_result('warning', 'No navigation element found',
                               severity='low')
                
        except Exception as e:
            self.add_result('error', f'Navigation check failed: {str(e)[:50]}',
                           severity='low')
