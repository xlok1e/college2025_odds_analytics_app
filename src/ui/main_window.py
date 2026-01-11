import sys
from pathlib import Path

from PySide6.QtCore import QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QMainWindow, QVBoxLayout, QWidget

# Добавляем корневую директорию в path для импорта config и db_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import db_config
from db_manager import DatabaseManager
from src.data.event_repository import EventRepository
from src.data.odds_service import OddsService
from src.styles.theme import COLORS
from src.ui.widgets.event_detail import EventDetail
from src.ui.widgets.events_list import EventsList


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.db = DatabaseManager(db_config)
        self.db.initialize()

        # Сохраняем db_manager для доступа из виджетов
        self.db_manager = self.db

        self.event_repository = EventRepository(self.db)
        self.odds_service = OddsService(self.db)
        self.events = []
        self.selected_event_id = None

        self.load_events()
        self.init_ui()

    def load_events(self):
        """Загрузка событий из базы данных"""
        try:
            self.events = self.event_repository.get_all_events()
            print(f"✓ Загружено событий: {len(self.events)}")
        except Exception as e:
            print(f"✗ Ошибка загрузки событий: {e}")
            self.events = []

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

        self.events_list = EventsList(self.events)
        self.events_list.event_selected.connect(self.on_event_selected)
        content_layout.addWidget(self.events_list, 60)

        self.event_detail = EventDetail(None, self.odds_service)
        self.event_detail.event_deleted.connect(self.on_event_deleted)
        content_layout.addWidget(self.event_detail, 40)

        main_layout.addLayout(content_layout)

    def on_event_selected(self, event_id: int):
        self.selected_event_id = event_id
        event = self.event_repository.get_event_by_id(event_id)

        if event:
            self.event_detail.set_odds_service(self.odds_service)
            self.event_detail.set_event(event)

    def on_event_deleted(self):
        if self.selected_event_id:
            success = self.event_repository.delete_event(self.selected_event_id)
            if success:
                self.load_events()
                self.events_list.set_events(self.events)
                self.selected_event_id = None
                self.event_detail.set_event(None)

    def refresh_events(self):
        self.load_events()
        self.events_list.set_events(self.events)

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.db.close()
        event.accept()
