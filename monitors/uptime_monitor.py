"""
Uptime Monitor - Checks website availability, response time, and SSL.
"""
import ssl
import socket
import requests
import certifi
from datetime import datetime
from typing import Any, Dict, List
from urllib.parse import urlparse
from .base_monitor import BaseMonitor, MonitorResult

class UptimeMonitor(BaseMonitor):
    """Monitors website uptime, response time, and SSL certificate."""
    
    @property
    def name(self) -> str:
        return "uptime"
    
    def run(self) -> List[MonitorResult]:
        """Run uptime checks."""
        self.results = []
        self.logger.info(f"Starting uptime checks for {self.base_url}")
        
        # Check main site availability
        self._check_availability()
        
        # Check SSL certificate
        self._check_ssl()
        
        # Check critical pages
        self._check_critical_pages()
        
        return self.results
    
    def _check_availability(self):
        """Check if the website is accessible."""
        try:
            response = self.retry_with_backoff(
                requests.get, self.base_url,
                timeout=30, allow_redirects=True,
                headers={'User-Agent': 'WordPress-Monitor/1.0'}
            )
            response_time = response.elapsed.total_seconds() * 1000
            
            thresholds = self.config.get('thresholds', {})
            warning_time = thresholds.get('response_time_warning', 2000)
            critical_time = thresholds.get('response_time_critical', 3000)
            
            if response.status_code == 200:
                if response_time > critical_time:
                    self.add_result('warning', f'Site responding but slow ({response_time:.0f}ms)',
                                   severity='high', url=self.base_url, response_time=response_time,
                                   details={'status_code': response.status_code})
                elif response_time > warning_time:
                    self.add_result('warning', f'Site response time elevated ({response_time:.0f}ms)',
                                   severity='medium', url=self.base_url, response_time=response_time)
                else:
                    self.add_result('success', f'Site is up ({response_time:.0f}ms)',
                                   url=self.base_url, response_time=response_time)
            elif response.status_code >= 500:
                self.add_result('critical', f'Server error: HTTP {response.status_code}',
                               severity='critical', url=self.base_url,
                               details={'status_code': response.status_code})
            elif response.status_code >= 400:
                self.add_result('error', f'Client error: HTTP {response.status_code}',
                               severity='high', url=self.base_url,
                               details={'status_code': response.status_code})
            else:
                self.add_result('success', f'Site responding with HTTP {response.status_code}',
                               url=self.base_url, response_time=response_time)
                
        except requests.exceptions.Timeout:
            self.add_result('critical', 'Website timeout - no response',
                           severity='critical', url=self.base_url)
        except requests.exceptions.ConnectionError as e:
            self.add_result('critical', f'Connection failed: {str(e)[:100]}',
                           severity='critical', url=self.base_url)
        except Exception as e:
            self.add_result('critical', f'Unexpected error: {str(e)[:100]}',
                           severity='critical', url=self.base_url)
    
    def _check_ssl(self):
        """Check SSL certificate validity and expiration."""
        parsed = urlparse(self.base_url)
        if parsed.scheme != 'https':
            self.add_result('warning', 'Site not using HTTPS',
                           severity='high', url=self.base_url)
            return
        
        hostname = parsed.hostname
        port = parsed.port or 443
        
        try:
            # Use certifi's CA bundle to avoid Windows SSL issues
            context = ssl.create_default_context(cafile=certifi.where())
            with socket.create_connection((hostname, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse expiry date
                    not_after = cert.get('notAfter')
                    if not_after:
                        expiry = datetime.strptime(not_after, '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (expiry - datetime.utcnow()).days
                        
                        thresholds = self.config.get('thresholds', {})
                        warning_days = thresholds.get('ssl_expiry_warning', 30)
                        critical_days = thresholds.get('ssl_expiry_critical', 7)
                        
                        if days_until_expiry <= 0:
                            self.add_result('critical', 'SSL certificate has EXPIRED',
                                           severity='critical', url=self.base_url,
                                           details={'expiry_date': not_after, 'days': days_until_expiry})
                        elif days_until_expiry <= critical_days:
                            self.add_result('critical', f'SSL expires in {days_until_expiry} days',
                                           severity='critical', url=self.base_url,
                                           details={'expiry_date': not_after, 'days': days_until_expiry})
                        elif days_until_expiry <= warning_days:
                            self.add_result('warning', f'SSL expires in {days_until_expiry} days',
                                           severity='high', url=self.base_url,
                                           details={'expiry_date': not_after, 'days': days_until_expiry})
                        else:
                            self.add_result('success', f'SSL valid for {days_until_expiry} days',
                                           url=self.base_url,
                                           details={'expiry_date': not_after, 'days': days_until_expiry})
                    
                    # Check issuer
                    issuer = dict(x[0] for x in cert.get('issuer', []))
                    self.logger.info(f"SSL Issuer: {issuer.get('organizationName', 'Unknown')}")
                    
        except ssl.SSLError as e:
            self.add_result('critical', f'SSL error: {str(e)[:100]}',
                           severity='critical', url=self.base_url)
        except Exception as e:
            self.add_result('error', f'SSL check failed: {str(e)[:100]}',
                           severity='high', url=self.base_url)
    
    def _check_critical_pages(self):
        """Check all critical pages are accessible."""
        critical_pages = self.config.get('critical_pages', ['/'])
        
        for page in critical_pages:
            url = self.get_full_url(page)
            try:
                response = requests.get(url, timeout=15,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                response_time = response.elapsed.total_seconds() * 1000
                
                if response.status_code == 200:
                    self.add_result('success', f'Page accessible: {page}',
                                   url=url, response_time=response_time)
                elif response.status_code == 404:
                    self.add_result('error', f'Page not found: {page}',
                                   severity='high', url=url,
                                   details={'status_code': 404})
                elif response.status_code >= 500:
                    self.add_result('critical', f'Server error on {page}: HTTP {response.status_code}',
                                   severity='critical', url=url,
                                   details={'status_code': response.status_code})
                else:
                    self.add_result('warning', f'Unexpected status on {page}: HTTP {response.status_code}',
                                   severity='medium', url=url,
                                   details={'status_code': response.status_code})
                    
            except Exception as e:
                self.add_result('error', f'Failed to check {page}: {str(e)[:50]}',
                               severity='high', url=url)
