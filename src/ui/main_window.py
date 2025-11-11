from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont

from src.data.mock_data import MOCK_EVENTS
from src.ui.widgets.events_list import EventsList
from src.ui.widgets.event_detail import EventDetail
from src.styles.theme import COLORS


class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.selected_event_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Анализ коэффициентов букмекерских контор")
        self.setMinimumSize(QSize(1400, 900))
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(24)
        
        header_layout = QVBoxLayout()
        header_layout.setSpacing(0)
        
        title_label = QLabel("Анализ коэффициентов букмекерских контор")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {COLORS['foreground']}; font-size: 28px; font-family: 'Google Sans';")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Система учета и анализа изменений коэффициентов спортивных событий")
        subtitle_label.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 16px; font-family: 'Google Sans';")
        header_layout.addWidget(subtitle_label)
        
        main_layout.addLayout(header_layout)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(16)
        
        self.events_list = EventsList(MOCK_EVENTS)
        self.events_list.event_selected.connect(self.on_event_selected)
        content_layout.addWidget(self.events_list, 60)
        
        self.event_detail = EventDetail(None)
        self.event_detail.event_deleted.connect(self.on_event_deleted)
        content_layout.addWidget(self.event_detail, 40)
        
        main_layout.addLayout(content_layout)
        
    def on_event_selected(self, event_id: int):
        self.selected_event_id = event_id
        
        event = next((e for e in MOCK_EVENTS if e.id == event_id), None)
        
        if event:
            self.event_detail.set_event(event)
            
    def on_event_deleted(self):
        self.selected_event_id = None
        self.event_detail.set_event(None)
