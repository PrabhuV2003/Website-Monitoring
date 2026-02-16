"""
Content Checker - Verifies content integrity and detects changes.
"""
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from .base_monitor import BaseMonitor, MonitorResult

try:
    from PIL import Image
    import imagehash
    IMAGEHASH_AVAILABLE = True
except ImportError:
    IMAGEHASH_AVAILABLE = False

class ContentChecker(BaseMonitor):
    """Checks content integrity and detects unauthorized changes."""
    
    @property
    def name(self) -> str:
        return "content"
    
    def __init__(self, config: Dict[str, Any], base_url: str):
        super().__init__(config, base_url)
        self.baseline_dir = Path("data/baselines")
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
    
    def run(self) -> List[MonitorResult]:
        """Run content integrity checks."""
        self.results = []
        self.logger.info("Starting content integrity checks")
        
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages:
            url = self.get_full_url(page)
            self._check_page_content(url, page)
        
        # Note: Image checking is now handled by ImageChecker to avoid duplicate work
        
        # Check navigation
        self._check_navigation()
        
        return self.results
    
    def _check_page_content(self, url: str, page_path: str):
        """Check page content for changes."""
        try:
            response = requests.get(url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            if response.status_code != 200:
                self.add_result('error', f'Page returned HTTP {response.status_code}',
                               severity='high', url=url)
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove dynamic content before hashing
            for element in soup.select('script, style, noscript, [data-timestamp]'):
                element.decompose()
            
            # Get main content
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                content_text = main_content.get_text(strip=True)
            else:
                content_text = soup.get_text(strip=True)
            
            # Create hash
            content_hash = hashlib.md5(content_text.encode()).hexdigest()
            
            # Check against baseline
            baseline_file = self.baseline_dir / f"{self._sanitize_filename(page_path)}.hash"
            
            if baseline_file.exists():
                with open(baseline_file, 'r') as f:
                    stored_hash = f.read().strip()
                
                if stored_hash != content_hash:
                    # Content changed - alert AND update baseline
                    self.add_result('warning', f'Content changed on {page_path}',
                                   severity='medium', url=url,
                                   details={'old_hash': stored_hash[:8], 'new_hash': content_hash[:8]})
                    
                    # AUTO-UPDATE: Make this the new baseline
                    with open(baseline_file, 'w') as f:
                        f.write(content_hash)
                    self.logger.info(f"Baseline auto-updated for {page_path}")
                else:
                    self.add_result('success', f'Content unchanged on {page_path}',
                                   url=url)
            else:
                # Create baseline
                with open(baseline_file, 'w') as f:
                    f.write(content_hash)
                self.add_result('success', f'Baseline created for {page_path}',
                               url=url, details={'hash': content_hash[:8]})
            
            # Check for suspicious content
            self._check_suspicious_content(soup, url)
            
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
    
    def _check_images(self):
        """Check ALL images on each critical page with load times."""
        import time
        pages = self.config.get('critical_pages', ['/'])
        
        for page in pages:  # Check ALL pages, not just first 3
            url = self.get_full_url(page)
            
            try:
                response = requests.get(url, timeout=15,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                soup = BeautifulSoup(response.text, 'html.parser')
                
                images = soup.find_all('img')
                broken = []
                slow_images = []
                image_details = []
                total_load_time = 0
                checked_count = 0
                
                for img in images:  # Check ALL images
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if not src:
                        continue
                    
                    if src.startswith('data:'):
                        continue
                    
                    img_url = src if src.startswith('http') else f"{self.base_url}{src if src.startswith('/') else '/' + src}"
                    
                    try:
                        start_time = time.time()
                        img_response = requests.get(img_url, timeout=10,
                            headers={'User-Agent': 'WordPress-Monitor/1.0'},
                            stream=True)
                        # Read the content to measure full load time
                        _ = img_response.content
                        load_time = (time.time() - start_time) * 1000  # Convert to ms
                        
                        checked_count += 1
                        total_load_time += load_time
                        
                        if img_response.status_code >= 400:
                                broken.append({
                                    'image_url': img_url,
                                    'alt_text': img.get('alt', 'N/A'),
                                    'status_code': img_response.status_code,
                                    'status_message': f'HTTP {img_response.status_code}',
                                    'found_on_page': page
                                })
                        else:
                            # Track slow images (> 2 seconds)
                            if load_time > 2000:
                                slow_images.append({
                                    'image_url': img_url,
                                    'load_time_ms': round(load_time, 0)
                                })
                            
                            image_details.append({
                                'url': img_url.split('/')[-1][:50],  # Just filename
                                'load_time_ms': round(load_time, 0),
                                'size_kb': round(len(img_response.content) / 1024, 1)
                            })
                    except requests.exceptions.Timeout:
                        broken.append({
                            'image_url': img_url,
                            'alt_text': img.get('alt', 'N/A'),
                            'status_code': 'timeout',
                            'status_message': 'Request timed out',
                            'found_on_page': page
                        })
                    except Exception as e:
                        broken.append({
                            'image_url': img_url,
                            'alt_text': img.get('alt', 'N/A'),
                            'status_code': 'error',
                            'status_message': str(e)[:50],
                            'found_on_page': page
                        })
                
                avg_load_time = round(total_load_time / checked_count, 0) if checked_count > 0 else 0
                
                # Report broken images
                if broken:
                    self.add_result('error', f'{len(broken)} broken images on {page}',
                                   severity='high', url=url,
                                   details={
                                       'broken_images': broken[:10],
                                       'total_images': len(images),
                                       'checked': checked_count
                                   })
                
                # Report slow images
                if slow_images:
                    self.add_result('warning', f'{len(slow_images)} slow images on {page} (>2s)',
                                   severity='medium', url=url,
                                   details={
                                       'slow_images': slow_images[:10],
                                       'avg_load_time_ms': avg_load_time
                                   })
                
                # Summary result
                if not broken:
                    self.add_result('success', f'All {checked_count} images OK on {page} (avg: {avg_load_time}ms)',
                                   url=url, 
                                   response_time=avg_load_time,
                                   details={
                                       'total_images': len(images),
                                       'checked': checked_count,
                                       'avg_load_time_ms': avg_load_time,
                                       'total_load_time_ms': round(total_load_time, 0),
                                       'slowest_images': sorted(image_details, key=lambda x: x['load_time_ms'], reverse=True)[:5]
                                   })
                    
            except Exception as e:
                self.add_result('error', f'Image check failed for {page}: {str(e)[:50]}',
                               severity='medium', url=url)
    
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
    
    def _sanitize_filename(self, path: str) -> str:
        """Sanitize a path for use as a filename."""
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9]', '_', path)
        return sanitized[:50] or 'index'
    
    def update_baseline(self, page_path: str, content_hash: str):
        """Update the baseline for a page."""
        baseline_file = self.baseline_dir / f"{self._sanitize_filename(page_path)}.hash"
        with open(baseline_file, 'w') as f:
            f.write(content_hash)
