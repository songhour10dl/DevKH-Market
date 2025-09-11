import requests
from bs4 import BeautifulSoup
import time
import re
from typing import List, Optional, Callable
from urllib.parse import urljoin, urlparse
from PyQt6.QtCore import QThread, pyqtSignal
from data_models import JobListing, JobSite, ScrapingConfig

class JobScraper(QThread):
    progress_updated = pyqtSignal(str, int, int) 
    job_found = pyqtSignal(object)
    scraping_finished = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: ScrapingConfig):
        super().__init__()
        self.config = config
        self.jobs = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self._stop_scraping = False
    
    def stop_scraping(self):
        self._stop_scraping = True
    
    def run(self):
        try:
            self.jobs = []
            active_sites = [site for site in self.config.job_sites if site.is_active]
            total_operations = len(active_sites) * len(self.config.search_queries)
            current_operation = 0
            
            for site in active_sites:
                if self._stop_scraping:
                    break
                    
                for query in self.config.search_queries:
                    if self._stop_scraping:
                        break
                    
                    current_operation += 1
                    self.progress_updated.emit(
                        f"Scraping {site.name} for '{query}'...",
                        current_operation,
                        total_operations
                    )
                    
                    try:
                        jobs = self._scrape_site(site, query)
                        for job in jobs:
                            self.job_found.emit(job)
                            self.jobs.append(job)
                        
                        time.sleep(self.config.delay_between_requests)
                        
                    except Exception as e:
                        self.error_occurred.emit(f"Error scraping {site.name}: {str(e)}")
            
            self.scraping_finished.emit(self.jobs)
            
        except Exception as e:
            self.error_occurred.emit(f"Scraping failed: {str(e)}")
    
    def _scrape_site(self, site: JobSite, query: str) -> List[JobListing]:
        jobs = []
        
        try:
            search_url = site.get_search_url(query)
            
            if "khmer24" in site.base_url.lower():
                jobs = self._scrape_khmer24(site, search_url, query)
            elif "bongthom" in site.base_url.lower():
                jobs = self._scrape_bongthom(site, search_url, query)
            elif "jobtify" in site.base_url.lower():
                jobs = self._scrape_jobtify(site, search_url, query)
            else:
                jobs = self._scrape_generic(site, search_url, query)
                
        except Exception as e:
            print(f"Error scraping {site.name}: {e}")
        
        return jobs
    
    def _scrape_khmer24(self, site: JobSite, search_url: str, query: str) -> List[JobListing]:
        """Scrape Khmer24 job listings"""
        jobs = []
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_elements = soup.find_all(['div', 'article'], class_=re.compile(r'job|listing|item'))
            
            for element in job_elements[:20]:
                if self._stop_scraping:
                    break
                
                job = self._extract_job_info(element, site)
                if job:
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Error scraping Khmer24: {e}")
        
        return jobs
    
    def _scrape_bongthom(self, site: JobSite, search_url: str, query: str) -> List[JobListing]:
        """Scrape BongThom job listings"""
        jobs = []
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            job_elements = soup.find_all(['div', 'article'], class_=re.compile(r'job|listing|item'))
            
            for element in job_elements[:20]:
                if self._stop_scraping:
                    break
                
                job = self._extract_job_info(element, site)
                if job:
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Error scraping BongThom: {e}")
        
        return jobs
    
    def _scrape_jobtify(self, site: JobSite, search_url: str, query: str) -> List[JobListing]:
        """Scrape Jobtify job listings"""
        jobs = []
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Generic job listing extraction
            job_elements = soup.find_all(['div', 'article'], class_=re.compile(r'job|listing|item'))
            
            for element in job_elements[:20]:
                if self._stop_scraping:
                    break
                
                job = self._extract_job_info(element, site)
                if job:
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Error scraping Jobtify: {e}")
        
        return jobs
    
    def _scrape_generic(self, site: JobSite, search_url: str, query: str) -> List[JobListing]:
        """Generic scraping approach for unknown sites"""
        jobs = []
        
        try:
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common job listing patterns
            job_elements = soup.find_all(['div', 'article', 'li'], 
                                       class_=re.compile(r'job|listing|item|card'))
            
            for element in job_elements[:15]:
                if self._stop_scraping:
                    break
                
                job = self._extract_job_info(element, site)
                if job:
                    jobs.append(job)
                    
        except Exception as e:
            print(f"Error with generic scraping: {e}")
        
        return jobs
    
    def _extract_job_info(self, element, site: JobSite) -> Optional[JobListing]:
        """Extract job information from HTML element"""
        try:
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'a'], 
                                    class_=re.compile(r'title|name|job'))
            title = title_elem.get_text(strip=True) if title_elem else "Unknown Title"
            
            company_elem = element.find(['span', 'div', 'p'], 
                                      class_=re.compile(r'company|employer'))
            company = company_elem.get_text(strip=True) if company_elem else "Unknown Company"
            
            location_elem = element.find(['span', 'div', 'p'], 
                                       class_=re.compile(r'location|address|city'))
            location = location_elem.get_text(strip=True) if location_elem else "Cambodia"
            
            desc_elem = element.find(['p', 'div'], 
                                   class_=re.compile(r'description|summary|content'))
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            link_elem = element.find('a', href=True)
            url = ""
            if link_elem:
                href = link_elem['href']
                if href.startswith('http'):
                    url = href
                else:
                    url = urljoin(site.base_url, href)
            
            if title and title != "Unknown Title" and len(title) > 3:
                return JobListing(
                    title=title,
                    company=company,
                    location=location,
                    description=description,
                    url=url,
                    source_site=site.name
                )
                
        except Exception as e:
            print(f"Error extracting job info: {e}")
        
        return None
