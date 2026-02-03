"""Виджет статистики по коэффициентам"""

from typing import Optional

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QFrame, QGridLayout, QLabel, QVBoxLayout, QWidget

from src.styles.theme import COLORS
from src.ui.workers.data_loader import StatisticsDataLoader


class StatCard(QFrame):
    """Карточка со статистическим показателем"""

    def __init__(self, label: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.label_text = label
        self.value_text = value
        self.subtitle_text = subtitle
        self.setup_ui()

    def setup_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
        """)

        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        self.label_widget = QLabel(self.label_text)
        self.label_widget.setStyleSheet(
            f"color: {COLORS['muted_foreground']}; font-size: 12px; padding: 0;"
        )
        layout.addWidget(self.label_widget)

        self.value_widget = QLabel(self.value_text)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        self.value_widget.setFont(value_font)
        self.value_widget.setStyleSheet("padding: 0;")
        layout.addWidget(self.value_widget)

        if self.subtitle_text:
            self.subtitle_widget = QLabel(self.subtitle_text)
            self.subtitle_widget.setStyleSheet(
                f"color: {COLORS['muted_foreground']}; font-size: 12px; padding: 0;"
            )
            layout.addWidget(self.subtitle_widget)

    def update_value(self, value: str, subtitle: str = ""):
        """Обновить значение карточки"""
        self.value_text = value
        self.value_widget.setText(value)

        if subtitle and hasattr(self, 'subtitle_widget'):
            self.subtitle_text = subtitle
            self.subtitle_widget.setText(subtitle)


class Statistics(QWidget):
    """Виджет статистики по коэффициенту"""

    data_loaded = Signal()  # Сигнал о завершении загрузки данных

    def __init__(self, odds_service=None, event_id: Optional[int] = None,
                 bet_type: str = "П1", parent=None, auto_load=False):
        super().__init__(parent)
        self.odds_service = odds_service
        self.event_id = event_id
        self.bet_type = bet_type

        self.min_card = None
        self.max_card = None
        self.avg_card = None
        self.changes_card = None
        self.percent_value_label = None

        self.loader_thread = None
        self.loader_worker = None
        self.loading_request_id = 0  # Счетчик запросов для отслеживания актуальности данных
        self.pending_request_id = None  # ID ожидающего запроса

        self.setup_ui()

        # Загружаем данные только если auto_load=True
        if auto_load and self.odds_service and self.event_id:
            self.load_data_async()

    def setup_ui(self):
        """Создание UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container = QWidget()
        container.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        title = QLabel("СТАТИСТИКА ПО КОЭФФИЦИЕНТУ")
        title.setStyleSheet(
            "background: transparent; border: none; padding: 0; "
            "font-size: 14px; font-weight: 600;"
        )
        layout.addWidget(title)

        self.bet_label = QLabel(self.bet_type)
        self.bet_label.setStyleSheet(
            f"color: {COLORS['muted_foreground']}; font-size: 14px; border: none; margin-top: 6px; margin-left: -2px;"
        )
        layout.addWidget(self.bet_label)

        grid = QGridLayout()
        grid.setSpacing(16)
        grid.setContentsMargins(0, 20, 0, 0)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Карточки со статистикой
        self.min_card = StatCard("Минимальное значение", "—", "")
        self.max_card = StatCard("Максимальное значение", "—", "")
        self.avg_card = StatCard("Среднее значение", "—")
        self.changes_card = StatCard("Количество изменений", "—")

        # Карточка процента изменения
        percent_card = QWidget()
        percent_card.setStyleSheet(f"""
            QWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0px;
            }}
        """)
        from PySide6.QtWidgets import QSizePolicy
        percent_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        percent_layout = QVBoxLayout(percent_card)
        percent_layout.setContentsMargins(16, 16, 16, 16)
        percent_layout.setSpacing(8)

        percent_label = QLabel("Процент изменения")
        percent_label.setStyleSheet(
            f"color: {COLORS['muted_foreground']}; font-size: 11px; "
            f"background: transparent; border: none; padding: 0;"
        )
        percent_layout.addWidget(percent_label)

        self.percent_value_label = QLabel("—")
        percent_font = QFont()
        percent_font.setPointSize(20)
        percent_font.setBold(True)
        self.percent_value_label.setFont(percent_font)
        self.percent_value_label.setStyleSheet(
            f"color: {COLORS['muted_foreground']}; background: transparent; "
            f"border: none; padding: 0;"
        )
        percent_layout.addWidget(self.percent_value_label)

        self.percent_subtitle = QLabel("от первого до последнего значения")
        self.percent_subtitle.setStyleSheet(
            f"color: {COLORS['muted_foreground']}; font-size: 11px; "
            f"background: transparent; border: none; padding: 0;"
        )
        percent_layout.addWidget(self.percent_subtitle)

        grid.addWidget(self.min_card, 0, 0)
        grid.addWidget(self.max_card, 0, 1)
        grid.addWidget(self.avg_card, 1, 0)
        grid.addWidget(self.changes_card, 1, 1)
        grid.addWidget(percent_card, 2, 0, 1, 2)

        layout.addLayout(grid)
        layout.addStretch()

        main_layout.addWidget(container)

    def load_data_async(self, bookmaker: Optional[str] = None):
        """Асинхронная загрузка данных из БД"""
        if not self.odds_service or not self.event_id:
            return

        # Проверяем что виджет не был удален
        try:
            if not self.bet_label or self.bet_label.isHidden():
                return
        except RuntimeError:
            # Виджет уже удален
            return

        # Показываем индикатор загрузки
        self.bet_label.setText(f"{self.bet_type} • Загрузка...")

        # Увеличиваем счетчик запросов
        self.loading_request_id += 1
        current_request_id = self.loading_request_id

        # Если поток уже работает, сохраняем запрос и ждем завершения текущего
        if self.loader_thread and self.loader_thread.isRunning():
            self.pending_request_id = current_request_id
            return

        # Запускаем загрузку
        self.start_loading(current_request_id)

    def start_loading(self, request_id: int):
        """Запуск загрузки данных"""
        self.pending_request_id = None

        # Создаем новый поток для загрузки данных
        self.loader_thread = QThread()
        self.loader_worker = StatisticsDataLoader(
            self.odds_service,
            self.event_id,
            self.bet_type
        )
        self.loader_worker.moveToThread(self.loader_thread)

        # Сохраняем request_id в worker для проверки актуальности
        self.loader_worker.request_id = request_id

        # Подключаем сигналы
        self.loader_thread.started.connect(self.loader_worker.run)
        self.loader_worker.finished.connect(self.on_data_loaded)
        self.loader_worker.error.connect(self.on_data_error)
        self.loader_worker.finished.connect(self.on_loading_complete)
        self.loader_worker.error.connect(self.on_loading_complete)

        # Запускаем поток
        self.loader_thread.start()

    def on_data_loaded(self, stats):
        """Обработка загруженных данных"""
        # Проверяем актуальность данных - игнорируем устаревшие результаты
        if self.loader_worker and hasattr(self.loader_worker, 'request_id') and self.loader_worker.request_id != self.loading_request_id:
            print(f"[Statistics] Игнорируем устаревшие данные (request_id={self.loader_worker.request_id}, current={self.loading_request_id})")
            # ВСЕГДА испускаем сигнал, даже для устаревших данных
            self.data_loaded.emit()
            return

        # Проверяем что виджет не был удален
        try:
            if not self.bet_label or self.bet_label.isHidden():
                self.data_loaded.emit()
                return
        except RuntimeError:
            # Виджет уже удален
            self.data_loaded.emit()
            return

        self.bet_label.setText(self.bet_type)

        if stats['changes_count'] > 0:
            # Обновляем карточки
            min_datetime = stats['min_datetime']
            if hasattr(min_datetime, 'strftime'):
                min_dt_str = min_datetime.strftime('%d.%m.%Y %H:%M')
            else:
                min_dt_str = str(min_datetime)

            max_datetime = stats['max_datetime']
            if hasattr(max_datetime, 'strftime'):
                max_dt_str = max_datetime.strftime('%d.%m.%Y %H:%M')
            else:
                max_dt_str = str(max_datetime)

            try:
                self.min_card.update_value(f"{stats['min_value']:.2f}", min_dt_str)
                self.max_card.update_value(f"{stats['max_value']:.2f}", max_dt_str)
                self.avg_card.update_value(f"{stats['avg_value']:.2f}")
                self.changes_card.update_value(str(stats['changes_count']))
            except (RuntimeError, AttributeError):
                # Виджеты уже удалены
                return

            # Обновляем процент изменения
            percent = stats['percent_change']
            percent_text = f"{percent:+.1f}%"

            # Выбираем цвет в зависимости от направления изменения
            if percent > 0:
                color = COLORS.get('success', '#22c55e')
            elif percent < 0:
                color = COLORS['destructive']
            else:
                color = COLORS['muted_foreground']

            try:
                self.percent_value_label.setText(percent_text)
                self.percent_value_label.setStyleSheet(
                    f"color: {color}; background: transparent; border: none; padding: 0;"
                )
            except (RuntimeError, AttributeError):
                # Виджеты уже удалены
                return
        else:
            # Нет данных
            try:
                self.min_card.update_value("—", "")
                self.max_card.update_value("—", "")
                self.avg_card.update_value("—")
                self.changes_card.update_value("0")
                self.percent_value_label.setText("—")
            except (RuntimeError, AttributeError):
                # Виджеты уже удалены
                return

        # ВСЕГДА испускаем сигнал о завершении загрузки
        self.data_loaded.emit()

    def on_data_error(self, error_message):
        """Обработка ошибки загрузки"""
        # Проверяем актуальность данных - игнорируем устаревшие ошибки
        if self.loader_worker and hasattr(self.loader_worker, 'request_id') and self.loader_worker.request_id != self.loading_request_id:
            print(f"[Statistics] Игнорируем устаревшую ошибку (request_id={self.loader_worker.request_id}, current={self.loading_request_id})")
            # ВСЕГДА испускаем сигнал, даже для устаревших ошибок
            self.data_loaded.emit()
            return

        print(f"✗ Ошибка загрузки статистики: {error_message}")

        # Проверяем что виджет не был удален
        try:
            if self.bet_label and not self.bet_label.isHidden():
                self.bet_label.setText(f"{self.bet_type} • Ошибка загрузки")
        except RuntimeError:
            # Виджет уже удален
            pass

        # ВСЕГДА испускаем сигнал о завершении загрузки
        self.data_loaded.emit()

    def on_loading_complete(self):
        """Вызывается когда загрузка завершена (успешно или с ошибкой)"""
        # Очищаем поток
        if self.loader_thread:
            self.loader_thread.quit()
            self.loader_thread.wait()  # Теперь безопасно ждать
            self.loader_worker.deleteLater()
            self.loader_thread.deleteLater()
            self.loader_thread = None
            self.loader_worker = None

        # Если есть ожидающий запрос, обрабатываем его
        if self.pending_request_id is not None:
            pending_id = self.pending_request_id
            # Проверяем, что это все еще актуальный запрос
            if pending_id == self.loading_request_id:
                self.start_loading(pending_id)

    def update_data(self, event_id: int, bet_type: str, bookmaker: Optional[str] = None):
        """Обновление данных статистики"""
        self.event_id = event_id
        self.bet_type = bet_type

        self.load_data_async(bookmaker)

    def set_odds_service(self, odds_service):
        """Установить сервис коэффициентов"""
        self.odds_service = odds_service
        if self.event_id:
            self.load_data_async()
