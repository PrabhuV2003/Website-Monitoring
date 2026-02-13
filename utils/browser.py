"""
Browser Utility - Provides Selenium-based browser automation.
Supports both headless and visible browser modes.
"""
import time
from typing import Any, Dict, List, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

from .logger import get_logger


class BrowserManager:
    """Manages browser instances for web testing."""
    
    def __init__(self, headless: bool = True, browser_type: str = 'chrome'):
        """
        Initialize browser manager.
        
        Args:
            headless: If True, runs browser in headless mode (invisible).
                     If False, shows the browser window.
            browser_type: 'chrome' or 'edge'
        """
        self.headless = headless
        self.browser_type = browser_type.lower()
        self.driver = None
        self.logger = get_logger()
        
    def start(self) -> bool:
        """Start the browser."""
        try:
            if self.browser_type == 'edge':
                self.driver = self._create_edge_driver()
            else:
                self.driver = self._create_chrome_driver()
            
            self.driver.set_page_load_timeout(30)
            self.logger.info(f"Browser started ({'headless' if self.headless else 'visible'} mode)")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            # Try fallback to Edge if Chrome fails
            if self.browser_type == 'chrome':
                try:
                    self.logger.info("Trying Edge browser as fallback...")
                    self.browser_type = 'edge'
                    self.driver = self._create_edge_driver()
                    self.driver.set_page_load_timeout(30)
                    self.logger.info(f"Edge browser started ({'headless' if self.headless else 'visible'} mode)")
                    return True
                except Exception as e2:
                    self.logger.error(f"Edge fallback also failed: {e2}")
            return False
    
    def _create_chrome_driver(self):
        """Create Chrome WebDriver."""
        options = ChromeOptions()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=WordPress-Monitor/1.0')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        
        service = ChromeService(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)
    
    def _create_edge_driver(self):
        """Create Edge WebDriver."""
        options = EdgeOptions()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=WordPress-Monitor/1.0')
        
        service = EdgeService(EdgeChromiumDriverManager().install())
        return webdriver.Edge(service=service, options=options)
    
    def navigate(self, url: str) -> Tuple[bool, int, float]:
        """
        Navigate to a URL.
        
        Returns:
            Tuple of (success, status_code, load_time_ms)
        """
        if not self.driver:
            return False, 0, 0
        
        start_time = time.time()
        try:
            self.driver.get(url)
            load_time = (time.time() - start_time) * 1000
            
            # Get response status from performance logs if available
            # For now, we check if page loaded successfully
            if self.driver.current_url:
                return True, 200, load_time
            return False, 0, load_time
            
        except TimeoutException:
            load_time = (time.time() - start_time) * 1000
            return False, 408, load_time
        except Exception as e:
            load_time = (time.time() - start_time) * 1000
            self.logger.error(f"Navigation error: {e}")
            return False, 0, load_time
    
    def get_all_links(self) -> List[Dict[str, str]]:
        """Get all anchor links from current page."""
        if not self.driver:
            return []
        
        links = []
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'a')
            for elem in elements:
                href = elem.get_attribute('href')
                text = elem.text.strip() or elem.get_attribute('aria-label') or ''
                if href and not href.startswith('javascript:') and not href.startswith('mailto:'):
                    links.append({
                        'url': href,
                        'text': text[:100]
                    })
        except Exception as e:
            self.logger.error(f"Error getting links: {e}")
        
        return links
    
    def get_all_images(self) -> List[Dict[str, Any]]:
        """Get all images from current page with their status."""
        if not self.driver:
            return []
        
        images = []
        try:
            elements = self.driver.find_elements(By.TAG_NAME, 'img')
            for elem in elements:
                src = elem.get_attribute('src') or elem.get_attribute('data-src')
                alt = elem.get_attribute('alt') or ''
                
                if src and not src.startswith('data:'):
                    # Check if image is actually loaded
                    is_loaded = self.driver.execute_script(
                        "return arguments[0].complete && arguments[0].naturalHeight !== 0",
                        elem
                    )
                    
                    # Get natural dimensions
                    natural_width = self.driver.execute_script(
                        "return arguments[0].naturalWidth", elem
                    )
                    natural_height = self.driver.execute_script(
                        "return arguments[0].naturalHeight", elem
                    )
                    
                    images.append({
                        'src': src,
                        'alt': alt,
                        'is_loaded': is_loaded,
                        'natural_width': natural_width,
                        'natural_height': natural_height
                    })
        except Exception as e:
            self.logger.error(f"Error getting images: {e}")
        
        return images
    
    def check_link(self, url: str) -> Dict[str, Any]:
        """Check a single link by navigating to it."""
        start_time = time.time()
        try:
            # Store current URL
            original_url = self.driver.current_url
            
            # Navigate to link
            self.driver.get(url)
            load_time = (time.time() - start_time) * 1000
            
            # Check for error pages
            page_title = self.driver.title.lower()
            page_source = self.driver.page_source.lower()
            
            # Common error indicators
            error_indicators = ['404', 'not found', 'error', 'forbidden', '403', '500']
            is_error = any(indicator in page_title for indicator in error_indicators)
            
            # Navigate back
            self.driver.get(original_url)
            
            return {
                'url': url,
                'load_time_ms': round(load_time, 0),
                'status': 'error' if is_error else 'success',
                'status_code': 404 if '404' in page_title or 'not found' in page_title else (200 if not is_error else 500),
                'page_title': self.driver.title
            }
            
        except TimeoutException:
            load_time = (time.time() - start_time) * 1000
            return {
                'url': url,
                'load_time_ms': round(load_time, 0),
                'status': 'error',
                'status_code': 'TIMEOUT',
                'status_message': 'Page load timeout'
            }
        except Exception as e:
            load_time = (time.time() - start_time) * 1000
            return {
                'url': url,
                'load_time_ms': round(load_time, 0),
                'status': 'error',
                'status_code': 'ERROR',
                'status_message': str(e)[:100]
            }
    
    def take_screenshot(self, filename: str) -> bool:
        """Take a screenshot of current page."""
        if not self.driver:
            return False
        try:
            self.driver.save_screenshot(filename)
            return True
        except Exception as e:
            self.logger.error(f"Screenshot error: {e}")
            return False
    
    def get_page_source(self) -> str:
        """Get current page source."""
        if not self.driver:
            return ""
        return self.driver.page_source
    
    def get_current_url(self) -> str:
        """Get current URL."""
        if not self.driver:
            return ""
        return self.driver.current_url
    
    def stop(self):
        """Stop and close the browser."""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
            self.driver = None
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()
        return False
