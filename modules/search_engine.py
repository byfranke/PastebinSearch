
"""
Search Engine for PastebinSearch Tool
Handles all search operations and Pastebin interactions
"""

import asyncio
import aiohttp
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urljoin, quote
from bs4 import BeautifulSoup
import json
import hashlib

class PastebinSearchEngine:
    """Main search engine for Pastebin"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = "https://pastebin.com"
        self.search_urls = {
            'archive': f"{self.base_url}/archive",
            'trends': f"{self.base_url}/trends",
            'api': f"{self.base_url}/api/api_post.php"
        }
        self.last_request_time = 0
        self.results_cache = {}
        
        # Search patterns for different content types
        self.security_patterns = {
            'credentials': [
                r'(?i)(password|pass|pwd)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(username|user|login)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(api[_-]?key)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(secret[_-]?key)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(access[_-]?token)\s*[=:]\s*[\'"]?([^\s\'"]+)',
            ],
            'database': [
                r'(?i)(server|host)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(database|db[_-]?name)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(connection[_-]?string)\s*[=:]\s*[\'"]?([^\s\'"]+)',
            ],
            'crypto': [
                r'(?i)(private[_-]?key)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(wallet[_-]?address)\s*[=:]\s*[\'"]?([^\s\'"]+)',
                r'(?i)(mnemonic|seed[_-]?phrase)\s*[=:]\s*[\'"]?([^\s\'"]+)',
            ]
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.create_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_session()
    
    async def create_session(self):
        """Create HTTP session with proper configuration"""
        import ssl
        
        timeout = aiohttp.ClientTimeout(total=self.config['search']['timeout'])
        
        # Check if brotli is available
        accept_encoding = 'gzip, deflate'
        try:
            import brotli
            accept_encoding = 'gzip, deflate, br'
        except ImportError:
            # Brotli not available, use only gzip and deflate
            pass

        headers = {
            'User-Agent': self.config['search']['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': accept_encoding,
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        # Configure SSL context
        ssl_context = None
        if not self.config['advanced']['ssl_verify']:
            # Create SSL context that allows self-signed certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        
        # Configure proxy if enabled
        connector_kwargs = {}
        if self.config['search']['proxy']['enabled']:
            connector_kwargs['trust_env'] = True
        
        connector = aiohttp.TCPConnector(
            ssl=ssl_context if ssl_context else self.config['advanced']['ssl_verify'],
            **connector_kwargs
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
            connector=connector
        )
    
    async def close_session(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
    
    async def rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        rate_limit = self.config['search']['rate_limit']
        
        if elapsed < rate_limit:
            wait_time = rate_limit - elapsed
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def search(self, search_term: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Perform basic search with enhanced error handling"""
        if not self.session:
            await self.create_session()
        
        limit = limit or self.config['search']['default_limit']
        cache_key = self.generate_cache_key(search_term, {'limit': limit})
        
        # Check cache
        if self.config['advanced']['cache_enabled'] and cache_key in self.results_cache:
            cached_result = self.results_cache[cache_key]
            if self.is_cache_valid(cached_result['timestamp']):
                return cached_result['results']
        
        try:
            # Test connectivity first if this is the first request
            if not hasattr(self, '_connectivity_tested'):
                connectivity = await self.test_connectivity()
                self._connectivity_tested = True
                
                if not connectivity['pastebin_reachable']:
                    raise Exception(f"Cannot reach Pastebin: {connectivity['error_details']}. {connectivity['suggested_fix']}")
            
            results = await self._search_archive(search_term, limit)
            
            # Cache results
            if self.config['advanced']['cache_enabled']:
                self.results_cache[cache_key] = {
                    'results': results,
                    'timestamp': time.time()
                }
            
            return results
            
        except aiohttp.ClientSSLError as e:
            raise Exception(f"SSL Certificate Error: {str(e)}. Try running with '--config' and disable SSL verification in advanced settings.")
            
        except aiohttp.ClientConnectorError as e:
            raise Exception(f"Connection Error: {str(e)}. Check your internet connection and firewall settings.")
            
        except asyncio.TimeoutError:
            raise Exception(f"Request timed out. Try increasing the timeout in configuration or check your connection.")
            
        except Exception as e:
            # If it's already a formatted exception, re-raise it
            if "SSL Certificate Error:" in str(e) or "Connection Error:" in str(e) or "Cannot reach Pastebin:" in str(e):
                raise e
            else:
                raise Exception(f"Search failed: {str(e)}")
    
    async def advanced_search(self, search_term: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Perform advanced search with filters"""
        if not self.session:
            await self.create_session()
        
        cache_key = self.generate_cache_key(search_term, filters)
        
        # Check cache
        if self.config['advanced']['cache_enabled'] and cache_key in self.results_cache:
            cached_result = self.results_cache[cache_key]
            if self.is_cache_valid(cached_result['timestamp']):
                return cached_result['results']
        
        try:
            # Get base results
            results = await self._search_archive(search_term, filters.get('limit', 100))
            
            # Apply advanced filters
            if 'date_range' in filters:
                results = self.filter_by_date(results, filters['date_range'])
            
            if 'size_range' in filters:
                results = self.filter_by_size(results, filters['size_range'])
            
            if 'syntax' in filters:
                results = self.filter_by_syntax(results, filters['syntax'])
            
            if 'security_scan' in filters and filters['security_scan']:
                results = await self.scan_for_security_issues(results)
            
            # Cache results
            if self.config['advanced']['cache_enabled']:
                self.results_cache[cache_key] = {
                    'results': results,
                    'timestamp': time.time()
                }
            
            return results
            
        except Exception as e:
            raise Exception(f"Advanced search failed: {str(e)}")
    
    async def _search_archive(self, search_term: str, limit: int) -> List[Dict[str, Any]]:
        """Search Pastebin archive with multiple real strategies"""
        results = []
        
        # Try different search approaches - more realistic methods
        search_urls = [
            f"https://pastebin.com/search?q={quote(search_term)}",  # Direct search if available
            f"https://pastebin.com/archive",  # Browse recent pastes
            f"https://pastebin.com/trending",  # Check trending pastes
            f"https://www.bing.com/search?q=site:pastebin.com+{quote(search_term)}",  # Bing sometimes works better
            f"https://duckduckgo.com/html/?q=site:pastebin.com+{quote(search_term)}",  # HTML version
        ]
        
        for search_url in search_urls:
            try:
                print(f"Trying search method: {search_url[:50]}...")
                
                await self.rate_limit()
                
                # Use different headers for different sources
                headers = {}
                if "bing.com" in search_url:
                    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                elif "duckduckgo.com/html" in search_url:
                    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
                
                async with self.session.get(search_url, headers=headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Debug: Check if we got actual content
                        if len(html) > 1000:
                            print(f"Received {len(html)} bytes of HTML content")
                            
                            if "duckduckgo.com" in search_url:
                                page_results = self.parse_duckduckgo_results(html, search_term)
                            elif "google.com" in search_url or "bing.com" in search_url:
                                page_results = self.parse_google_results(html, search_term)
                            elif "pastebin.com" in search_url:
                                page_results = self.parse_archive_page(html, search_term)
                                # For Pastebin pages, also try to find any paste links
                                if not page_results:
                                    page_results = self.extract_pastebin_links(html, search_term)
                            else:
                                page_results = []
                        else:
                            print("Received minimal content - possible blocking")
                            page_results = []
                        
                        if page_results:
                            results.extend(page_results)
                            print(f"Found {len(page_results)} results from this method")
                            break
                        else:
                            print("No results from this method")
                    elif response.status == 403:
                        print(f"Access forbidden (403) - trying next method")
                    elif response.status == 429:
                        print(f"Rate limited (429) - waiting before trying next method")
                        await asyncio.sleep(10)
                    else:
                        print(f"HTTP error {response.status}")
                        
            except Exception as e:
                print(f"Search method failed: {str(e)[:100]}")
                continue
        
        # If no results yet, offer manual search option
        if not results:
            print("No automated results found.")
            print("You can use manual browser search for better results")
            print("   Run: python pastebinsearch.py --manual \"your_search_term\"")
            
            # Return helpful placeholder results
            help_results = [
                {
                    'title': f'No automated results for: {search_term}',
                    'url': 'https://pastebin.com/no-results',
                    'date': datetime.now().isoformat(),
                    'size': 0,
                    'syntax': 'text',
                    'relevance': 1.0,
                    'search_term': search_term,
                    'found_at': datetime.now().isoformat(),
                    'source': 'no_results'
                },
                {
                    'title': 'Try: --manual "your_search_term" for browser-based search',
                    'url': 'https://pastebin.com/help-manual',
                    'date': datetime.now().isoformat(),
                    'size': 0,
                    'syntax': 'text',
                    'relevance': 0.9,
                    'search_term': search_term,
                    'found_at': datetime.now().isoformat(),
                    'source': 'help'
                }
            ]
            return help_results
        
        return results[:limit]
    
    async def _try_search_strategy(self, base_url: str, search_term: str, limit: int, max_pages: int, strategy_type: str = "direct") -> List[Dict[str, Any]]:
        """Try a specific search strategy"""
        results = []
        page = 1
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while len(results) < limit and page <= max_pages and consecutive_failures < max_consecutive_failures:
            await self.rate_limit()
            
            url = base_url
            if page > 1:
                url += f"?page={page}" if "?" not in url else f"&page={page}"
            
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        
                        # Parse based on strategy type
                        if strategy_type in ["google_search", "duckduckgo_search"]:
                            page_results = self.parse_search_engine_results(html, search_term)
                        else:
                            page_results = self.parse_archive_page(html, search_term)
                        
                        if not page_results:
                            consecutive_failures += 1
                        else:
                            consecutive_failures = 0
                            results.extend(page_results)
                        
                        page += 1
                    elif response.status == 429:
                        # Rate limited, wait longer
                        print("Rate limited, waiting...")
                        await asyncio.sleep(30)
                        consecutive_failures += 1
                    elif response.status == 403:
                        print("Access forbidden, trying different approach...")
                        consecutive_failures += 1
                    elif response.status in [404, 500, 502, 503, 504]:
                        print(f"Server error {response.status}, trying next page...")
                        consecutive_failures += 1
                        page += 1
                    else:
                        print(f"Unexpected status {response.status}")
                        consecutive_failures += 1
                        
            except aiohttp.ClientSSLError as e:
                print(f"SSL Error on page {page}: {e}")
                # Try to recreate session with different SSL settings
                try:
                    await self.close_session()
                    await self.create_session_with_fallback_ssl()
                    consecutive_failures += 1
                except Exception as fallback_e:
                    print(f"SSL fallback failed: {fallback_e}")
                    break
                    
            except aiohttp.ClientConnectorError as e:
                print(f"Connection error on page {page}: {e}")
                consecutive_failures += 1
                await asyncio.sleep(5)  # Wait before retry
                
            except Exception as e:
                print(f"Error fetching page {page}: {e}")
                consecutive_failures += 1
                
                if consecutive_failures >= max_consecutive_failures:
                    break
                    
                await asyncio.sleep(2)  # Brief pause before retry
        
        return results
    
    async def create_session_with_fallback_ssl(self):
        """Create session with fallback SSL configuration"""
        import ssl
        
        timeout = aiohttp.ClientTimeout(total=self.config['search']['timeout'])
        
        headers = {
            'User-Agent': self.config['search']['user_agent'],
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        
        # Create more permissive SSL context
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        ssl_context.set_ciphers('DEFAULT@SECLEVEL=1')  # Allow weaker ciphers if needed
        
        # Configure proxy if enabled
        connector_kwargs = {}
        if self.config['search']['proxy']['enabled']:
            connector_kwargs['trust_env'] = True
        
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            **connector_kwargs
        )
        
        self.session = aiohttp.ClientSession(
            timeout=timeout,
            headers=headers,
            connector=connector
        )
    
    def parse_archive_page(self, html: str, search_term: str) -> List[Dict[str, Any]]:
        """Parse Pastebin archive page HTML"""
        try:
            # Try different parsers in order of preference
            for parser in ['lxml', 'html.parser', 'html5lib']:
                try:
                    soup = BeautifulSoup(html, parser)
                    break
                except Exception:
                    continue
            else:
                # Fallback to default parser
                soup = BeautifulSoup(html, 'html.parser')
        
        except Exception as e:
            print(f"HTML parsing error: {e}")
            return []
        
        results = []
        
        # Try different selectors to find paste entries
        selectors = [
            'table.maintable tr',  # Classic Pastebin table
            '.table-responsive table tr',  # Modern responsive table
            'article',  # Article-based layout
            '.paste_box_line',  # Paste box layout
            'div[class*="paste"]'  # Any div with paste in class name
        ]
        
        paste_entries = []
        for selector in selectors:
            paste_entries = soup.select(selector)
            if paste_entries:
                break
        
        # If no structured entries found, try to extract any links
        if not paste_entries:
            paste_entries = soup.find_all('a', href=True)
        
        for entry in paste_entries:
            try:
                # Extract information based on entry type
                if entry.name == 'tr':  # Table row
                    cells = entry.find_all('td')
                    if len(cells) >= 3:
                        title_cell = cells[0]
                        date_cell = cells[1] if len(cells) > 1 else None
                        size_cell = cells[2] if len(cells) > 2 else None
                        syntax_cell = cells[3] if len(cells) > 3 else None
                        
                        link = title_cell.find('a')
                        if link and link.get('href'):
                            paste_url = urljoin(self.base_url, link.get('href'))
                            title = link.text.strip()
                            
                            # Get other details
                            date = self.parse_date(date_cell.text.strip() if date_cell else '')
                            size = self.parse_size(size_cell.text.strip() if size_cell else '0')
                            syntax = syntax_cell.text.strip() if syntax_cell else 'text'
                            
                            # Calculate relevance score
                            relevance = self.calculate_relevance(title, search_term)
                            
                            if relevance > 0:  # Only include relevant results
                                result = {
                                    'title': title,
                                    'url': paste_url,
                                    'date': date,
                                    'size': size,
                                    'syntax': syntax,
                                    'relevance': relevance,
                                    'search_term': search_term,
                                    'found_at': datetime.now().isoformat()
                                }
                                results.append(result)
                
                elif entry.name == 'a':  # Direct link
                    href = entry.get('href', '')
                    if '/pastebin.com/' in href or href.startswith('/'):
                        paste_url = urljoin(self.base_url, href)
                        title = entry.text.strip()
                        
                        if title and search_term.lower() in title.lower():
                            relevance = self.calculate_relevance(title, search_term)
                            
                            result = {
                                'title': title,
                                'url': paste_url,
                                'date': datetime.now().isoformat(),
                                'size': 0,
                                'syntax': 'unknown',
                                'relevance': relevance,
                                'search_term': search_term,
                                'found_at': datetime.now().isoformat()
                            }
                            results.append(result)
                        
            except Exception as e:
                continue  # Skip problematic entries
        
        return results
    
    def parse_search_engine_results(self, html: str, search_term: str) -> List[Dict[str, Any]]:
        """Parse search engine results for Pastebin links"""
        try:
            # Try different parsers
            for parser in ['lxml', 'html.parser']:
                try:
                    soup = BeautifulSoup(html, parser)
                    break
                except Exception:
                    continue
            else:
                soup = BeautifulSoup(html, 'html.parser')
        
        except Exception as e:
            print(f"Search results parsing error: {e}")
            return []
        
        results = []
        
        # Find all links that point to pastebin.com
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            
            # Check if this is a Pastebin link
            if 'pastebin.com/' in href and '/search?' not in href:
                # Clean up the URL
                if href.startswith('/url?q='):
                    # Google search result format
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(href.split('?', 1)[1])
                    if 'q' in parsed:
                        href = parsed['q'][0]
                
                if 'pastebin.com/' in href:
                    title = link.text.strip()
                    
                    if title and len(title) > 5:  # Skip empty or very short titles
                        relevance = self.calculate_relevance(title, search_term)
                        
                        if relevance > 0:
                            result = {
                                'title': title[:100],  # Limit title length
                                'url': href,
                                'date': datetime.now().isoformat(),
                                'size': 0,
                                'syntax': 'unknown',
                                'relevance': relevance,
                                'search_term': search_term,
                                'found_at': datetime.now().isoformat(),
                                'source': 'search_engine'
                            }
                            results.append(result)
                            
                            # Limit results from search engines
                            if len(results) >= 20:
                                break
        
        return results
    
    def parse_duckduckgo_results(self, html: str, search_term: str) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo search results for Pastebin links"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"DuckDuckGo parsing error: {e}")
            return []
        
        results = []
        
        # Find DuckDuckGo result links
        links = soup.find_all('a', href=True)
        
        for link in links:
            href = link.get('href', '')
            
            # DuckDuckGo sometimes wraps URLs
            if 'pastebin.com/' in href:
                title = link.get_text(strip=True)
                
                # Skip navigation links
                if len(title) > 10 and 'pastebin.com' not in title.lower():
                    result = {
                        'title': title[:100],
                        'url': href,
                        'date': datetime.now().isoformat(),
                        'size': 0,
                        'syntax': 'unknown',
                        'relevance': self.calculate_relevance(title, search_term),
                        'search_term': search_term,
                        'found_at': datetime.now().isoformat(),
                        'source': 'duckduckgo'
                    }
                    results.append(result)
                    
                    if len(results) >= 20:  # Limit results
                        break
        
        return results
    
    def parse_google_results(self, html: str, search_term: str) -> List[Dict[str, Any]]:
        """Parse Google search results for Pastebin links"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"Google parsing error: {e}")
            return []
        
        results = []
        
        # Google result selectors
        result_divs = soup.find_all('div', class_='g') or soup.find_all('div', class_='tF2Cxc')
        
        for div in result_divs:
            try:
                # Find the link
                link_elem = div.find('a', href=True)
                if not link_elem:
                    continue
                    
                href = link_elem.get('href', '')
                
                if 'pastebin.com/' in href and '/search' not in href:
                    # Get title
                    title_elem = div.find('h3') or link_elem
                    title = title_elem.get_text(strip=True) if title_elem else 'Untitled'
                    
                    if len(title) > 5:
                        result = {
                            'title': title[:100],
                            'url': href,
                            'date': datetime.now().isoformat(),
                            'size': 0,
                            'syntax': 'unknown',
                            'relevance': self.calculate_relevance(title, search_term),
                            'search_term': search_term,
                            'found_at': datetime.now().isoformat(),
                            'source': 'google'
                        }
                        results.append(result)
                        
                        if len(results) >= 20:
                            break
                            
            except Exception as e:
                continue
        
        return results
    
    async def fallback_search(self, search_term: str, limit: int) -> List[Dict[str, Any]]:
        """Fallback search method - try to return empty to trigger manual mode"""
        print("No results from automated methods...")
        print("Preparing to switch to manual browser search...")
        
        # Return empty to trigger manual search
        return []
    
    def extract_pastebin_links(self, html: str, search_term: str) -> List[Dict[str, Any]]:
        """Extract any Pastebin links from HTML content"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
        except Exception as e:
            print(f"HTML parsing error in extract_pastebin_links: {e}")
            return []
        
        results = []
        
        # Find all links
        all_links = soup.find_all('a', href=True)
        
        for link in all_links:
            href = link.get('href', '').strip()
            text = link.get_text(strip=True)
            
            # Check if it's a Pastebin link
            import re
            paste_pattern = r'(?:https?://)?(?:www\.)?pastebin\.com/([a-zA-Z0-9]{8,})'
            match = re.search(paste_pattern, href)
            
            if match and text and len(text) > 3:
                # Avoid navigation links
                skip_texts = ['home', 'login', 'signup', 'api', 'tools', 'faq', 'contact', 'archive', 'trending']
                if not any(skip in text.lower() for skip in skip_texts):
                    
                    # Check relevance to search term
                    relevance = self.calculate_relevance(text, search_term)
                    
                    if relevance > 0.0:  # Include if any relevance
                        result = {
                            'title': text[:100],
                            'url': href if href.startswith('http') else f'https://pastebin.com/{match.group(1)}',
                            'date': datetime.now().isoformat(),
                            'size': len(text) * 20,  # Rough estimate
                            'syntax': self._detect_syntax_from_title(text),
                            'relevance': relevance,
                            'search_term': search_term,
                            'found_at': datetime.now().isoformat(),
                            'source': 'pastebin_extract'
                        }
                        results.append(result)
                        
                        if len(results) >= 10:
                            break
        
        return results
    
    def _detect_syntax_from_title(self, title: str) -> str:
        """Detect syntax/language from title text"""
        title_lower = title.lower()
        
        syntax_keywords = {
            'python': ['python', 'py', 'django', 'flask', 'pip'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular'],
            'sql': ['sql', 'database', 'mysql', 'postgres', 'oracle'],
            'php': ['php', 'laravel', 'wordpress', 'symfony'],
            'java': ['java', 'spring', 'maven', 'gradle'],
            'cpp': ['cpp', 'c++', 'cplus'],
            'c': [' c ', 'clang', 'gcc'],
            'json': ['json', 'api', 'config', 'settings'],
            'xml': ['xml', 'soap', 'rss'],
            'bash': ['bash', 'shell', 'script', 'sh'],
            'powershell': ['powershell', 'ps1'],
            'log': ['log', 'error', 'debug', 'trace']
        }
        
        for syntax, keywords in syntax_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return syntax
        
        return 'text'
    
    async def _open_manual_search(self, search_term: str) -> List[Dict[str, Any]]:
        """Open manual browser search when automated methods fail"""
        print("\nOpening manual search in browser...")
        print("Automated search was blocked. Switching to manual mode.")
        
        try:
            import webbrowser
            import time
            
            # URLs para busca manual
            search_urls = [
                f"https://duckduckgo.com/?q=site:pastebin.com+{quote(search_term)}",
                f"https://www.google.com/search?q=site:pastebin.com+{quote(search_term)}",
                f"https://pastebin.com/archive",
                f"https://pastebin.com/trending"
            ]
            
            print(f"\nSearch URLs being opened for '{search_term}':")
            for i, url in enumerate(search_urls, 1):
                print(f"  {i}. {url}")
                
            # Perguntar ao usuário qual método usar
            print("\nChoose search method:")
            print("  1. DuckDuckGo site search")  
            print("  2. Google site search")
            print("  3. Pastebin Archive")
            print("  4. Pastebin Trending")
            print("  5. Open all methods")
            
            # Se estivermos em modo não-interativo, abrir DuckDuckGo por padrão
            try:
                from rich.prompt import Prompt
                choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5"], default="1")
            except:
                choice = "1"  # Default fallback
            
            urls_to_open = []
            if choice == "5":
                urls_to_open = search_urls
            else:
                urls_to_open = [search_urls[int(choice) - 1]]
            
            # Abrir URLs no browser
            for url in urls_to_open:
                print(f"Opening: {url}")
                webbrowser.open(url)
                time.sleep(1)  # Delay entre aberturas
            
            print("\nManual Search Instructions:")
            print("  1. Look for Pastebin links in the opened browser tabs")
            print("  2. Copy interesting paste URLs")
            print("  3. Return to the terminal and press Enter when done")
            print("  4. You can then use the tool to analyze specific URLs")
            
            # Aguardar input do usuário
            try:
                input("\nPress Enter when you've finished your manual search...")
            except:
                print("\nManual search completed (non-interactive mode)")
            
            # Retornar instruções ao invés de resultados vazios
            manual_results = [
                {
                    'title': f'Manual search completed for: {search_term}',
                    'url': 'https://pastebin.com/manual-search',
                    'date': datetime.now().isoformat(),
                    'size': 0,
                    'syntax': 'text',
                    'relevance': 1.0,
                    'search_term': search_term,
                    'found_at': datetime.now().isoformat(),
                    'source': 'manual_browser'
                },
                {
                    'title': 'Use: python pastebinsearch.py analyze <URL> to check specific pastes',
                    'url': 'https://pastebin.com/help',
                    'date': datetime.now().isoformat(),
                    'size': 0,
                    'syntax': 'text',
                    'relevance': 0.9,
                    'search_term': search_term,
                    'found_at': datetime.now().isoformat(),
                    'source': 'manual_help'
                }
            ]
            
            return manual_results
            
        except Exception as e:
            print(f"[ERROR] Error opening manual search: {e}")
            return []
    
    async def scan_for_security_issues(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Scan results for potential security issues"""
        enhanced_results = []
        
        for result in results:
            try:
                # Fetch paste content for analysis
                content = await self.fetch_paste_content(result['url'])
                if content:
                    security_flags = self.analyze_content_security(content)
                    result['security_flags'] = security_flags
                    result['risk_level'] = self.calculate_risk_level(security_flags)
                
                enhanced_results.append(result)
                
                # Rate limiting for content fetching
                await asyncio.sleep(self.config['search']['rate_limit'])
                
            except Exception as e:
                result['security_flags'] = []
                result['risk_level'] = 'unknown'
                enhanced_results.append(result)
        
        return enhanced_results
    
    async def fetch_paste_content(self, paste_url: str) -> Optional[str]:
        """Fetch content from a paste URL"""
        try:
            # Convert to raw URL
            raw_url = paste_url.replace('/pastebin.com/', '/pastebin.com/raw/')
            
            await self.rate_limit()
            
            async with self.session.get(raw_url) as response:
                if response.status == 200:
                    return await response.text()
                
        except Exception as e:
            pass
        
        return None
    
    def analyze_content_security(self, content: str) -> List[Dict[str, Any]]:
        """Analyze content for security issues"""
        security_flags = []
        
        for category, patterns in self.security_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.MULTILINE)
                
                for match in matches:
                    flag = {
                        'category': category,
                        'type': 'credential_exposure' if category == 'credentials' else f'{category}_exposure',
                        'match': match.group(0)[:100],  # Truncate for safety
                        'line': content[:match.start()].count('\n') + 1,
                        'severity': self.get_pattern_severity(category, pattern)
                    }
                    security_flags.append(flag)
        
        return security_flags
    
    def get_pattern_severity(self, category: str, pattern: str) -> str:
        """Get severity level for a security pattern"""
        high_risk = ['password', 'private_key', 'secret_key', 'access_token']
        medium_risk = ['username', 'api_key', 'database', 'connection_string']
        
        pattern_lower = pattern.lower()
        
        if any(risk in pattern_lower for risk in high_risk):
            return 'high'
        elif any(risk in pattern_lower for risk in medium_risk):
            return 'medium'
        else:
            return 'low'
    
    def calculate_risk_level(self, security_flags: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level"""
        if not security_flags:
            return 'low'
        
        high_count = sum(1 for flag in security_flags if flag['severity'] == 'high')
        medium_count = sum(1 for flag in security_flags if flag['severity'] == 'medium')
        
        if high_count > 0:
            return 'critical'
        elif medium_count > 2:
            return 'high'
        elif medium_count > 0:
            return 'medium'
        else:
            return 'low'
    
    def filter_by_date(self, results: List[Dict[str, Any]], days: int) -> List[Dict[str, Any]]:
        """Filter results by date range"""
        cutoff_date = datetime.now() - timedelta(days=days)
        filtered = []
        
        for result in results:
            try:
                result_date = datetime.fromisoformat(result['date'].replace('Z', '+00:00'))
                if result_date >= cutoff_date:
                    filtered.append(result)
            except:
                # If date parsing fails, include the result
                filtered.append(result)
        
        return filtered
    
    def filter_by_size(self, results: List[Dict[str, Any]], size_range: Tuple[int, int]) -> List[Dict[str, Any]]:
        """Filter results by size range"""
        min_size, max_size = size_range
        
        return [
            result for result in results
            if min_size <= result.get('size', 0) <= max_size
        ]
    
    def filter_by_syntax(self, results: List[Dict[str, Any]], syntax_types: List[str]) -> List[Dict[str, Any]]:
        """Filter results by syntax/language"""
        return [
            result for result in results
            if result.get('syntax', 'text').lower() in [s.lower() for s in syntax_types]
        ]
    
    def parse_date(self, date_str: str) -> str:
        """Parse date string from Pastebin"""
        try:
            # Handle various date formats from Pastebin
            # This would need to be implemented based on actual Pastebin formats
            return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()
    
    def parse_size(self, size_str: str) -> int:
        """Parse size string to bytes"""
        try:
            # Handle formats like "1.2 KB", "500 B", etc.
            size_str = size_str.strip().upper()
            
            if 'KB' in size_str:
                return int(float(size_str.replace('KB', '').strip()) * 1024)
            elif 'MB' in size_str:
                return int(float(size_str.replace('MB', '').strip()) * 1024 * 1024)
            elif 'GB' in size_str:
                return int(float(size_str.replace('GB', '').strip()) * 1024 * 1024 * 1024)
            elif 'B' in size_str:
                return int(size_str.replace('B', '').strip())
            else:
                return int(size_str)
        except:
            return 0
    
    def calculate_relevance(self, title: str, search_term: str) -> float:
        """Calculate relevance score for a result"""
        title_lower = title.lower()
        search_lower = search_term.lower()
        
        # Exact match gets highest score
        if search_lower in title_lower:
            return 1.0
        
        # Calculate word overlap
        search_words = search_lower.split()
        title_words = title_lower.split()
        
        overlap = len(set(search_words) & set(title_words))
        return overlap / len(search_words) if search_words else 0.0
    
    def generate_cache_key(self, search_term: str, filters: Dict[str, Any]) -> str:
        """Generate cache key for search results"""
        cache_data = f"{search_term}:{json.dumps(filters, sort_keys=True)}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def is_cache_valid(self, timestamp: float) -> bool:
        """Check if cached result is still valid"""
        cache_duration = self.config['advanced']['cache_duration']
        return (time.time() - timestamp) < cache_duration
    
    async def test_connectivity(self) -> Dict[str, Any]:
        """Test connectivity to Pastebin and diagnose issues"""
        if not self.session:
            await self.create_session()
        
        test_results = {
            'pastebin_reachable': False,
            'ssl_working': False,
            'response_time': 0,
            'error_details': None,
            'suggested_fix': None
        }
        
        start_time = time.time()
        
        try:
            # Test basic connectivity
            async with self.session.get(self.base_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                test_results['response_time'] = time.time() - start_time
                test_results['pastebin_reachable'] = True
                test_results['ssl_working'] = True
                return test_results
                
        except aiohttp.ClientSSLError as e:
            test_results['error_details'] = f"SSL Error: {str(e)}"
            test_results['suggested_fix'] = "Try disabling SSL verification in advanced settings"
            
            # Try with SSL disabled
            try:
                await self.close_session()
                await self.create_session_with_fallback_ssl()
                
                async with self.session.get(self.base_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    test_results['pastebin_reachable'] = True
                    test_results['ssl_working'] = False
                    test_results['response_time'] = time.time() - start_time
                    test_results['suggested_fix'] = "SSL verification disabled - connection working"
                    
            except Exception as fallback_e:
                test_results['error_details'] = f"SSL and fallback failed: {str(fallback_e)}"
                test_results['suggested_fix'] = "Check internet connection and firewall settings"
                
        except aiohttp.ClientConnectorError as e:
            test_results['error_details'] = f"Connection Error: {str(e)}"
            test_results['suggested_fix'] = "Check internet connection and DNS settings"
            
        except asyncio.TimeoutError:
            test_results['error_details'] = "Connection timeout"
            test_results['suggested_fix'] = "Check internet connection or try increasing timeout"
            
        except Exception as e:
            test_results['error_details'] = f"Unknown error: {str(e)}"
            test_results['suggested_fix'] = "Check logs and try restarting the application"
        
        return test_results
    
    def clear_cache(self):
        """Clear results cache"""
        self.results_cache.clear()
    
    async def get_trending_pastes(self) -> List[Dict[str, Any]]:
        """Get trending pastes from Pastebin"""
        if not self.session:
            await self.create_session()
        
        try:
            await self.rate_limit()
            
            async with self.session.get(self.search_urls['trends']) as response:
                if response.status == 200:
                    html = await response.text()
                    return self.parse_trending_page(html)
                
        except Exception as e:
            raise Exception(f"Failed to get trending pastes: {str(e)}")
        
        return []
    
    def parse_trending_page(self, html: str) -> List[Dict[str, Any]]:
        """Parse trending pastes page"""
        # Implementation would parse the trending page HTML
        # This is a placeholder for the actual parsing logic
        return []

