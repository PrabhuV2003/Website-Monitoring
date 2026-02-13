"""
WordPress Checker - WordPress-specific checks for plugins, themes, and security.
"""
import re
import requests
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from .base_monitor import BaseMonitor, MonitorResult

class WordPressChecker(BaseMonitor):
    """Checks WordPress-specific aspects like plugins, themes, and security."""
    
    @property
    def name(self) -> str:
        return "wordpress"
    
    def run(self) -> List[MonitorResult]:
        """Run WordPress-specific checks."""
        self.results = []
        self.logger.info("Starting WordPress checks")
        
        # Check WordPress version
        self._check_wp_version()
        
        # Check wp-admin accessibility
        self._check_admin_access()
        
        # Check REST API
        self._check_rest_api()
        
        # Check for common security issues
        self._check_security()
        
        # Check debug log exposure
        self._check_debug_log()
        
        # Check for readme/changelog files
        self._check_info_disclosure()
        
        return self.results
    
    def _check_wp_version(self):
        """Detect and check WordPress version."""
        try:
            response = requests.get(self.base_url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            # Check meta generator tag
            soup = BeautifulSoup(response.text, 'html.parser')
            generator = soup.find('meta', attrs={'name': 'generator'})
            
            version = None
            if generator:
                content = generator.get('content', '')
                match = re.search(r'WordPress\s*([\d.]+)', content)
                if match:
                    version = match.group(1)
            
            # Check RSS feed
            if not version:
                feed_url = f"{self.base_url}/feed/"
                try:
                    feed_resp = requests.get(feed_url, timeout=10)
                    match = re.search(r'generator>.*WordPress.*?([\d.]+)', feed_resp.text)
                    if match:
                        version = match.group(1)
                except:
                    pass
            
            if version:
                self.add_result('success', f'WordPress version: {version}',
                               details={'version': version})
                self._check_version_security(version)
            else:
                self.add_result('success', 'WordPress version hidden (good security practice)')
                
        except Exception as e:
            self.add_result('warning', f'Could not detect WP version: {str(e)[:50]}',
                           severity='low')
    
    def _check_version_security(self, version: str):
        """Check if WordPress version has known issues."""
        # This is a simplified check - in production, you'd check against a vulnerability database
        parts = version.split('.')
        try:
            major = int(parts[0])
            minor = int(parts[1]) if len(parts) > 1 else 0
            
            if major < 6:
                self.add_result('warning', f'WordPress {version} may be outdated',
                               severity='medium', details={'current_version': version})
        except:
            pass
    
    def _check_admin_access(self):
        """Check wp-admin accessibility."""
        wp_config = self.config.get('wordpress_checks', {})
        admin_path = wp_config.get('admin_path', '/wp-admin/')
        admin_url = self.get_full_url(admin_path)
        
        try:
            response = requests.get(admin_url, timeout=15, allow_redirects=False,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            # Should redirect to login
            if response.status_code in [301, 302]:
                location = response.headers.get('location', '')
                if 'wp-login.php' in location:
                    self.add_result('success', 'wp-admin redirects to login correctly',
                                   url=admin_url)
                else:
                    self.add_result('warning', f'wp-admin redirects to unexpected location',
                                   severity='medium', url=admin_url,
                                   details={'redirect': location})
            elif response.status_code == 200:
                self.add_result('warning', 'wp-admin accessible without redirect',
                               severity='medium', url=admin_url)
            elif response.status_code == 403:
                self.add_result('success', 'wp-admin protected (403 Forbidden)',
                               url=admin_url)
            elif response.status_code == 404:
                self.add_result('warning', 'wp-admin not found (custom path?)',
                               severity='low', url=admin_url)
            else:
                self.add_result('warning', f'wp-admin returned HTTP {response.status_code}',
                               severity='low', url=admin_url)
                
        except Exception as e:
            self.add_result('error', f'wp-admin check failed: {str(e)[:50]}',
                           severity='medium', url=admin_url)
    
    def _check_rest_api(self):
        """Check WordPress REST API."""
        wp_config = self.config.get('wordpress_checks', {})
        rest_endpoint = wp_config.get('rest_api_endpoint', '/wp-json/wp/v2/')
        api_url = self.get_full_url('/wp-json/')
        
        try:
            response = requests.get(api_url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    name = data.get('name', 'Unknown')
                    self.add_result('success', f'REST API accessible: {name}',
                                   url=api_url, details={'site_name': name})
                    
                    # Check if user enumeration is possible
                    users_url = self.get_full_url('/wp-json/wp/v2/users')
                    users_resp = requests.get(users_url, timeout=10)
                    if users_resp.status_code == 200:
                        try:
                            users = users_resp.json()
                            if users:
                                self.add_result('warning', 'User enumeration possible via REST API',
                                               severity='medium', url=users_url,
                                               details={'user_count': len(users)})
                        except:
                            pass
                except:
                    self.add_result('success', 'REST API responds', url=api_url)
            elif response.status_code == 404:
                self.add_result('warning', 'REST API not found (disabled?)',
                               severity='low', url=api_url)
            else:
                self.add_result('warning', f'REST API returned HTTP {response.status_code}',
                               severity='low', url=api_url)
                
        except Exception as e:
            self.add_result('error', f'REST API check failed: {str(e)[:50]}',
                           severity='medium', url=api_url)
    
    def _check_security(self):
        """Check for common security issues."""
        security_checks = [
            ('/wp-config.php', 'Configuration file exposed'),
            ('/.htaccess', 'htaccess file exposed'),
            ('/wp-includes/', 'wp-includes directory listing'),
            ('/wp-content/debug.log', 'Debug log exposed'),
            ('/xmlrpc.php', 'XML-RPC enabled'),
        ]
        
        for path, message in security_checks:
            url = self.get_full_url(path)
            try:
                response = requests.get(url, timeout=10, allow_redirects=False,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                
                if path == '/xmlrpc.php':
                    if response.status_code == 200 and 'XML-RPC' in response.text:
                        self.add_result('warning', 'XML-RPC is enabled (potential security risk)',
                                       severity='medium', url=url)
                    continue
                
                if response.status_code == 200:
                    # Check if it's actual content or an error page
                    if len(response.content) > 100:
                        self.add_result('critical', message,
                                       severity='critical', url=url)
                        
            except:
                pass  # Connection issues are OK for security checks
    
    def _check_debug_log(self):
        """Check for exposed debug.log."""
        debug_paths = [
            '/wp-content/debug.log',
            '/debug.log',
            '/error_log',
            '/error.log'
        ]
        
        for path in debug_paths:
            url = self.get_full_url(path)
            try:
                response = requests.get(url, timeout=10,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                
                if response.status_code == 200 and len(response.content) > 50:
                    # Check if it looks like a log file
                    if any(keyword in response.text.lower() for keyword in 
                           ['error', 'warning', 'notice', 'fatal', 'php']):
                        self.add_result('critical', f'Debug/error log exposed at {path}',
                                       severity='critical', url=url)
            except:
                pass
    
    def _check_info_disclosure(self):
        """Check for information disclosure files."""
        disclosure_files = [
            '/readme.html',
            '/license.txt',
            '/wp-includes/version.php'
        ]
        
        for path in disclosure_files:
            url = self.get_full_url(path)
            try:
                response = requests.get(url, timeout=10,
                    headers={'User-Agent': 'WordPress-Monitor/1.0'})
                
                if response.status_code == 200:
                    if path == '/readme.html' and 'wordpress' in response.text.lower():
                        self.add_result('warning', 'WordPress readme.html exposed',
                                       severity='low', url=url)
            except:
                pass
