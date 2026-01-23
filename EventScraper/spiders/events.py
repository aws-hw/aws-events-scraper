import scrapy
import datetime
from scrapy.spiders import Spider
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


class EventSpider(Spider):
    name = "Event"
    allowed_domains = ["aws-experience.com"]

    start_urls = [
        "https://aws-experience.com/apj/smb/events?location=virtual",
        "https://aws-experience.com/apj/smb/events?location=AU",
        "https://aws-experience.com/apj/smb/events?location=NZ",
    ]
    
    def __init__(self, *args, **kwargs):
        super(EventSpider, self).__init__(*args, **kwargs)
        self.driver = None
    
    def start_requests(self):
        """Initialize Selenium driver and start scraping"""
        self.logger.info("Initializing Chrome driver...")
        
        # Setup Chrome options
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            # Try to use system Chrome/ChromeDriver first (for GitHub Actions)
            # GitHub Actions installs Chrome and ChromeDriver is available in PATH
            import shutil
            chromedriver_path = shutil.which('chromedriver')
            
            if chromedriver_path:
                self.logger.info(f"Using system ChromeDriver at: {chromedriver_path}")
                service = Service(chromedriver_path)
            else:
                # Fallback to webdriver-manager (for local development)
                self.logger.info("System ChromeDriver not found, using webdriver-manager")
                service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.logger.info("Chrome driver initialized successfully")
            self.logger.info(f"Chrome version: {self.driver.capabilities.get('browserVersion', 'unknown')}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {str(e)}")
            raise
        
        # Process each URL
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse, dont_filter=True)
    
    def parse(self, response):
        """Parse the event listing page and extract event links"""
        self.logger.info(f"Parsing URL: {response.url}")
        
        try:
            self.driver.get(response.url)
            self.logger.info("Page loaded with Selenium")
            
            # Log page title to verify page loaded
            self.logger.info(f"Page title: {self.driver.title}")
            
            # Wait for content to load
            time.sleep(5)
            
            # Log page source length to verify content
            page_source = self.driver.page_source
            self.logger.info(f"Page source length: {len(page_source)} characters")
            
            # Scroll to trigger lazy loading
            for i in range(5):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Check for "Load More" button
                try:
                    load_more = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Load More') or contains(text(), 'Show More')]")
                    if load_more.is_displayed():
                        self.logger.info("Clicking 'Load More' button")
                        load_more.click()
                        time.sleep(2)
                except:
                    pass
            
            # Scroll back to top
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
            
            # Find event links
            event_links = []
            try:
                # Try multiple selectors
                selectors = [
                    "//a[contains(@href, '/apj/smb/e/')]",
                    "//a[contains(@href, '/e/')]",
                    "//a[contains(@href, 'event')]",
                ]
                
                for selector in selectors:
                    try:
                        links = self.driver.find_elements(By.XPATH, selector)
                        if links:
                            self.logger.info(f"Found {len(links)} links with selector: {selector}")
                            event_links.extend(links)
                            break
                    except Exception as e:
                        self.logger.warning(f"Selector {selector} failed: {str(e)}")
                
                if not event_links:
                    self.logger.warning(f"No event links found on {response.url}")
                    # Save screenshot for debugging
                    try:
                        screenshot_path = f"debug_screenshot_{response.url.split('=')[-1]}.png"
                        self.driver.save_screenshot(screenshot_path)
                        self.logger.info(f"Saved debug screenshot to {screenshot_path}")
                    except:
                        pass
                    return
                
                # Extract unique URLs
                registration_urls = set()
                for link in event_links:
                    try:
                        href = link.get_attribute('href')
                        if href and ('/e/' in href or 'event' in href.lower()):
                            registration_urls.add(href)
                    except:
                        pass
                
                self.logger.info(f"Found {len(registration_urls)} unique event links on {response.url}")
                
                # Yield requests for each event
                for registration_url in registration_urls:
                    yield scrapy.Request(
                        registration_url,
                        callback=self.parse_event,
                        dont_filter=True
                    )
                    
            except Exception as e:
                self.logger.error(f"Error finding event links: {str(e)}")
                
        except Exception as e:
            self.logger.error(f"Error parsing page: {str(e)}")

    def parse_event(self, response):
        """Parse individual event pages to extract event details"""
        try:
            self.logger.info(f"Loading event page: {response.url}")
            
            self.driver.get(response.url)
            time.sleep(3)
            
            # Wait for event content
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'BannerInformationEntry')]"))
                )
            except:
                self.logger.warning(f"Timeout loading event content on {response.url}")
            
            event = {}
            
            # Get page source and parse with Scrapy
            page_source = self.driver.page_source
            selector = scrapy.Selector(text=page_source)
            
            # Event Name
            event_name = selector.xpath('//h1/text()').get()
            if not event_name:
                event_name = selector.xpath('//h1[contains(@class, "Heading")]/text()').get()
            event['event_name'] = event_name.strip() if event_name else ''
            
            # Extract date, time, and location
            entries = selector.xpath('//div[contains(@class, "BannerInformationEntry")]')
            
            location = ''
            date = ''
            time_str = ''
            
            for entry in entries:
                heading = entry.xpath('.//span[contains(@class, "BannerInformationEntryHeading")]/text()').get()
                value_text = entry.xpath('.//div[contains(@class, "BannerInformationEntryValueContainer")]//text()').getall()
                value = ' '.join([t.strip() for t in value_text if t.strip()])
                
                if heading and value:
                    if 'Location' in heading:
                        location = value
                    elif 'Date' in heading:
                        date = value
                    elif 'Time' in heading:
                        time_str = value
            
            event['location'] = location
            event['date'] = date
            event['time'] = time_str
            event['registration_url'] = response.url

        except Exception as e:
            self.logger.error(f"Error parsing event {response.url}: {str(e)}")
            event = {
                'event_name': '',
                'date': '',
                'time': '',
                'location': '',
                'registration_url': response.url
            }

        # Only yield if we have event name and it's in the right location
        if event.get('event_name'):
            location = event.get('location', '').lower()
            self.logger.info(f"Event: {event.get('event_name')}, Location: {location}")
            if any(keyword.lower() in location for keyword in ['online', 'australia', 'new zealand', 'malaysia']):
                self.logger.info(f"✓ Yielding event: {event.get('event_name')}")
                yield event
            else:
                self.logger.info(f"✗ Skipping event (location filter): {event.get('event_name')}")
        else:
            self.logger.warning(f"Skipping event with no name: {response.url}")
    
    def closed(self, reason):
        """Clean up Selenium driver when spider closes"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Chrome driver closed")
