
"""
Browser Manager for PastebinSearch Tool
Handles browser automation and monitoring
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
import json
import time

try:
    from playwright.async_api import async_playwright, Browser, BrowserContext, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

class BrowserManager:
    """Manages browser automation for PastebinSearch"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self.get_default_config()
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.selenium_driver = None
        self.use_playwright = PLAYWRIGHT_AVAILABLE
        self.monitoring_active = False
        
    def get_default_config(self) -> Dict[str, Any]:
        """Get default browser configuration"""
        return {
            'headless': True,
            'browser_type': 'chromium',
            'window_size': '1920x1080',
            'timeout': 30,
            'auto_download': True,
            'download_path': './downloads'
        }
    
    async def start_browser(self) -> bool:
        """Start browser session"""
        try:
            if self.use_playwright:
                return await self._start_playwright_browser()
            elif SELENIUM_AVAILABLE:
                return self._start_selenium_browser()
            else:
                raise Exception("No browser automation library available. Install Playwright or Selenium.")
                
        except Exception as e:
            print(f"Failed to start browser: {e}")
            return False
    
    async def _start_playwright_browser(self) -> bool:
        """Start browser using Playwright"""
        try:
            self.playwright = await async_playwright().start()
            
            # Choose browser type
            if self.config['browser_type'] == 'firefox':
                browser_launcher = self.playwright.firefox
            elif self.config['browser_type'] == 'webkit':
                browser_launcher = self.playwright.webkit
            else:
                browser_launcher = self.playwright.chromium
            
            # Launch browser
            self.browser = await browser_launcher.launch(
                headless=self.config['headless'],
                args=['--no-sandbox', '--disable-dev-shm-usage'] if not self.config['headless'] else None
            )
            
            # Create context
            width, height = map(int, self.config['window_size'].split('x'))
            self.context = await self.browser.new_context(
                viewport={'width': width, 'height': height},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Set timeout
            self.page.set_default_timeout(self.config['timeout'] * 1000)
            
            print("Playwright browser started successfully")
            return True
            
        except Exception as e:
            print(f"Playwright browser start failed: {e}")
            return False
    
    def _start_selenium_browser(self) -> bool:
        """Start browser using Selenium"""
        try:
            if self.config['browser_type'] == 'firefox':
                options = FirefoxOptions()
                if self.config['headless']:
                    options.add_argument('--headless')
                self.selenium_driver = webdriver.Firefox(options=options)
            else:
                options = ChromeOptions()
                if self.config['headless']:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                self.selenium_driver = webdriver.Chrome(options=options)
            
            # Set window size
            width, height = map(int, self.config['window_size'].split('x'))
            self.selenium_driver.set_window_size(width, height)
            
            # Set timeout
            self.selenium_driver.implicitly_wait(self.config['timeout'])
            
            print("Selenium browser started successfully")
            return True
            
        except Exception as e:
            print(f"Selenium browser start failed: {e}")
            return False
    
    async def stop_browser(self):
        """Stop browser session"""
        try:
            if self.use_playwright and self.browser:
                await self.context.close()
                await self.browser.close()
                await self.playwright.stop()
                print("Playwright browser stopped")
            elif self.selenium_driver:
                self.selenium_driver.quit()
                print("Selenium browser stopped")
            
            self.monitoring_active = False
            
        except Exception as e:
            print(f"Error stopping browser: {e}")
    
    async def navigate_to_url(self, url: str) -> bool:
        """Navigate to a specific URL"""
        try:
            if self.use_playwright and self.page:
                await self.page.goto(url)
                await self.page.wait_for_load_state('networkidle')
                print(f"Navigated to: {url}")
                return True
            elif self.selenium_driver:
                self.selenium_driver.get(url)
                print(f"Navigated to: {url}")
                return True
            else:
                print("[ERROR] No active browser session")
                return False
                
        except Exception as e:
            print(f"Navigation failed: {e}")
            return False
    
    async def auto_navigate(self) -> bool:
        """Auto navigate to Pastebin and perform initial setup"""
        try:
            if not await self.navigate_to_url("https://pastebin.com"):
                return False
            
            await asyncio.sleep(2)  # Wait for page load
            
            # Check if we're on the right page
            if self.use_playwright and self.page:
                title = await self.page.title()
                if "Pastebin" in title:
                    print("Successfully accessed Pastebin")
                    await self._setup_pastebin_session()
                    return True
            elif self.selenium_driver:
                title = self.selenium_driver.title
                if "Pastebin" in title:
                    print("Successfully accessed Pastebin")
                    self._setup_pastebin_session_selenium()
                    return True
            
            return False
            
        except Exception as e:
            print(f"Auto navigation failed: {e}")
            return False
    
    async def _setup_pastebin_session(self):
        """Setup Pastebin session with Playwright"""
        try:
            # Accept cookies if present
            try:
                cookie_button = await self.page.wait_for_selector(
                    'button:has-text("Accept")', timeout=5000
                )
                if cookie_button:
                    await cookie_button.click()
                    print("Accepted cookies")
            except Exception as e:
                print(f"Cookie banner handling: {type(e).__name__}")
            
            # Navigate to archive
            archive_link = await self.page.wait_for_selector('a[href="/archive"]', timeout=10000)
            if archive_link:
                await archive_link.click()
                await self.page.wait_for_load_state('networkidle')
                print("Navigated to archive")
            
        except Exception as e:
            print(f"[WARNING] Setup warning: {e}")
    
    def _setup_pastebin_session_selenium(self):
        """Setup Pastebin session with Selenium"""
        try:
            # Accept cookies if present
            try:
                cookie_button = WebDriverWait(self.selenium_driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
                )
                cookie_button.click()
                print("Accepted cookies")
            except Exception as e:
                print(f"Cookie banner handling: {type(e).__name__}")
            
            # Navigate to archive
            archive_link = WebDriverWait(self.selenium_driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@href='/archive']"))
            )
            archive_link.click()
            time.sleep(2)  # Wait for navigation
            print("Navigated to archive")
            
        except Exception as e:
            print(f"[WARNING] Setup warning: {e}")
    
    async def search_in_browser(self, search_term: str) -> List[Dict[str, Any]]:
        """Perform search using browser automation"""
        try:
            if self.use_playwright and self.page:
                return await self._playwright_search(search_term)
            elif self.selenium_driver:
                return self._selenium_search(search_term)
            else:
                print("[ERROR] No active browser session")
                return []
                
        except Exception as e:
            print(f"[ERROR] Browser search failed: {e}")
            return []
    
    async def _playwright_search(self, search_term: str) -> List[Dict[str, Any]]:
        """Perform search with Playwright"""
        try:
            # Navigate to search page
            search_url = f"https://pastebin.com/archive/{search_term}"
            await self.page.goto(search_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Extract search results
            results = []
            result_elements = await self.page.query_selector_all('tr')
            
            for element in result_elements:
                try:
                    cells = await element.query_selector_all('td')
                    if len(cells) >= 3:
                        title_elem = await cells[0].query_selector('a')
                        if title_elem:
                            title = await title_elem.text_content()
                            url = await title_elem.get_attribute('href')
                            
                            date = await cells[1].text_content()
                            size = await cells[2].text_content()
                            
                            results.append({
                                'title': title.strip(),
                                'url': f"https://pastebin.com{url}",
                                'date': date.strip(),
                                'size': size.strip(),
                                'source': 'browser_automation'
                            })
                except:
                    continue
            
            print(f"Found {len(results)} results via browser")
            return results
            
        except Exception as e:
            print(f"Playwright search failed: {e}")
            return []
    
    def _selenium_search(self, search_term: str) -> List[Dict[str, Any]]:
        """Perform search with Selenium"""
        try:
            # Navigate to search page
            search_url = f"https://pastebin.com/archive/{search_term}"
            self.selenium_driver.get(search_url)
            time.sleep(3)  # Wait for results to load
            
            # Extract search results
            results = []
            result_elements = self.selenium_driver.find_elements(By.TAG_NAME, 'tr')
            
            for element in result_elements:
                try:
                    cells = element.find_elements(By.TAG_NAME, 'td')
                    if len(cells) >= 3:
                        title_elem = cells[0].find_element(By.TAG_NAME, 'a')
                        title = title_elem.text
                        url = title_elem.get_attribute('href')
                        
                        date = cells[1].text
                        size = cells[2].text
                        
                        results.append({
                            'title': title.strip(),
                            'url': url,
                            'date': date.strip(),
                            'size': size.strip(),
                            'source': 'browser_automation'
                        })
                except:
                    continue
            
            print(f"Found {len(results)} results via browser")
            return results
        except Exception as e:
            print(f"Selenium search failed: {e}")
            return []
    
    async def monitor_changes(self, url: str = "https://pastebin.com/archive", interval: int = 60):
        """Monitor a page for changes"""
        if not await self.navigate_to_url(url):
            return
        
        self.monitoring_active = True
        print(f"Started monitoring: {url} (every {interval}s)")
        
        previous_hash = None
        
        while self.monitoring_active:
            try:
                if self.use_playwright and self.page:
                    content = await self.page.content()
                elif self.selenium_driver:
                    content = self.selenium_driver.page_source
                else:
                    break
                
                # Calculate content hash
                import hashlib
                current_hash = hashlib.sha256(content.encode()).hexdigest()
                
                if previous_hash and current_hash != previous_hash:
                    print("Page change detected!")
                    await self._handle_page_change(url)
                
                previous_hash = current_hash
                
                # Wait before next check
                await asyncio.sleep(interval)
                
                # Refresh page
                if self.use_playwright and self.page:
                    await self.page.reload()
                    await self.page.wait_for_load_state('networkidle')
                elif self.selenium_driver:
                    self.selenium_driver.refresh()
                    time.sleep(2)
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
        
        print("Monitoring stopped")
    
    async def _handle_page_change(self, url: str):
        """Handle detected page changes"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Log the change
            change_info = {
                'url': url,
                'timestamp': timestamp,
                'change_type': 'content_update'
            }
            
            # Save to file
            changes_file = Path('page_changes.json')
            changes = []
            
            if changes_file.exists():
                with open(changes_file, 'r') as f:
                    changes = json.load(f)
            
            changes.append(change_info)
            
            with open(changes_file, 'w') as f:
                json.dump(changes, f, indent=2)
            
            print(f"Change logged: {timestamp}")
            
        except Exception as e:
            print(f"Error handling page change: {e}")
    
    def stop_monitoring(self):
        """Stop page monitoring"""
        self.monitoring_active = False
        print("Stopping monitoring...")
    
    async def take_screenshot(self, filename: Optional[str] = None) -> str:
        """Take screenshot of current page"""
        try:
            if not filename:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot_path = Path(filename)
            
            if self.use_playwright and self.page:
                await self.page.screenshot(path=str(screenshot_path))
            elif self.selenium_driver:
                self.selenium_driver.save_screenshot(str(screenshot_path))
            else:
                raise Exception("No active browser session")
            
            print(f"Screenshot saved: {screenshot_path}")
            return str(screenshot_path)
            
        except Exception as e:
            print(f"Screenshot failed: {e}")
            return ""
    
    async def extract_page_text(self) -> str:
        """Extract all text from current page"""
        try:
            if self.use_playwright and self.page:
                return await self.page.inner_text('body')
            elif self.selenium_driver:
                return self.selenium_driver.find_element(By.TAG_NAME, 'body').text
            else:
                return ""
                
        except Exception as e:
            print(f"Text extraction failed: {e}")
            return ""
    
    def get_current_url(self) -> str:
        """Get current page URL"""
        try:
            if self.use_playwright and self.page:
                return self.page.url
            elif self.selenium_driver:
                return self.selenium_driver.current_url
            else:
                return ""
                
        except Exception as e:
            print(f"URL retrieval failed: {e}")
            return ""
    
    async def wait_for_element(self, selector: str, timeout: int = 10) -> bool:
        """Wait for element to appear"""
        try:
            if self.use_playwright and self.page:
                await self.page.wait_for_selector(selector, timeout=timeout*1000)
                return True
            elif self.selenium_driver:
                WebDriverWait(self.selenium_driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Element wait timeout: {selector}")
            return False
    
    def is_browser_active(self) -> bool:
        """Check if browser is active"""
        if self.use_playwright:
            return self.browser is not None and self.page is not None
        else:
            return self.selenium_driver is not None

