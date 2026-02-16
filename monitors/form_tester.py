"""
Form Tester - Tests form submissions on WordPress sites.
"""
import time
import requests
from typing import Any, Dict, List, Optional
from bs4 import BeautifulSoup
from .base_monitor import BaseMonitor, MonitorResult

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class FormTester(BaseMonitor):
    """Tests form submissions and validation on WordPress sites."""
    
    @property
    def name(self) -> str:
        return "forms"
    
    def run(self) -> List[MonitorResult]:
        """Run form tests only on URLs defined in config (forms or forms_to_test)."""
        self.results = []
        self.logger.info("Starting form tests")
        
        # Support both 'forms_to_test' and 'forms' config keys
        forms_config = self.config.get('forms_to_test', []) or self.config.get('forms', [])
        
        if not forms_config:
            self.logger.info("No forms configured in config file - skipping form tests")
            self.add_result('success', 'No forms configured for testing - skipped',
                           details={'reason': 'No form URLs defined in config'})
            return self.results
        
        self.logger.info(f"Found {len(forms_config)} form(s) configured for testing")
        
        for form_config in forms_config:
            form_url = form_config.get('url') or form_config.get('path', '/')
            form_name = form_config.get('name', form_url)
            self.logger.info(f"Testing form: {form_name} on {form_url}")
            
            # Log CAPTCHA info
            if form_config.get('has_captcha'):
                self.logger.info(f"Form on {form_url} has CAPTCHA - using dry run mode")
            
            # Normalize: ensure 'path' key exists for _test_form compatibility
            if 'path' not in form_config and 'url' in form_config:
                form_config['path'] = form_config['url']
            
            self._test_form(form_config)
        
        return self.results
    
    def _analyze_form(self, form, page_url: str, index: int):
        """Analyze a form's structure."""
        action = form.get('action', '')
        method = form.get('method', 'post').upper()
        form_id = form.get('id', f'form-{index}')
        
        # Find inputs
        inputs = form.find_all(['input', 'textarea', 'select'])
        required_fields = [inp for inp in inputs if inp.get('required')]
        
        # Check for common issues
        if not action:
            self.add_result('warning', f'Form {form_id} has no action attribute',
                           severity='low', url=page_url)
        
        # Check for CAPTCHA
        has_captcha = bool(form.find(class_=lambda x: x and 'captcha' in x.lower() if x else False))
        if has_captcha:
            self.logger.info(f"Form {form_id} has CAPTCHA protection")
        
        # Check for honeypot
        honeypot = form.find(style=lambda x: x and 'display:none' in x if x else False)
        
        details = {
            'form_id': form_id,
            'method': method,
            'action': action,
            'field_count': len(inputs),
            'required_fields': len(required_fields),
            'has_captcha': has_captcha,
            'has_honeypot': honeypot is not None
        }
        
        self.add_result('success', f'Form {form_id} analyzed: {len(inputs)} fields',
                       url=page_url, details=details)
    
    def _test_form(self, form_config: Dict[str, Any]):
        """Test a specific form with Selenium."""
        if not SELENIUM_AVAILABLE:
            self.add_result('warning', 'Selenium not available for form testing',
                           severity='low')
            self._test_form_basic(form_config)
            return
        
        path = form_config.get('path', '/')
        url = self.get_full_url(path)
        form_selector = form_config.get('form_selector')
        fields = form_config.get('fields', [])
        submit_selector = form_config.get('submit_selector')
        success_indicator = form_config.get('success_indicator')
        dry_run = form_config.get('dry_run', False)  # Don't actually submit if True
        
        driver = None
        try:
            options = Options()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            
            self.logger.info(f"Starting Chrome for form test on {path}")
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(60)
            
            self.logger.info(f"Navigating to {url}")
            driver.get(url)
            time.sleep(3)  # Wait for page to fully load including JS
            
            # Scroll to form
            if form_selector:
                try:
                    form = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, form_selector))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(true);", form)
                    time.sleep(1)
                except Exception as e:
                    self.add_result('error', f'Form not found with selector "{form_selector}": {e}',
                                   severity='high', url=url)
                    return
            else:
                form = driver.find_element(By.TAG_NAME, 'form')
            
            self.logger.info(f"Found form, filling {len(fields)} fields")
            filled_count = 0
            
            # Fill fields
            for field in fields:
                field_name = field.get('name')
                field_selector = field.get('selector')  # Optional CSS selector
                field_value = field.get('value')
                field_type = field.get('type', 'text')
                
                try:
                    # Find element by selector or name
                    if field_selector:
                        element = driver.find_element(By.CSS_SELECTOR, field_selector)
                    elif field_name:
                        element = driver.find_element(By.NAME, field_name)
                    else:
                        self.logger.warning(f"Field has no name or selector, skipping")
                        continue
                    
                    # Scroll element into view
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(0.3)
                    
                    # Handle different field types
                    if field_type == 'checkbox':
                        if field_value in ['on', 'true', True, '1']:
                            if not element.is_selected():
                                element.click()
                        elif element.is_selected():
                            element.click()
                    elif field_type == 'radio':
                        if not element.is_selected():
                            element.click()
                    elif field_type == 'select':
                        from selenium.webdriver.support.ui import Select
                        select = Select(element)
                        select.select_by_visible_text(field_value)
                    else:
                        # text, email, tel, textarea, etc.
                        element.clear()
                        element.send_keys(field_value)
                    
                    filled_count += 1
                    self.logger.info(f"Filled field: {field_name or field_selector}")
                    
                except Exception as e:
                    self.add_result('warning', 
                        f'Could not fill field {field_name or field_selector}: {str(e)[:50]}',
                        severity='medium', url=url)
            
            self.logger.info(f"Filled {filled_count}/{len(fields)} fields")
            
            # Dry run - don't submit
            if dry_run:
                self.add_result('success', f'Form fields filled on {path} (dry run)',
                               url=url, details={'fields_filled': filled_count})
                return
            
            # Submit form
            time.sleep(1)
            if submit_selector:
                submit_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, submit_selector))
                )
            else:
                submit_btn = form.find_element(By.CSS_SELECTOR, 
                    "input[type='submit'], button[type='submit'], .submit-button")
            
            self.logger.info("Clicking submit button")
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
            time.sleep(0.5)
            submit_btn.click()
            time.sleep(5)  # Wait for form submission and response
            
            # Check for success
            if success_indicator:
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, success_indicator))
                    )
                    self.add_result('success', f'Form submission successful on {path}',
                                   url=url, details={'fields_filled': filled_count})
                except:
                    # Take screenshot on failure
                    screenshot_path = f"screenshots/form_error_{path.replace('/', '_')}.png"
                    try:
                        driver.save_screenshot(screenshot_path)
                        self.logger.info(f"Screenshot saved: {screenshot_path}")
                    except:
                        pass
                    
                    # Check for error messages
                    page_source = driver.page_source.lower()
                    if 'error' in page_source or 'invalid' in page_source:
                        self.add_result('error', f'Form submission failed on {path} - validation error',
                                       severity='high', url=url)
                    else:
                        self.add_result('warning', f'Form success indicator not found on {path}',
                                       severity='medium', url=url)
            else:
                self.add_result('success', f'Form submitted on {path} (no success check)',
                               url=url, details={'fields_filled': filled_count})
            
        except Exception as e:
            error_msg = str(e).lower()
            # If Chrome/browser is not available, fall back to basic HTTP test
            if 'chrome' in error_msg or 'binary' in error_msg or 'webdriver' in error_msg or 'chromedriver' in error_msg:
                self.logger.warning(f"Chrome not available for form test on {path}, falling back to basic HTTP check")
                self._test_form_basic(form_config)
            else:
                self.add_result('error', f'Form test failed on {path}: {str(e)[:100]}',
                               severity='high', url=url)
        finally:
            if driver:
                driver.quit()
    
    def _test_form_basic(self, form_config: Dict[str, Any]):
        """Basic form testing without Selenium - checks form presence and field accessibility."""
        path = form_config.get('path', '/')
        url = self.get_full_url(path)
        form_name = form_config.get('name', path)
        
        try:
            response = requests.get(url, timeout=15,
                headers={'User-Agent': 'WordPress-Monitor/1.0'})
            
            if response.status_code != 200:
                self.add_result('error', f'Form page {form_name} returned HTTP {response.status_code}',
                               severity='high', url=url)
                return
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find form
            form_selector = form_config.get('form_selector')
            if form_selector:
                form = soup.select_one(form_selector)
            else:
                form = soup.find('form')
            
            if not form:
                self.add_result('warning', f'Form not found on {form_name} ({path})',
                               severity='medium', url=url)
                return
            
            # Check expected fields
            fields = form_config.get('fields', [])
            fields_found = 0
            fields_missing = []
            
            for field in fields:
                selector = field.get('selector')
                if selector:
                    # Search in entire page since some forms use JS to render fields
                    element = soup.select_one(selector)
                    if element:
                        fields_found += 1
                    else:
                        fields_missing.append(selector)
            
            # Check submit button
            submit_selector = form_config.get('submit_selector')
            submit_found = False
            if submit_selector:
                submit_found = soup.select_one(submit_selector) is not None
            
            details = {
                'form_found': True,
                'fields_expected': len(fields),
                'fields_found': fields_found,
                'fields_missing': fields_missing[:5] if fields_missing else [],
                'submit_button_found': submit_found,
                'mode': 'basic_http (Chrome not available)'
            }
            
            if fields_missing:
                self.add_result('warning', 
                    f'Form {form_name}: found but {len(fields_missing)} field(s) not detected in HTML',
                    severity='low', url=url, details=details)
            else:
                self.add_result('success', 
                    f'Form {form_name}: present with {fields_found}/{len(fields)} fields verified',
                    url=url, details=details)
                
        except Exception as e:
            self.add_result('error', f'Form check failed for {form_name}: {str(e)[:50]}',
                           severity='medium', url=url)
