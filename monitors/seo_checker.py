"""
SEO Checker - Verifies SEO elements and accessibility.
"""
import requests
from typing import Any, Dict, List
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base_monitor import BaseMonitor, MonitorResult

class SEOChecker(BaseMonitor):
    """Checks SEO elements and basic accessibility."""
    
    @property
    def name(self) -> str:
        return "seo"
    
    def run(self) -> List[MonitorResult]:
        """Run SEO checks."""
        self.results = []
        self.logger.info("Starting SEO checks")
        
        seo_config = self.config.get('seo_checks', {})
        
        # Check meta tags on critical pages
        self._check_meta_tags()
        
        # Check sitemap
        if seo_config.get('check_sitemap', True):
            self._check_sitemap()
        
        # Check robots.txt
        if seo_config.get('check_robots_txt', True):
            self._check_robots_txt()
        
        # Check canonical tags
        if seo_config.get('check_canonical', True):
            self._check_canonical()
        
        # Check structured data
        if seo_config.get('check_structured_data', True):
            self._check_structured_data()
        
        return self.results
    
    def _check_meta_tags(self):
        """Check meta titles and descriptions."""
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages:
            url = self.get_full_url(page)
            
            try:
                response = requests.get(url, timeout=15,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                soup = BeautifulSoup(response.text, 'html.parser')
                
                issues = []
                details = {}
                
                # Check title
                title = soup.find('title')
                if title and title.string:
                    title_text = title.string.strip()
                    details['title'] = title_text[:60]
                    details['title_length'] = len(title_text)
                    
                    if len(title_text) < 10:
                        issues.append('Title too short')
                    elif len(title_text) > 60:
                        issues.append('Title too long (>60 chars)')
                else:
                    issues.append('Missing title tag')
                
                # Check meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc:
                    desc_content = meta_desc.get('content', '')
                    details['description'] = desc_content[:100]
                    details['description_length'] = len(desc_content)
                    
                    if len(desc_content) < 50:
                        issues.append('Meta description too short')
                    elif len(desc_content) > 160:
                        issues.append('Meta description too long (>160 chars)')
                else:
                    issues.append('Missing meta description')
                
                # Check H1
                h1_tags = soup.find_all('h1')
                details['h1_count'] = len(h1_tags)
                if len(h1_tags) == 0:
                    issues.append('Missing H1 tag')
                elif len(h1_tags) > 1:
                    issues.append(f'Multiple H1 tags ({len(h1_tags)})')
                
                # Check Open Graph
                og_title = soup.find('meta', attrs={'property': 'og:title'})
                og_desc = soup.find('meta', attrs={'property': 'og:description'})
                details['has_og_tags'] = bool(og_title and og_desc)
                
                if issues:
                    self.add_result('warning', f'SEO issues on {page}: {", ".join(issues)}',
                                   severity='low', url=url, details=details)
                else:
                    self.add_result('success', f'SEO elements OK on {page}',
                                   url=url, details=details)
                    
            except Exception as e:
                self.add_result('error', f'SEO check failed for {page}: {str(e)[:50]}',
                               severity='low', url=url)
    
    def _check_sitemap(self):
        """Check XML sitemap accessibility."""
        seo_config = self.config.get('seo_checks', {})
        sitemap_path = seo_config.get('sitemap_path', '/sitemap_index.xml')
        
        sitemap_urls = [
            sitemap_path,
            '/sitemap.xml',
            '/sitemap_index.xml',
            '/wp-sitemap.xml'
        ]
        
        sitemap_found = False
        
        for path in sitemap_urls:
            url = self.get_full_url(path)
            try:
                response = requests.get(url, timeout=15,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                
                if response.status_code == 200 and '<?xml' in response.text:
                    sitemap_found = True
                    
                    # Count URLs in sitemap
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(response.text, 'xml')
                    url_count = len(soup.find_all('url')) or len(soup.find_all('sitemap'))
                    
                    self.add_result('success', f'Sitemap found at {path}',
                                   url=url, details={'url_count': url_count})
                    break
                    
            except Exception as e:
                self.logger.debug(f"Sitemap check failed for {path}: {e}")
        
        if not sitemap_found:
            self.add_result('warning', 'No XML sitemap found',
                           severity='medium')
    
    def _check_robots_txt(self):
        """Check robots.txt file."""
        url = self.get_full_url('/robots.txt')
        
        try:
            response = requests.get(url, timeout=10,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            if response.status_code == 200:
                content = response.text.lower()
                
                details = {
                    'has_sitemap': 'sitemap:' in content,
                    'allows_all': 'disallow:' not in content or 'disallow: ' in content,
                    'blocks_all': 'disallow: /' in content and 'disallow: /' == content.split('\n')[1].strip().lower() if len(content.split('\n')) > 1 else False
                }
                
                if 'disallow: /' in content and content.count('disallow') == 1:
                    self.add_result('warning', 'robots.txt may be blocking all crawlers',
                                   severity='high', url=url, details=details)
                else:
                    self.add_result('success', 'robots.txt is accessible',
                                   url=url, details=details)
            elif response.status_code == 404:
                self.add_result('warning', 'robots.txt not found',
                               severity='low', url=url)
            else:
                self.add_result('warning', f'robots.txt returned HTTP {response.status_code}',
                               severity='low', url=url)
                
        except Exception as e:
            self.add_result('error', f'robots.txt check failed: {str(e)[:50]}',
                           severity='low', url=url)
    
    def _check_canonical(self):
        """Check canonical tags."""
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages[:3]:
            url = self.get_full_url(page)
            
            try:
                response = requests.get(url, timeout=15,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                soup = BeautifulSoup(response.text, 'html.parser')
                
                canonical = soup.find('link', attrs={'rel': 'canonical'})
                
                if canonical:
                    canonical_url = canonical.get('href', '')
                    
                    # Check if canonical points to self or different URL
                    if canonical_url and canonical_url != url:
                        # Normalize URLs for comparison
                        if canonical_url.rstrip('/') != url.rstrip('/'):
                            self.add_result('warning', 
                                f'Canonical mismatch on {page}',
                                severity='low', url=url,
                                details={'canonical': canonical_url})
                        else:
                            self.add_result('success', f'Canonical tag OK on {page}',
                                           url=url)
                    else:
                        self.add_result('success', f'Canonical tag OK on {page}',
                                       url=url)
                else:
                    self.add_result('warning', f'Missing canonical tag on {page}',
                                   severity='low', url=url)
                    
            except Exception as e:
                self.logger.debug(f"Canonical check failed for {page}: {e}")
    
    def _check_structured_data(self):
        """Check for structured data markup."""
        try:
            response = requests.get(self.base_url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            structured_data = []
            
            # Check for JSON-LD
            json_ld = soup.find_all('script', attrs={'type': 'application/ld+json'})
            if json_ld:
                structured_data.append(f'{len(json_ld)} JSON-LD blocks')
            
            # Check for microdata
            microdata = soup.find_all(attrs={'itemtype': True})
            if microdata:
                structured_data.append(f'{len(microdata)} microdata items')
            
            # Check for RDFa
            rdfa = soup.find_all(attrs={'typeof': True})
            if rdfa:
                structured_data.append(f'{len(rdfa)} RDFa items')
            
            if structured_data:
                self.add_result('success', f'Structured data found: {", ".join(structured_data)}',
                               details={'types': structured_data})
            else:
                self.add_result('warning', 'No structured data markup found',
                               severity='low')
                
        except Exception as e:
            self.add_result('error', f'Structured data check failed: {str(e)[:50]}',
                           severity='low')
