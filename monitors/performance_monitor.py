"""
Performance Monitor - Checks page speed, TTFB, and Core Web Vitals.
"""
import time
import requests
from typing import Any, Dict, List, Optional
from .base_monitor import BaseMonitor, MonitorResult

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class PerformanceMonitor(BaseMonitor):
    """Monitors page performance and Core Web Vitals."""
    
    @property
    def name(self) -> str:
        return "performance"
    
    def run(self) -> List[MonitorResult]:
        """Run performance checks."""
        self.results = []
        self.logger.info("Starting performance checks")
        
        # Check TTFB for main page
        self._check_ttfb()
        
        # Check PageSpeed Insights if API key available
        perf_config = self.config.get('performance', {})
        if perf_config.get('enable_pagespeed'):
            self._check_pagespeed()
        
        # Check for mixed content
        self._check_mixed_content()
        
        # Browser-based metrics if available
        if SELENIUM_AVAILABLE and perf_config.get('check_console_errors'):
            self._check_browser_metrics()
        
        return self.results
    
    def _check_ttfb(self):
        """Check Time to First Byte."""
        pages = self.config.get('critical_pages', ['/'])
        thresholds = self.config.get('thresholds', {})
        warning_time = thresholds.get('response_time_warning', 2000)
        critical_time = thresholds.get('response_time_critical', 3000)
        
        for page in pages[:5]:  # Limit to first 5 pages
            url = self.get_full_url(page)
            
            try:
                start = time.time()
                response = requests.get(url, timeout=30, stream=True,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                ttfb = (time.time() - start) * 1000
                
                # Read a bit to get full response
                _ = response.content[:1024]
                total_time = response.elapsed.total_seconds() * 1000
                
                details = {
                    'ttfb_ms': round(ttfb, 2),
                    'total_time_ms': round(total_time, 2),
                    'status_code': response.status_code,
                    'content_length': len(response.content)
                }
                
                if ttfb > critical_time:
                    self.add_result('warning', f'Slow TTFB on {page}: {ttfb:.0f}ms',
                                   severity='high', url=url, response_time=ttfb,
                                   details=details)
                elif ttfb > warning_time:
                    self.add_result('warning', f'Elevated TTFB on {page}: {ttfb:.0f}ms',
                                   severity='medium', url=url, response_time=ttfb,
                                   details=details)
                else:
                    self.add_result('success', f'Good TTFB on {page}: {ttfb:.0f}ms',
                                   url=url, response_time=ttfb, details=details)
                    
            except requests.exceptions.Timeout:
                self.add_result('critical', f'Page timeout: {page}',
                               severity='critical', url=url)
            except Exception as e:
                self.add_result('error', f'TTFB check failed for {page}: {str(e)[:50]}',
                               severity='medium', url=url)
    
    def _check_pagespeed(self):
        """Check Google PageSpeed Insights."""
        import os
        api_key = self.config.get('performance', {}).get('pagespeed_api_key') or os.getenv('PAGESPEED_API_KEY')
        
        if not api_key:
            self.logger.info("PageSpeed API key not configured, skipping")
            return
        
        try:
            api_url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
            params = {
                'url': self.base_url,
                'key': api_key,
                'strategy': 'mobile',
                'category': ['performance', 'accessibility', 'seo']
            }
            
            response = requests.get(api_url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract scores
                categories = data.get('lighthouseResult', {}).get('categories', {})
                
                scores = {}
                for cat_name, cat_data in categories.items():
                    score = int(cat_data.get('score', 0) * 100)
                    scores[cat_name] = score
                
                perf_score = scores.get('performance', 0)
                
                if perf_score >= 90:
                    self.add_result('success', f'PageSpeed score: {perf_score}/100',
                                   details=scores)
                elif perf_score >= 50:
                    self.add_result('warning', f'PageSpeed score needs improvement: {perf_score}/100',
                                   severity='medium', details=scores)
                else:
                    self.add_result('warning', f'Poor PageSpeed score: {perf_score}/100',
                                   severity='high', details=scores)
                                   
            else:
                self.logger.warning(f"PageSpeed API returned {response.status_code}")
                
        except Exception as e:
            self.logger.error(f"PageSpeed check failed: {e}")
    
    def _check_mixed_content(self):
        """Check for mixed content (HTTP resources on HTTPS page)."""
        from urllib.parse import urlparse
        from bs4 import BeautifulSoup
        
        if not self.base_url.startswith('https'):
            return
        
        try:
            response = requests.get(self.base_url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            soup = BeautifulSoup(response.text, 'html.parser')
            
            mixed_content = []
            
            # Check various resource types
            for tag, attr in [('script', 'src'), ('link', 'href'), 
                              ('img', 'src'), ('iframe', 'src')]:
                for element in soup.find_all(tag):
                    url = element.get(attr, '')
                    if url.startswith('http://'):
                        mixed_content.append({
                            'tag': tag,
                            'url': url[:100]
                        })
            
            if mixed_content:
                self.add_result('warning', 
                    f'Found {len(mixed_content)} mixed content resources',
                    severity='medium',
                    details={'mixed_content': mixed_content[:5]})
            else:
                self.add_result('success', 'No mixed content found')
                
        except Exception as e:
            self.logger.error(f"Mixed content check failed: {e}")
    
    def _check_browser_metrics(self):
        """Check browser-based performance metrics and console errors."""
        if not SELENIUM_AVAILABLE:
            return
        
        driver = None
        try:
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
            
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(30)
            
            driver.get(self.base_url)
            time.sleep(3)
            
            # Get console logs
            logs = driver.get_log('browser')
            errors = [log for log in logs if log['level'] in ['SEVERE', 'ERROR']]
            warnings = [log for log in logs if log['level'] == 'WARNING']
            
            if errors:
                self.add_result('warning', 
                    f'Found {len(errors)} JavaScript errors',
                    severity='medium',
                    details={'errors': [e['message'][:100] for e in errors[:5]]})
            else:
                self.add_result('success', 'No JavaScript errors detected')
            
            if warnings:
                self.add_result('warning',
                    f'Found {len(warnings)} console warnings',
                    severity='low',
                    details={'warning_count': len(warnings)})
            
            # Get navigation timing
            timing = driver.execute_script("""
                var t = window.performance.timing;
                return {
                    domContentLoaded: t.domContentLoadedEventEnd - t.navigationStart,
                    loadComplete: t.loadEventEnd - t.navigationStart,
                    ttfb: t.responseStart - t.navigationStart
                };
            """)
            
            if timing:
                self.add_result('success', 
                    f'Page load complete: {timing.get("loadComplete", 0)}ms',
                    details=timing)
            
        except Exception as e:
            self.logger.error(f"Browser metrics check failed: {e}")
        finally:
            if driver:
                driver.quit()
