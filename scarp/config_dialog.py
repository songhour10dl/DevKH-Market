from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QPushButton, QLineEdit,
    QLabel, QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox,
    QMessageBox, QInputDialog, QColorDialog, QFormLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from typing import List
from data_models import JobSite, SkillCategory, ScrapingConfig

class ConfigDialog(QDialog):
    def __init__(self, config: ScrapingConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Configuration")
        self.setModal(True)
        self.resize(800, 600)
        
        self.init_ui()
        self.load_config_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        self.tab_widget = QTabWidget()
        
        self.sites_tab = self.create_sites_tab()
        self.tab_widget.addTab(self.sites_tab, "Job Sites")
        
        self.queries_tab = self.create_queries_tab()
        self.tab_widget.addTab(self.queries_tab, "Search Queries")
        
        self.skills_tab = self.create_skills_tab()
        self.tab_widget.addTab(self.skills_tab, "Skills")
        
        self.settings_tab = self.create_settings_tab()
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        layout.addWidget(self.tab_widget)
        
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def create_sites_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Job Sites:"))
        self.sites_list = QListWidget()
        self.sites_list.itemChanged.connect(self.on_site_item_changed)
        left_layout.addWidget(self.sites_list)
        
        site_buttons = QHBoxLayout()
        add_site_btn = QPushButton("Add Site")
        add_site_btn.clicked.connect(self.add_job_site)
        site_buttons.addWidget(add_site_btn)
        
        edit_site_btn = QPushButton("Edit Site")
        edit_site_btn.clicked.connect(self.edit_job_site)
        site_buttons.addWidget(edit_site_btn)
        
        remove_site_btn = QPushButton("Remove Site")
        remove_site_btn.clicked.connect(self.remove_job_site)
        site_buttons.addWidget(remove_site_btn)
        
        left_layout.addLayout(site_buttons)
        layout.addWidget(left_panel)
        
        right_panel = QGroupBox("Site Details")
        right_layout = QFormLayout(right_panel)
        
        self.site_name_edit = QLineEdit()
        self.site_name_edit.setReadOnly(True)
        right_layout.addRow("Name:", self.site_name_edit)
        
        self.site_url_edit = QLineEdit()
        self.site_url_edit.setReadOnly(True)
        right_layout.addRow("Base URL:", self.site_url_edit)
        
        self.site_search_edit = QLineEdit()
        self.site_search_edit.setReadOnly(True)
        right_layout.addRow("Search Template:", self.site_search_edit)
        
        layout.addWidget(right_panel)
        
        return widget
    
    def create_queries_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        layout.addWidget(QLabel("Search Queries:"))
        
        self.queries_list = QListWidget()
        layout.addWidget(self.queries_list)
        
        query_buttons = QHBoxLayout()
        
        add_query_btn = QPushButton("Add Query")
        add_query_btn.clicked.connect(self.add_search_query)
        query_buttons.addWidget(add_query_btn)
        
        edit_query_btn = QPushButton("Edit Query")
        edit_query_btn.clicked.connect(self.edit_search_query)
        query_buttons.addWidget(edit_query_btn)
        
        remove_query_btn = QPushButton("Remove Query")
        remove_query_btn.clicked.connect(self.remove_search_query)
        query_buttons.addWidget(remove_query_btn)
        
        query_buttons.addStretch()
        
        layout.addLayout(query_buttons)
        
        return widget
    
    def create_skills_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("Skill Categories:"))
        self.categories_list = QListWidget()
        self.categories_list.currentItemChanged.connect(self.on_category_selected)
        left_layout.addWidget(self.categories_list)
        
        cat_buttons = QHBoxLayout()
        add_cat_btn = QPushButton("Add Category")
        add_cat_btn.clicked.connect(self.add_skill_category)
        cat_buttons.addWidget(add_cat_btn)
        
        edit_cat_btn = QPushButton("Edit Category")
        edit_cat_btn.clicked.connect(self.edit_skill_category)
        cat_buttons.addWidget(edit_cat_btn)
        
        remove_cat_btn = QPushButton("Remove Category")
        remove_cat_btn.clicked.connect(self.remove_skill_category)
        cat_buttons.addWidget(remove_cat_btn)
        
        left_layout.addLayout(cat_buttons)
        layout.addWidget(left_panel)
        
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("Skills in Category:"))
        self.skills_list = QListWidget()
        right_layout.addWidget(self.skills_list)
        
        skill_buttons = QHBoxLayout()
        add_skill_btn = QPushButton("Add Skill")
        add_skill_btn.clicked.connect(self.add_skill)
        skill_buttons.addWidget(add_skill_btn)
        
        edit_skill_btn = QPushButton("Edit Skill")
        edit_skill_btn.clicked.connect(self.edit_skill)
        skill_buttons.addWidget(edit_skill_btn)
        
        remove_skill_btn = QPushButton("Remove Skill")
        remove_skill_btn.clicked.connect(self.remove_skill)
        skill_buttons.addWidget(remove_skill_btn)
        
        right_layout.addLayout(skill_buttons)
        layout.addWidget(right_panel)
        
        return widget
    
    def create_settings_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        settings_group = QGroupBox("Scraping Settings")
        settings_layout = QFormLayout(settings_group)
        
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setRange(1, 20)
        settings_layout.addRow("Max pages per site:", self.max_pages_spin)
        
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.1, 10.0)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setSuffix(" seconds")
        settings_layout.addRow("Delay between requests:", self.delay_spin)
        
        self.selenium_check = QCheckBox("Use Selenium for JavaScript-heavy sites")
        settings_layout.addRow(self.selenium_check)
        
        layout.addWidget(settings_group)
        layout.addStretch()
        
        return widget
    
    def load_config_data(self):
        self.sites_list.clear()
        for site in self.config.job_sites:
            item = QListWidgetItem(site.name)
            item.setCheckState(Qt.CheckState.Checked if site.is_active else Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, site)
            self.sites_list.addItem(item)
        
        self.queries_list.clear()
        for query in self.config.search_queries:
            self.queries_list.addItem(query)
        
        self.categories_list.clear()
        for category in self.config.skill_categories:
            item = QListWidgetItem(category.name)
            item.setData(Qt.ItemDataRole.UserRole, category)
            self.categories_list.addItem(item)
        
        self.max_pages_spin.setValue(self.config.max_pages_per_site)
        self.delay_spin.setValue(self.config.delay_between_requests)
        self.selenium_check.setChecked(self.config.use_selenium)
    
    def on_site_item_changed(self, item: QListWidgetItem):
        site = item.data(Qt.ItemDataRole.UserRole)
        if site:
            site.is_active = item.checkState() == Qt.CheckState.Checked
            
            self.site_name_edit.setText(site.name)
            self.site_url_edit.setText(site.base_url)
            self.site_search_edit.setText(site.search_url_template)
    
    def on_category_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        self.skills_list.clear()
        if current:
            category = current.data(Qt.ItemDataRole.UserRole)
            if category:
                for skill in category.skills:
                    self.skills_list.addItem(skill)
    
    def add_job_site(self):
        name, ok = QInputDialog.getText(self, "Add Job Site", "Site name:")
        if not ok or not name.strip():
            return
        
        base_url, ok = QInputDialog.getText(self, "Add Job Site", "Base URL:")
        if not ok or not base_url.strip():
            return
        
        search_template, ok = QInputDialog.getText(
            self, "Add Job Site", 
            "Search URL template (use {query} for search term):"
        )
        if not ok or not search_template.strip():
            return
        
        site = JobSite(
            name=name.strip(),
            base_url=base_url.strip(),
            search_url_template=search_template.strip()
        )
        
        self.config.job_sites.append(site)
        
        item = QListWidgetItem(site.name)
        item.setCheckState(Qt.CheckState.Checked)
        item.setData(Qt.ItemDataRole.UserRole, site)
        self.sites_list.addItem(item)
    
    def edit_job_site(self):
        current_item = self.sites_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a site to edit.")
            return
        
        site = current_item.data(Qt.ItemDataRole.UserRole)
        if not site:
            return
        
        name, ok = QInputDialog.getText(self, "Edit Job Site", "Site name:", text=site.name)
        if not ok:
            return
        
        base_url, ok = QInputDialog.getText(self, "Edit Job Site", "Base URL:", text=site.base_url)
        if not ok:
            return
        
        search_template, ok = QInputDialog.getText(
            self, "Edit Job Site", 
            "Search URL template:", 
            text=site.search_url_template
        )
        if not ok:
            return
        
        site.name = name.strip()
        site.base_url = base_url.strip()
        site.search_url_template = search_template.strip()
        
        current_item.setText(site.name)
        
        self.site_name_edit.setText(site.name)
        self.site_url_edit.setText(site.base_url)
        self.site_search_edit.setText(site.search_url_template)
    
    def remove_job_site(self):
        current_item = self.sites_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a site to remove.")
            return
        
        site = current_item.data(Qt.ItemDataRole.UserRole)
        if site in self.config.job_sites:
            self.config.job_sites.remove(site)
        
        self.sites_list.takeItem(self.sites_list.row(current_item))
    
    def add_search_query(self):
        query, ok = QInputDialog.getText(self, "Add Search Query", "Search query:")
        if ok and query.strip():
            self.config.search_queries.append(query.strip())
            self.queries_list.addItem(query.strip())
    
    def edit_search_query(self):
        current_item = self.queries_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a query to edit.")
            return
        
        old_query = current_item.text()
        new_query, ok = QInputDialog.getText(self, "Edit Search Query", "Search query:", text=old_query)
        
        if ok and new_query.strip():
            try:
                index = self.config.search_queries.index(old_query)
                self.config.search_queries[index] = new_query.strip()
                current_item.setText(new_query.strip())
            except ValueError:
                pass
    
    def remove_search_query(self):
        current_item = self.queries_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a query to remove.")
            return
        
        query = current_item.text()
        if query in self.config.search_queries:
            self.config.search_queries.remove(query)
        
        self.queries_list.takeItem(self.queries_list.row(current_item))
    
    def add_skill_category(self):
        """Add a new skill category"""
        name, ok = QInputDialog.getText(self, "Add Skill Category", "Category name:")
        if not ok or not name.strip():
            return
        
        color = QColorDialog.getColor(QColor("#3498db"), self, "Choose category color")
        if not color.isValid():
            color = QColor("#3498db")
        
        category = SkillCategory(
            name=name.strip(),
            skills=[],
            color=color.name()
        )
        
        self.config.skill_categories.append(category)
        
        item = QListWidgetItem(category.name)
        item.setData(Qt.ItemDataRole.UserRole, category)
        self.categories_list.addItem(item)
    
    def edit_skill_category(self):
        current_item = self.categories_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a category to edit.")
            return
        
        category = current_item.data(Qt.ItemDataRole.UserRole)
        if not category:
            return
        
        name, ok = QInputDialog.getText(self, "Edit Skill Category", "Category name:", text=category.name)
        if not ok:
            return
        
        current_color = QColor(category.color)
        color = QColorDialog.getColor(current_color, self, "Choose category color")
        if not color.isValid():
            color = current_color
        
        category.name = name.strip()
        category.color = color.name()
        
        current_item.setText(category.name)
    
    def remove_skill_category(self):
        current_item = self.categories_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a category to remove.")
            return
        
        category = current_item.data(Qt.ItemDataRole.UserRole)
        if category in self.config.skill_categories:
            self.config.skill_categories.remove(category)
        
        self.categories_list.takeItem(self.categories_list.row(current_item))
        self.skills_list.clear()
    
    def add_skill(self):
        current_item = self.categories_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Warning", "Please select a category first.")
            return
        
        category = current_item.data(Qt.ItemDataRole.UserRole)
        if not category:
            return
        
        skill, ok = QInputDialog.getText(self, "Add Skill", "Skill name:")
        if ok and skill.strip():
            category.skills.append(skill.strip())
            self.skills_list.addItem(skill.strip())
    
    def edit_skill(self):
        current_cat_item = self.categories_list.currentItem()
        current_skill_item = self.skills_list.currentItem()
        
        if not current_cat_item or not current_skill_item:
            QMessageBox.warning(self, "Warning", "Please select a category and skill to edit.")
            return
        
        category = current_cat_item.data(Qt.ItemDataRole.UserRole)
        if not category:
            return
        
        old_skill = current_skill_item.text()
        new_skill, ok = QInputDialog.getText(self, "Edit Skill", "Skill name:", text=old_skill)
        
        if ok and new_skill.strip():
            try:
                index = category.skills.index(old_skill)
                category.skills[index] = new_skill.strip()
                current_skill_item.setText(new_skill.strip())
            except ValueError:
                pass
    
    def remove_skill(self):
        current_cat_item = self.categories_list.currentItem()
        current_skill_item = self.skills_list.currentItem()
        
        if not current_cat_item or not current_skill_item:
            QMessageBox.warning(self, "Warning", "Please select a category and skill to remove.")
            return
        
        category = current_cat_item.data(Qt.ItemDataRole.UserRole)
        if not category:
            return
        
        skill = current_skill_item.text()
        if skill in category.skills:
            category.skills.remove(skill)
        
        self.skills_list.takeItem(self.skills_list.row(current_skill_item))
    
    def get_config(self) -> ScrapingConfig:
        self.config.max_pages_per_site = self.max_pages_spin.value()
        self.config.delay_between_requests = self.delay_spin.value()
        self.config.use_selenium = self.selenium_check.isChecked()
        
        return self.config
