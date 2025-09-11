"""
Skill analysis and matching engine
"""

import re
from typing import List, Dict, Tuple
from collections import Counter
from data_models import JobListing, SkillCategory

class SkillAnalyzer:
    """Analyzes job listings for skill requirements"""
    
    def __init__(self, skill_categories: List[SkillCategory]):
        self.skill_categories = skill_categories
        self.all_skills = {}
        self._build_skill_mapping()
    
    def _build_skill_mapping(self):
        """Build mapping of skills to categories"""
        self.all_skills = {}
        for category in self.skill_categories:
            for skill in category.skills:
                self.all_skills[skill.lower()] = category.name
    
    def analyze_job(self, job: JobListing) -> List[str]:
        """Analyze a single job listing for skills"""
        found_skills = []
        text_to_analyze = f"{job.title} {job.description}".lower()
        
        for skill, category in self.all_skills.items():
            pattern = r'\b' + re.escape(skill.lower()) + r'\b'
            if re.search(pattern, text_to_analyze):
                found_skills.append(skill.title())
        
        job.identified_skills = found_skills
        return found_skills
    
    def analyze_jobs(self, jobs: List[JobListing]) -> Dict[str, any]:
        """Analyze multiple job listings"""
        all_skills = []
        skill_by_category = {cat.name: [] for cat in self.skill_categories}
        job_skill_mapping = [] 
        
        for job in jobs:
            skills = self.analyze_job(job)
            all_skills.extend(skills)
            job_skill_mapping.append((job, skills))
        
            for skill in skills:
                skill_lower = skill.lower()
                if skill_lower in self.all_skills:
                    category = self.all_skills[skill_lower]
                    skill_by_category[category].append(skill)
    
        skill_counts = Counter(all_skills)
        category_counts = {
            cat: Counter(skills) 
            for cat, skills in skill_by_category.items()
        }
        
        return {
            'total_jobs': len(jobs),
            'skill_counts': skill_counts,
            'category_counts': category_counts,
            'job_skill_mapping': job_skill_mapping,
            'top_skills': skill_counts.most_common(20),
            'skills_by_category': skill_by_category
        }
    
    def get_skill_statistics(self, jobs: List[JobListing]) -> Dict[str, any]:
        """Get detailed skill statistics"""
        analysis = self.analyze_jobs(jobs)
        
        stats = {
            'total_jobs_analyzed': analysis['total_jobs'],
            'unique_skills_found': len(analysis['skill_counts']),
            'most_demanded_skills': analysis['top_skills'][:10],
            'category_breakdown': {}
        }
        
        for category in self.skill_categories:
            cat_skills = analysis['category_counts'][category.name]
            if cat_skills:
                stats['category_breakdown'][category.name] = {
                    'total_mentions': sum(cat_skills.values()),
                    'unique_skills': len(cat_skills),
                    'top_skills': cat_skills.most_common(5),
                    'color': category.color
                }
        
        return stats
    
    def get_role_skill_mapping(self, jobs: List[JobListing]) -> Dict[str, List[str]]:
        """Map job roles to commonly required skills"""
        role_skills = {}
        
        for job in jobs:
            title_lower = job.title.lower()
            role = self._categorize_job_title(title_lower)
            
            if role not in role_skills:
                role_skills[role] = []
            
            role_skills[role].extend(job.identified_skills)
        
        role_top_skills = {}
        for role, skills in role_skills.items():
            skill_counts = Counter(skills)
            role_top_skills[role] = skill_counts.most_common(10)
        
        return role_top_skills
    
    def _categorize_job_title(self, title: str) -> str:
        """Categorize job title into role type"""
        title = title.lower()
        
        if any(word in title for word in ['frontend', 'front-end', 'front end', 'ui', 'ux']):
            return 'Frontend Developer'
        elif any(word in title for word in ['backend', 'back-end', 'back end', 'server']):
            return 'Backend Developer'
        elif any(word in title for word in ['mobile', 'android', 'ios', 'flutter', 'react native']):
            return 'Mobile Developer'
        elif any(word in title for word in ['devops', 'infrastructure', 'deployment', 'cloud']):
            return 'DevOps Engineer'
        elif any(word in title for word in ['full stack', 'fullstack', 'full-stack']):
            return 'Full Stack Developer'
        elif any(word in title for word in ['data', 'analyst', 'scientist', 'ml', 'ai']):
            return 'Data/AI Specialist'
        elif any(word in title for word in ['qa', 'test', 'quality']):
            return 'QA/Testing'
        elif any(word in title for word in ['support', 'help', 'technical support']):
            return 'IT Support'
        else:
            return 'Software Engineer'
