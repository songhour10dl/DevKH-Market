import json
import os
from typing import List, Dict, Any
from data_models import JobSite, SkillCategory, ScrapingConfig

class ConfigManager:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.default_config = self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "job_sites": [
                {
                    "name": "Khmer24",
                    "base_url": "https://www.khmer24.com",
                    "search_url_template": "https://www.khmer24.com/jobs/search?q={query}",
                    "is_active": True
                },
                {
                    "name": "BongThom",
                    "base_url": "https://www.bongthom.com",
                    "search_url_template": "https://www.bongthom.com/job/search?keyword={query}",
                    "is_active": True
                },
                {
                    "name": "Jobtify",
                    "base_url": "https://jobtify.com",
                    "search_url_template": "https://jobtify.com/jobs?search={query}",
                    "is_active": True
                },
                {
                    "name": "Pelprek",
                    "base_url": "https://pelprek.com",
                    "search_url_template": "https://pelprek.com/jobs/search?q={query}",
                    "is_active": False
                },
                {
                    "name": "CamHR",
                    "base_url": "https://camhr.com",
                    "search_url_template": "https://camhr.com/search-jobs?keywords={query}",
                    "is_active": False
                }
            ],
            "search_queries": [
                "Software Engineer",
                "Web Developer",
                "Frontend Developer",
                "Backend Developer",
                "Mobile Developer",
                "iOS Developer",
                "Android Developer",
                "IT Support",
                "DevOps Engineer"
            ],
            "skill_categories": [
                {
                    "name": "Backend",
                    "skills": ["Java", "Python", "Node.js", "C#", ".NET", "PHP", "Ruby", "Go", "Rust"],
                    "color": "#e74c3c"
                },
                {
                    "name": "Frontend",
                    "skills": ["HTML", "CSS", "JavaScript", "React", "Vue.js", "Angular", "TypeScript", "Sass", "Bootstrap"],
                    "color": "#3498db"
                },
                {
                    "name": "Mobile",
                    "skills": ["Flutter", "Kotlin", "Swift", "React Native", "Xamarin", "Ionic", "Android", "iOS"],
                    "color": "#2ecc71"
                },
                {
                    "name": "Database",
                    "skills": ["MySQL", "PostgreSQL", "MongoDB", "Redis", "SQLite", "Oracle", "SQL Server"],
                    "color": "#f39c12"
                },
                {
                    "name": "DevOps",
                    "skills": ["Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "Git", "Linux", "Nginx"],
                    "color": "#9b59b6"
                },
                {
                    "name": "Other",
                    "skills": ["C++", "Agile", "Scrum", "REST API", "GraphQL", "Microservices", "TDD", "CI/CD"],
                    "color": "#34495e"
                }
            ],
            "scraping_settings": {
                "max_pages_per_site": 5,
                "delay_between_requests": 1.0,
                "use_selenium": False
            }
        }
    
    def load_config(self) -> ScrapingConfig:
        """Load configuration from file"""
        if not os.path.exists(self.config_file):
            self.save_config(self.default_config)
            config_data = self.default_config
        else:
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                config_data = self.default_config
                self.save_config(config_data)
        
        job_sites = [JobSite(**site) for site in config_data.get("job_sites", [])]
        skill_categories = [SkillCategory(**cat) for cat in config_data.get("skill_categories", [])]
        search_queries = config_data.get("search_queries", [])
        
        scraping_settings = config_data.get("scraping_settings", {})
        
        return ScrapingConfig(
            job_sites=job_sites,
            search_queries=search_queries,
            skill_categories=skill_categories,
            max_pages_per_site=scraping_settings.get("max_pages_per_site", 5),
            delay_between_requests=scraping_settings.get("delay_between_requests", 1.0),
            use_selenium=scraping_settings.get("use_selenium", False)
        )
    
    def save_config(self, config_data: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def save_scraping_config(self, config: ScrapingConfig):
        """Save ScrapingConfig object to file"""
        config_data = {
            "job_sites": [
                {
                    "name": site.name,
                    "base_url": site.base_url,
                    "search_url_template": site.search_url_template,
                    "is_active": site.is_active
                }
                for site in config.job_sites
            ],
            "search_queries": config.search_queries,
            "skill_categories": [
                {
                    "name": cat.name,
                    "skills": cat.skills,
                    "color": cat.color
                }
                for cat in config.skill_categories
            ],
            "scraping_settings": {
                "max_pages_per_site": config.max_pages_per_site,
                "delay_between_requests": config.delay_between_requests,
                "use_selenium": config.use_selenium
            }
        }
        self.save_config(config_data)
