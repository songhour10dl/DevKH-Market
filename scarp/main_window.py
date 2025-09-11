import sys
import os
from typing import List, Dict
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QPushButton, QTableWidget, QTableWidgetItem, QTextEdit, QLabel,
    QProgressBar, QSplitter, QGroupBox, QListWidget, QListWidgetItem,
    QMessageBox, QFileDialog, QStatusBar, QHeaderView, QAbstractItemView,
    QLineEdit, QComboBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QPixmap
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from config_manager import ConfigManager
from scraper import JobScraper
from skill_analyzer import SkillAnalyzer
from export_manager import ExportManager
from data_models import JobListing, ScrapingConfig
from config_dialog import ConfigDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DevKh Market")
        self.setGeometry(100, 100, 1400, 900)
        
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()
        self.skill_analyzer = SkillAnalyzer(self.config.skill_categories)
        self.export_manager = ExportManager()
        
        self.jobs: List[JobListing] = []
        self.filtered_jobs: List[JobListing] = []
        self.skill_stats: Dict = {}
        
        self.scraper = None
        
        self.init_ui()
        self.setup_status_bar()
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.tab_widget = QTabWidget()
        
        self.jobs_tab = self.create_jobs_tab()
        self.tab_widget.addTab(self.jobs_tab, "Job Listings")
        
        self.analysis_tab = self.create_analysis_tab()
        self.tab_widget.addTab(self.analysis_tab, "Skill Analysis")
        
        self.config_tab = self.create_config_tab()
        self.tab_widget.addTab(self.config_tab, "Configuration")
        
        main_layout.addWidget(self.tab_widget)
        
    def create_control_panel(self) -> QWidget:
        panel = QGroupBox("Controls")
        layout = QHBoxLayout(panel)
        
        self.start_button = QPushButton("🔍 Start Scraping")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.start_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.stop_button.clicked.connect(self.stop_scraping)
        self.stop_button.setEnabled(False)
        layout.addWidget(self.stop_button)
        
        layout.addStretch()
        
        export_csv_btn = QPushButton("📊 Export CSV")
        export_csv_btn.clicked.connect(self.export_csv)
        layout.addWidget(export_csv_btn)
        
        export_word_btn = QPushButton("📄 Export Word")
        export_word_btn.clicked.connect(self.export_word)
        layout.addWidget(export_word_btn)
        
        config_btn = QPushButton("⚙ Configure")
        config_btn.clicked.connect(self.open_config_dialog)
        layout.addWidget(config_btn)
        
        return panel
    
    def create_jobs_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        search_panel = self.create_search_panel()
        layout.addWidget(search_panel)
        
        self.jobs_table = QTableWidget()
        self.jobs_table.setColumnCount(6)
        self.jobs_table.setHorizontalHeaderLabels([
            "Title", "Company", "Location", "Source", "Skills", "URL"
        ])
        
        header = self.jobs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        
        self.jobs_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.jobs_table.setAlternatingRowColors(True)
        self.jobs_table.itemSelectionChanged.connect(self.on_job_selected)
        
        layout.addWidget(self.jobs_table)
        
        self.job_details = QTextEdit()
        self.job_details.setMaximumHeight(200)
        self.job_details.setPlaceholderText("Select a job to view details...")
        layout.addWidget(self.job_details)
        
        return widget
    
    def create_search_panel(self) -> QWidget:
        """Create the search panel for filtering jobs"""
        panel = QGroupBox("Search & Filter Jobs")
        layout = QHBoxLayout(panel)
        
        layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, company, location, or skills...")
        self.search_input.textChanged.connect(self.filter_jobs)
        layout.addWidget(self.search_input)
        
        layout.addWidget(QLabel("Source:"))
        self.source_filter = QComboBox()
        self.source_filter.addItem("All Sources")
        self.source_filter.currentTextChanged.connect(self.filter_jobs)
        layout.addWidget(self.source_filter)
        
        layout.addWidget(QLabel("Location:"))
        self.location_filter = QComboBox()
        self.location_filter.addItem("All Locations")
        self.location_filter.currentTextChanged.connect(self.filter_jobs)
        layout.addWidget(self.location_filter)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_search)
        layout.addWidget(clear_btn)
        
        self.results_label = QLabel("0 jobs")
        layout.addWidget(self.results_label)
        
        return panel
    
    def create_analysis_tab(self) -> QWidget:
        """Create the skill analysis tab"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("No analysis data available")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        left_layout.addWidget(stats_group)
        
        skills_group = QGroupBox("Top Skills")
        skills_layout = QVBoxLayout(skills_group)
        
        self.skills_list = QListWidget()
        skills_layout.addWidget(self.skills_list)
        
        left_layout.addWidget(skills_group)
        
        layout.addWidget(left_panel, 1)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas)
        
        layout.addWidget(right_panel, 2)
        
        return widget
    
    def create_config_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        config_group = QGroupBox("Current Configuration")
        config_layout = QVBoxLayout(config_group)
        
        self.config_summary = QTextEdit()
        self.config_summary.setReadOnly(True)
        self.update_config_summary()
        config_layout.addWidget(self.config_summary)
        
        layout.addWidget(config_group)
        
        button_layout = QHBoxLayout()
        
        edit_config_btn = QPushButton("Edit Configuration")
        edit_config_btn.clicked.connect(self.open_config_dialog)
        button_layout.addWidget(edit_config_btn)
        
        reload_config_btn = QPushButton("Reload Configuration")
        reload_config_btn.clicked.connect(self.reload_config)
        button_layout.addWidget(reload_config_btn)
        
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def setup_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready to scrape job listings")
    
    def filter_jobs(self):
        search_text = self.search_input.text().lower()
        source_filter = self.source_filter.currentText()
        location_filter = self.location_filter.currentText()
        
        self.filtered_jobs = []
        
        for job in self.jobs:
            if search_text:
                searchable_text = f"{job.title} {job.company} {job.location} {job.description} {' '.join(job.identified_skills)}".lower()
                if search_text not in searchable_text:
                    continue
            
            if source_filter != "All Sources" and job.source_site != source_filter:
                continue
            
            if location_filter != "All Locations" and job.location != location_filter:
                continue
            
            self.filtered_jobs.append(job)
        
        self.update_jobs_table()
        self.update_results_count()
    
    def clear_search(self):
        self.search_input.clear()
        self.source_filter.setCurrentText("All Sources")
        self.location_filter.setCurrentText("All Locations")
        self.filtered_jobs = self.jobs.copy()
        self.update_jobs_table()
        self.update_results_count()
    
    def update_filter_options(self):
        sources = set(job.source_site for job in self.jobs)
        self.source_filter.clear()
        self.source_filter.addItem("All Sources")
        for source in sorted(sources):
            self.source_filter.addItem(source)
        
        locations = set(job.location for job in self.jobs if job.location)
        self.location_filter.clear()
        self.location_filter.addItem("All Locations")
        for location in sorted(locations):
            self.location_filter.addItem(location)
    
    def update_jobs_table(self):
        self.jobs_table.setRowCount(0)
        
        jobs_to_display = self.filtered_jobs if hasattr(self, 'filtered_jobs') else self.jobs
        
        for job in jobs_to_display:
            row = self.jobs_table.rowCount()
            self.jobs_table.insertRow(row)
            
            self.jobs_table.setItem(row, 0, QTableWidgetItem(job.title))
            self.jobs_table.setItem(row, 1, QTableWidgetItem(job.company))
            self.jobs_table.setItem(row, 2, QTableWidgetItem(job.location))
            self.jobs_table.setItem(row, 3, QTableWidgetItem(job.source_site))
            self.jobs_table.setItem(row, 4, QTableWidgetItem(", ".join(job.identified_skills)))
            self.jobs_table.setItem(row, 5, QTableWidgetItem(job.url))
    
    def update_results_count(self):
        if hasattr(self, 'filtered_jobs'):
            count = len(self.filtered_jobs)
            total = len(self.jobs)
            if count == total:
                self.results_label.setText(f"{count} jobs")
            else:
                self.results_label.setText(f"{count} of {total} jobs")
        else:
            self.results_label.setText(f"{len(self.jobs)} jobs")
    
    def start_scraping(self):
        if not any(site.is_active for site in self.config.job_sites):
            QMessageBox.warning(self, "Warning", "No active job sites configured!")
            return
        
        if not self.config.search_queries:
            QMessageBox.warning(self, "Warning", "No search queries configured!")
            return
        
        self.jobs.clear()
        self.filtered_jobs.clear()
        self.jobs_table.setRowCount(0)
        self.job_details.clear()
        self.clear_search()
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.scraper = JobScraper(self.config)
        self.scraper.progress_updated.connect(self.update_progress)
        self.scraper.job_found.connect(self.add_job_to_table)
        self.scraper.scraping_finished.connect(self.scraping_finished)
        self.scraper.error_occurred.connect(self.handle_scraping_error)
        self.scraper.start()
        
        self.status_bar.showMessage("Scraping in progress...")
    
    def stop_scraping(self):
        if self.scraper:
            self.scraper.stop_scraping()
            self.scraper.wait() 
        
        self.scraping_finished(self.jobs)
    
    @pyqtSlot(str, int, int)
    def update_progress(self, message: str, current: int, total: int):
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
        
        self.status_bar.showMessage(f"{message} ({current}/{total})")
    
    @pyqtSlot(object)
    def add_job_to_table(self, job: JobListing):
        """Add a job to the table"""
        self.jobs.append(job)
        
        self.update_filter_options()
        
        if not hasattr(self, 'filtered_jobs') or not self.search_input.text() and self.source_filter.currentText() == "All Sources" and self.location_filter.currentText() == "All Locations":
            row = self.jobs_table.rowCount()
            self.jobs_table.insertRow(row)
            
            self.jobs_table.setItem(row, 0, QTableWidgetItem(job.title))
            self.jobs_table.setItem(row, 1, QTableWidgetItem(job.company))
            self.jobs_table.setItem(row, 2, QTableWidgetItem(job.location))
            self.jobs_table.setItem(row, 3, QTableWidgetItem(job.source_site))
            self.jobs_table.setItem(row, 4, QTableWidgetItem(", ".join(job.identified_skills)))
            self.jobs_table.setItem(row, 5, QTableWidgetItem(job.url))
        
        self.update_results_count()
    
    @pyqtSlot(list)
    def scraping_finished(self, jobs: List[JobListing]):
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.filtered_jobs = self.jobs.copy()
        self.update_filter_options()
        self.update_results_count()
        
        if jobs:
            self.skill_stats = self.skill_analyzer.get_skill_statistics(jobs)
            self.update_analysis_tab()
            
            self.status_bar.showMessage(f"Scraping completed. Found {len(jobs)} jobs.")
            
            QMessageBox.information(
                self, 
                "Scraping Complete", 
                f"Successfully scraped {len(jobs)} job listings!\n\n"
                f"Unique skills identified: {self.skill_stats.get('unique_skills_found', 0)}"
            )
        else:
            self.status_bar.showMessage("Scraping completed. No jobs found.")
            QMessageBox.warning(self, "No Results", "No job listings were found. Please check your configuration.")
    
    @pyqtSlot(str)
    def handle_scraping_error(self, error_message: str):
        self.status_bar.showMessage(f"Error: {error_message}")
        QMessageBox.critical(self, "Scraping Error", error_message)
    
    def on_job_selected(self):
        current_row = self.jobs_table.currentRow()
        jobs_to_display = self.filtered_jobs if hasattr(self, 'filtered_jobs') else self.jobs
        
        if 0 <= current_row < len(jobs_to_display):
            job = jobs_to_display[current_row]
            
            details = f"Title: {job.title}\n"
            details += f"Company: {job.company}\n"
            details += f"Location: {job.location}\n"
            details += f"Source: {job.source_site}\n"
            details += f"URL: {job.url}\n"
            details += f"Scraped: {job.scraped_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            if job.identified_skills:
                details += f"Skills: {', '.join(job.identified_skills)}\n"
            
            details += f"\nDescription:\n{job.description}"
            
            self.job_details.setPlainText(details)
    
    def update_analysis_tab(self):
        if not self.skill_stats:
            return
        
        stats_text = f"Total Jobs Analyzed: {self.skill_stats['total_jobs_analyzed']}\n"
        stats_text += f"Unique Skills Found: {self.skill_stats['unique_skills_found']}\n\n"
        
        if 'category_breakdown' in self.skill_stats:
            stats_text += "Skills by Category:\n"
            for category, data in self.skill_stats['category_breakdown'].items():
                stats_text += f"• {category}: {data['total_mentions']} mentions, {data['unique_skills']} unique skills\n"
        
        self.stats_label.setText(stats_text)
        
        self.skills_list.clear()
        if 'most_demanded_skills' in self.skill_stats:
            for skill, count in self.skill_stats['most_demanded_skills']:
                item = QListWidgetItem(f"{skill} ({count})")
                self.skills_list.addItem(item)
        
        self.update_charts()
    
    def update_charts(self):
        if not self.skill_stats or 'category_breakdown' not in self.skill_stats:
            return
        
        self.figure.clear()
        
        ax1 = self.figure.add_subplot(2, 2, 1)
        ax2 = self.figure.add_subplot(2, 2, 2)
        ax3 = self.figure.add_subplot(2, 1, 2)
        
        if 'most_demanded_skills' in self.skill_stats:
            top_skills = self.skill_stats['most_demanded_skills'][:10]
            if top_skills:
                skills, counts = zip(*top_skills)
                ax1.barh(range(len(skills)), counts, color='#3498db')
                ax1.set_yticks(range(len(skills)))
                ax1.set_yticklabels(skills)
                ax1.set_xlabel('Frequency')
                ax1.set_title('Top 10 Most Demanded Skills')
                ax1.invert_yaxis()
        
        category_data = self.skill_stats['category_breakdown']
        if category_data:
            categories = []
            totals = []
            colors = []
            
            for cat_name, cat_data in category_data.items():
                if cat_data['total_mentions'] > 0:
                    categories.append(cat_name)
                    totals.append(cat_data['total_mentions'])
                    colors.append(cat_data['color'])
            
            if categories:
                ax2.pie(totals, labels=categories, colors=colors, autopct='%1.1f%%')
                ax2.set_title('Skills Distribution by Category')
        
        if category_data:
            cat_names = []
            cat_totals = []
            cat_colors = []
            
            for cat_name, cat_data in category_data.items():
                if cat_data['total_mentions'] > 0:
                    cat_names.append(cat_name)
                    cat_totals.append(cat_data['total_mentions'])
                    cat_colors.append(cat_data['color'])
            
            if cat_names:
                bars = ax3.bar(cat_names, cat_totals, color=cat_colors)
                ax3.set_xlabel('Skill Categories')
                ax3.set_ylabel('Total Mentions')
                ax3.set_title('Skill Demand by Category')
                ax3.tick_params(axis='x', rotation=45)
                
                for bar, total in zip(bars, cat_totals):
                    height = bar.get_height()
                    ax3.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                            str(total), ha='center', va='bottom')
        
        self.figure.tight_layout()
        self.canvas.draw()
    
    def export_csv(self):
        jobs_to_export = self.filtered_jobs if hasattr(self, 'filtered_jobs') and self.filtered_jobs else self.jobs
        
        if not jobs_to_export:
            QMessageBox.warning(self, "Warning", "No job data to export!")
            return
        
        try:
            filepath = self.export_manager.export_to_csv(jobs_to_export, self.skill_stats)
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Data exported successfully to:\n{filepath}"
            )
            self.status_bar.showMessage(f"Exported to {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{str(e)}")
    
    def export_word(self):
        jobs_to_export = self.filtered_jobs if hasattr(self, 'filtered_jobs') and self.filtered_jobs else self.jobs
        
        if not jobs_to_export:
            QMessageBox.warning(self, "Warning", "No job data to export!")
            return
        
        try:
            filepath = self.export_manager.export_to_word(jobs_to_export, self.skill_stats)
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Report exported successfully to:\n{filepath}"
            )
            self.status_bar.showMessage(f"Exported to {filepath}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export Word document:\n{str(e)}")
    
    def open_config_dialog(self):
        dialog = ConfigDialog(self.config, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.config = dialog.get_config()
            self.config_manager.save_scraping_config(self.config)
            self.skill_analyzer = SkillAnalyzer(self.config.skill_categories)
            self.update_config_summary()
            self.status_bar.showMessage("Configuration updated")
    
    def reload_config(self):
        try:
            self.config = self.config_manager.load_config()
            self.skill_analyzer = SkillAnalyzer(self.config.skill_categories)
            self.update_config_summary()
            self.status_bar.showMessage("Configuration reloaded")
            QMessageBox.information(self, "Success", "Configuration reloaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reload configuration:\n{str(e)}")
    
    def update_config_summary(self):
        summary = "=== JOB SITES ===\n"
        for site in self.config.job_sites:
            status = "✓ Active" if site.is_active else "✗ Inactive"
            summary += f"{site.name}: {status}\n"
        
        summary += f"\n=== SEARCH QUERIES ({len(self.config.search_queries)}) ===\n"
        for query in self.config.search_queries:
            summary += f"• {query}\n"
        
        summary += f"\n=== SKILL CATEGORIES ===\n"
        for category in self.config.skill_categories:
            summary += f"{category.name} ({len(category.skills)} skills):\n"
            summary += f"  {', '.join(category.skills[:10])}"
            if len(category.skills) > 10:
                summary += f" ... and {len(category.skills) - 10} more"
            summary += "\n\n"
        
        summary += f"=== SCRAPING SETTINGS ===\n"
        summary += f"Max pages per site: {self.config.max_pages_per_site}\n"
        summary += f"Delay between requests: {self.config.delay_between_requests}s\n"
        summary += f"Use Selenium: {'Yes' if self.config.use_selenium else 'No'}\n"
        
        self.config_summary.setPlainText(summary)
