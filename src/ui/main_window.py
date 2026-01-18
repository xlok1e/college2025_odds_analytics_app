import sys
from pathlib import Path

from PySide6.QtCore import QSize, QThread
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)

# Добавляем корневую директорию в path для импорта config и db_manager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import db_config
from db_manager import DatabaseManager
from src.data.event_repository import EventRepository
from src.data.odds_service import OddsService
from src.styles.theme import COLORS
from src.ui.widgets.event_detail import EventDetail
from src.ui.widgets.events_list import EventsList
from src.ui.workers.data_loader import EventLoader


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Безопасная инициализация БД
        try:
            self.db = DatabaseManager.from_env()
            self.db.initialize()
            print("✓ База данных успешно инициализирована")
        except Exception as e:
            print(f"✗ Критическая ошибка инициализации БД: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

        # Сохраняем db_manager для доступа из виджетов
        self.db_manager = self.db

        self.event_repository = EventRepository(self.db)
        self.odds_service = OddsService(self.db)
        self.events = []
        self.selected_event_id = None

        self.event_loader_thread = None
        self.event_loader_worker = None

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
        """Асинхронная загрузка события при клике"""
        self.selected_event_id = event_id

        # Показываем состояние загрузки СРАЗУ
        self.event_detail.show_loading_state()

        # Останавливаем предыдущую загрузку если она еще идет
        if self.event_loader_thread and self.event_loader_thread.isRunning():
            self.event_loader_thread.quit()
            self.event_loader_thread.wait()

        # Создаем новый поток для загрузки события
        self.event_loader_thread = QThread()
        self.event_loader_worker = EventLoader(
            self.event_repository,
            event_id
        )
        self.event_loader_worker.moveToThread(self.event_loader_thread)

        # Подключаем сигналы
        self.event_loader_thread.started.connect(self.event_loader_worker.run)
        self.event_loader_worker.finished.connect(self.on_event_loaded)
        self.event_loader_worker.error.connect(self.on_event_load_error)
        self.event_loader_worker.finished.connect(self.event_loader_thread.quit)
        self.event_loader_worker.error.connect(self.event_loader_thread.quit)

        # Запускаем поток
        self.event_loader_thread.start()

    def on_event_loaded(self, event):
        """Обработка загруженного события"""
        if event:
            # Устанавливаем событие - виджеты создаются с уже установленным odds_service
            self.event_detail.set_event(event)
        else:
            self.show_error_message("Событие не найдено")

    def on_event_load_error(self, error_message):
        """Обработка ошибки загрузки события"""
        print(f"✗ Ошибка загрузки события: {error_message}")
        self.show_error_message(f"Ошибка загрузки события: {error_message}")

    def closeEvent(self, event):
        """Обработка закрытия окна - останавливаем все потоки"""
        # Останавливаем поток загрузки события
        if self.event_loader_thread and self.event_loader_thread.isRunning():
            self.event_loader_thread.quit()
            self.event_loader_thread.wait()

        # Останавливаем потоки в виджете деталей
        if hasattr(self.event_detail, 'chart') and self.event_detail.chart:
            if hasattr(self.event_detail.chart, 'loader_thread') and self.event_detail.chart.loader_thread:
                if self.event_detail.chart.loader_thread.isRunning():
                    self.event_detail.chart.loader_thread.quit()
                    self.event_detail.chart.loader_thread.wait()

        if hasattr(self.event_detail, 'statistics') and self.event_detail.statistics:
            if hasattr(self.event_detail.statistics, 'loader_thread') and self.event_detail.statistics.loader_thread:
                if self.event_detail.statistics.loader_thread.isRunning():
                    self.event_detail.statistics.loader_thread.quit()
                    self.event_detail.statistics.loader_thread.wait()

        event.accept()

    def on_event_deleted(self):
        if self.selected_event_id:
            success = self.event_repository.delete_event(self.selected_event_id)
            if success:
                self.load_events()
                self.events_list.set_events(self.events)
                self.selected_event_id = None
                self.event_detail.set_event(None)

                self.show_success_message("Событие успешно удалено")
            else:
                self.show_error_message("Не удалось удалить событие. Попробуйте снова.")

    def show_success_message(self, message: str):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Успех")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def show_error_message(self, message: str):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Ошибка")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()

    def refresh_events(self):
        self.load_events()
        self.events_list.set_events(self.events)

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.db.close()
        event.accept()
