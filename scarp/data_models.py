from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class JobListing:
    title: str
    company: str
    location: str
    description: str
    url: str
    source_site: str
    scraped_at: datetime = field(default_factory=datetime.now)
    identified_skills: List[str] = field(default_factory=list)
    
    def __str__(self):
        return f"{self.title} at {self.company} ({self.location})"
    
    def __hash__(self):
        return hash((self.title, self.company, self.url, self.source_site))
    
    def __eq__(self, other):
        if not isinstance(other, JobListing):
            return False
        return (self.title == other.title and 
                self.company == other.company and 
                self.url == other.url and 
                self.source_site == other.source_site)

@dataclass
class JobSite:
    name: str
    base_url: str
    search_url_template: str
    is_active: bool = True
    
    def get_search_url(self, query: str) -> str:
        return self.search_url_template.format(query=query)

@dataclass
class SkillCategory:
    name: str
    skills: List[str]
    color: str = "#3498db"
    
@dataclass
class ScrapingConfig:
    job_sites: List[JobSite]
    search_queries: List[str]
    skill_categories: List[SkillCategory]
    max_pages_per_site: int = 5
    delay_between_requests: float = 1.0
    use_selenium: bool = False
