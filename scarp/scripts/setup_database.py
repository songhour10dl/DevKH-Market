import sqlite3
import os
from datetime import datetime

def create_database():
    """Create SQLite database for storing job data"""
    db_path = "job_data.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            description TEXT,
            url TEXT,
            source_site TEXT,
            scraped_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            category TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_skills (
            job_id INTEGER,
            skill_id INTEGER,
            PRIMARY KEY (job_id, skill_id),
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (skill_id) REFERENCES skills (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scraping_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_jobs INTEGER,
            sites_scraped TEXT,
            queries_used TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Database created successfully at: {os.path.abspath(db_path)}")

if __name__ == "__main__":
    create_database()
