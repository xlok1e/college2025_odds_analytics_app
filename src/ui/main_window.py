import sys
from pathlib import Path

from PySide6.QtCore import QSize, Qt, QThread
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
        self.pending_event_id = None  # ID события, ожидающего загрузки

        self.events_refresh_thread = None
        self.events_refresh_worker = None

        self.loading_event_id = None  # ID события, которое загружается в данный момент

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
        # Сохраняем ID выбранного события
        self.selected_event_id = event_id

        print(f"[MainWindow] Выбрано событие ID={event_id}")

        # Показываем состояние загрузки СРАЗУ
        self.event_detail.show_loading_state()

        # Если поток уже работает, сохраняем запрос и ждем завершения текущего
        if self.event_loader_thread and self.event_loader_thread.isRunning():
            print("[MainWindow] Загрузка уже выполняется, запрос будет обработан после завершения текущего")
            self.pending_event_id = event_id
            return

        # Запускаем загрузку
        self.start_event_loading(event_id)

    def start_event_loading(self, event_id: int):
        """Запуск загрузки события"""
        self.loading_event_id = event_id
        self.pending_event_id = None

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
        self.event_loader_worker.finished.connect(self.on_event_loading_complete)
        self.event_loader_worker.error.connect(self.on_event_loading_complete)

        # Запускаем поток
        self.event_loader_thread.start()

    def on_event_loaded(self, event):
        """Обработка загруженного события"""
        if not event:
            print("[MainWindow] Событие не найдено")
            # Проверяем, это все еще актуальное событие?
            if event and hasattr(event, 'id') and event.id == self.selected_event_id:
                self.show_error_message("Событие не найдено")
            self.loading_event_id = None
            return

        # Проверяем, это все еще актуальное выбранное событие?
        if event.id != self.selected_event_id:
            print(f"[MainWindow] Игнорируем устаревшие данные для события ID={event.id}, актуальное ID={self.selected_event_id}")
            return

        print(f"[MainWindow] Загружено событие ID={event.id}, отображаем данные")
        # Устанавливаем событие - виджеты создаются с уже установленным odds_service
        self.event_detail.set_event(event)

    def on_event_load_error(self, error_message):
        """Обработка ошибки загрузки события"""
        print(f"✗ Ошибка загрузки события: {error_message}")
        # Показываем ошибку только если это все еще актуальное событие
        if self.loading_event_id == self.selected_event_id:
            self.show_error_message(f"Ошибка загрузки события: {error_message}")

    def on_event_loading_complete(self):
        """Вызывается когда загрузка события завершена (успешно или с ошибкой)"""
        print("[MainWindow] Загрузка события завершена")

        # Очищаем поток
        if self.event_loader_thread:
            self.event_loader_thread.quit()
            self.event_loader_thread.wait()  # Теперь безопасно ждать, так как поток уже завершился
            if self.event_loader_worker:
                self.event_loader_worker.deleteLater()
            if self.event_loader_thread:
                self.event_loader_thread.deleteLater()
            self.event_loader_thread = None
            self.event_loader_worker = None

        self.loading_event_id = None

        # Если есть ожидающий запрос, обрабатываем его
        if self.pending_event_id is not None:
            pending_id = self.pending_event_id
            print(f"[MainWindow] Обрабатываем ожидающий запрос для события ID={pending_id}")
            # Проверяем, что это все еще актуальный выбор
            if pending_id == self.selected_event_id:
                self.start_event_loading(pending_id)
            else:
                self.pending_event_id = None

    def on_event_deleted(self):
        """Обработка удаления события (оптимизированная версия)"""
        if self.selected_event_id:
            deleted_event_id = self.selected_event_id

            # Удаляем событие из БД
            success = self.event_repository.delete_event(deleted_event_id)

            if success:
                # Удаляем событие из локального списка (без запроса к БД)
                self.events = [e for e in self.events if e.id != deleted_event_id]

                # Обновляем UI мгновенно
                self.events_list.set_events(self.events)
                self.selected_event_id = None
                self.event_detail.set_event(None)

                self.show_success_message("Событие успешно удалено")

                print(f"✓ Событие {deleted_event_id} удалено (осталось {len(self.events)} событий)")
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

    def refresh_events_sync(self):
        """Синхронное обновление списка событий (для немедленного обновления после импорта)"""
        print("[MainWindow] Синхронное обновление списка событий...")
        try:
            # Принудительно обрабатываем события Qt для обновления UI
            from PySide6.QtWidgets import QApplication
            QApplication.processEvents()

            print("[MainWindow] Начало загрузки событий из БД...")
            # Загружаем события напрямую (синхронно)
            self.events = self.event_repository.get_all_events()
            print(f"[MainWindow] Загружено {len(self.events)} событий из БД")

            # Обновляем UI
            print("[MainWindow] Обновление UI...")
            self.events_list.set_events(self.events)
            print("[MainWindow] UI обновлен успешно")

            # Принудительно обновляем UI
            QApplication.processEvents()
        except Exception as e:
            print(f"[MainWindow] Ошибка при синхронной загрузке событий: {e}")
            import traceback
            traceback.print_exc()
            self.show_error_message(f"Ошибка обновления списка событий: {str(e)}")

    def refresh_events(self):
        """Асинхронное обновление списка событий после импорта"""
        print("[MainWindow] Начало обновления списка событий")

        # Показываем индикатор загрузки
        from PySide6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)

        # Если поток уже работает, пропускаем (обновление уже идет)
        if self.events_refresh_thread and self.events_refresh_thread.isRunning():
            print("[MainWindow] Обновление уже выполняется, запрос игнорируется")
            QApplication.restoreOverrideCursor()
            return

        # Запускаем обновление
        self.start_events_refresh()

    def start_events_refresh(self):
        """Запуск обновления списка событий"""
        print("[MainWindow] Запуск загрузки событий из БД...")

        # Создаем новый поток для загрузки событий
        self.events_refresh_thread = QThread()
        self.events_refresh_worker = EventLoader(self.event_repository, -1)  # -1 означает загрузку всех
        self.events_refresh_worker.moveToThread(self.events_refresh_thread)

        # Подключаем сигналы
        self.events_refresh_thread.started.connect(self.events_refresh_worker.load_all_events)
        self.events_refresh_worker.all_events_loaded.connect(self.on_events_refreshed)
        self.events_refresh_worker.error.connect(self.on_events_refresh_error)
        self.events_refresh_worker.all_events_loaded.connect(self.on_events_refresh_complete)
        self.events_refresh_worker.error.connect(self.on_events_refresh_complete)

        # Запускаем поток
        self.events_refresh_thread.start()
        print("[MainWindow] Поток обновления событий запущен")

    def on_events_refreshed(self, events):
        """Обработка завершения загрузки событий"""
        print(f"[MainWindow] События загружены: {len(events)} шт.")

        # Восстанавливаем курсор
        from PySide6.QtWidgets import QApplication
        QApplication.restoreOverrideCursor()

        # Обновляем список событий
        self.events = events
        self.events_list.set_events(self.events)

        print("[MainWindow] Список событий обновлен в UI")

    def on_events_refresh_error(self, error_msg):
        """Обработка ошибки при загрузке событий"""
        print(f"[MainWindow] Ошибка загрузки событий: {error_msg}")

        # Показываем ошибку
        self.show_error_message(f"Ошибка обновления списка событий: {error_msg}")

    def on_events_refresh_complete(self):
        """Вызывается когда загрузка событий завершена (успешно или с ошибкой)"""
        print("[MainWindow] Загрузка событий завершена, очищаем поток...")

        # Восстанавливаем курсор
        from PySide6.QtWidgets import QApplication
        QApplication.restoreOverrideCursor()

        # Очищаем поток
        if self.events_refresh_thread:
            self.events_refresh_thread.quit()
            self.events_refresh_thread.wait()  # Безопасно ждать, так как поток уже завершил работу
            if self.events_refresh_worker:
                self.events_refresh_worker.deleteLater()
            if self.events_refresh_thread:
                self.events_refresh_thread.deleteLater()
            self.events_refresh_thread = None
            self.events_refresh_worker = None

        print("[MainWindow] Поток обновления событий очищен")

    def closeEvent(self, event):
        """Обработка закрытия окна - останавливаем все потоки и закрываем БД"""
        # Останавливаем поток загрузки события
        if self.event_loader_thread and self.event_loader_thread.isRunning():
            self.event_loader_thread.quit()
            self.event_loader_thread.wait(1000)  # Ждем максимум 1 секунду

        # Останавливаем поток обновления списка событий
        if self.events_refresh_thread and self.events_refresh_thread.isRunning():
            self.events_refresh_thread.quit()
            self.events_refresh_thread.wait(1000)  # Ждем максимум 1 секунду

        # Останавливаем потоки в виджете деталей
        if hasattr(self.event_detail, 'chart') and self.event_detail.chart:
            if hasattr(self.event_detail.chart, 'loader_thread') and self.event_detail.chart.loader_thread:
                if self.event_detail.chart.loader_thread.isRunning():
                    self.event_detail.chart.loader_thread.quit()
                    self.event_detail.chart.loader_thread.wait(1000)  # Ждем максимум 1 секунду

        if hasattr(self.event_detail, 'statistics') and self.event_detail.statistics:
            if hasattr(self.event_detail.statistics, 'loader_thread') and self.event_detail.statistics.loader_thread:
                if self.event_detail.statistics.loader_thread.isRunning():
                    self.event_detail.statistics.loader_thread.quit()
                    self.event_detail.statistics.loader_thread.wait(1000)  # Ждем максимум 1 секунду

        # Закрываем соединение с БД
        self.db.close()
        event.accept()
