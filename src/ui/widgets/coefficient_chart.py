from typing import Optional

from PySide6.QtCore import QPointF, Qt, QThread, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.styles.theme import COLORS
from src.ui.workers.data_loader import ChartDataLoader


class ChartCanvas(QWidget):
    """Виджет для рисования графика"""
    def __init__(self, data_points, time_labels, value_labels, parent=None):
        super().__init__(parent)
        self.data_points = data_points
        self.time_labels = time_labels
        self.value_labels = value_labels
        self.setMinimumHeight(250)

    def update_data(self, data_points, time_labels, value_labels):
        """Обновить данные графика"""
        self.data_points = data_points
        self.time_labels = time_labels
        self.value_labels = value_labels
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        left_margin = 50
        right_margin = 30
        top_margin = 20
        bottom_margin = 50

        chart_width = width - left_margin - right_margin
        chart_height = height - top_margin - bottom_margin

        painter.fillRect(
            left_margin, top_margin,
            chart_width, chart_height,
            QColor(COLORS['background'])
        )

        pen = QPen(QColor(COLORS['border']))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawRect(left_margin, top_margin, chart_width, chart_height)

        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        for i in range(5):
            y = top_margin + (chart_height / 4) * i
            painter.drawLine(left_margin, int(y), left_margin + chart_width, int(y))

        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(2)
        pen.setColor(QColor(COLORS['foreground']))
        painter.setPen(pen)

        painter.drawLine(left_margin, top_margin, left_margin, top_margin + chart_height)
        painter.drawLine(left_margin, top_margin + chart_height,
                        left_margin + chart_width, top_margin + chart_height)

        painter.setPen(QColor(COLORS['muted_foreground']))
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)

        for i, label in enumerate(self.value_labels):
            y = top_margin + (chart_height / 4) * i
            painter.drawText(10, int(y + 5), label)

        if len(self.time_labels) > 1:
            x_step = chart_width / (len(self.time_labels) - 1)
            for i, label in enumerate(self.time_labels):
                x = left_margin + x_step * i
                painter.drawText(int(x - 20), top_margin + chart_height + 20, label)

        if len(self.data_points) > 1:
            path = QPainterPath()

            scaled_points = []
            for x, y, value in self.data_points:
                scaled_x = left_margin + (x / 600) * chart_width
                scaled_y = top_margin + (y / 200) * chart_height
                scaled_points.append((scaled_x, scaled_y, value))

            path.moveTo(scaled_points[0][0], scaled_points[0][1])

            for x, y, _ in scaled_points[1:]:
                path.lineTo(x, y)

            pen = QPen(QColor(COLORS['chart_1']))
            pen.setWidth(3)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            painter.setPen(pen)
            painter.drawPath(path)

            # Находим минимальное значение для выделения
            if self.data_points:
                min_value = min(val for _, _, val in self.data_points)

                for x, y, value in scaled_points:
                    if abs(value - min_value) < 0.01:
                        painter.setBrush(QColor(COLORS['destructive']))
                        painter.setPen(QPen(QColor(COLORS['card']), 2))
                        painter.drawEllipse(QPointF(x, y), 6, 6)
                    else:
                        painter.setBrush(QColor(COLORS['chart_1']))
                        painter.setPen(QPen(QColor(COLORS['card']), 2))
                        painter.drawEllipse(QPointF(x, y), 5, 5)


class CoefficientChart(QWidget):
    """Виджет графика изменения коэффициента"""

    data_loaded = Signal()  # Сигнал о завершении загрузки данных

    def __init__(self, odds_service=None, event_id: Optional[int] = None,
                 bet_type: str = "П1", bookmaker: str = "Все букмекеры", parent=None, auto_load=False):
        super().__init__(parent)
        self.odds_service = odds_service
        self.event_id = event_id
        self.bet_type = bet_type
        self.bookmaker = bookmaker

        self.data_points = []
        self.time_labels = ["00:00"]
        self.value_labels = ["0.0"]

        self.loader_thread = None
        self.loader_worker = None
        self.loading_request_id = 0  # Счетчик запросов для отслеживания актуальности данных
        self.pending_request_id = None  # ID ожидающего запроса

        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(350)

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

        self.title_label = QLabel("ГРАФИК ИЗМЕНЕНИЯ КОЭФФИЦИЕНТА")
        self.title_label.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 14px; font-weight: 600;")
        layout.addWidget(self.title_label)

        self.params_label = QLabel(f"{self.bet_type} • {self.bookmaker}")
        self.params_label.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 14px; border: none; margin-bottom: 10px; margin-left: -2px;")
        layout.addWidget(self.params_label)

        self.canvas = ChartCanvas(self.data_points, self.time_labels, self.value_labels)
        layout.addWidget(self.canvas)

        main_layout.addWidget(container)

    def load_data_async(self):
        """Асинхронная загрузка данных из БД"""
        if not self.odds_service or not self.event_id:
            return

        # Проверяем что виджет не был удален
        try:
            if not self.params_label or self.params_label.isHidden():
                return
        except RuntimeError:
            # Виджет уже удален
            return

        # Показываем индикатор загрузки
        self.params_label.setText(f"{self.bet_type} • {self.bookmaker} • Загрузка...")

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
        self.loader_worker = ChartDataLoader(
            self.odds_service,
            self.event_id,
            self.bet_type,
            self.bookmaker
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

    def on_data_loaded(self, data_points, time_labels, value_labels):
        """Обработка загруженных данных"""
        # Проверяем актуальность данных - игнорируем устаревшие результаты
        if self.loader_worker and hasattr(self.loader_worker, 'request_id') and self.loader_worker.request_id != self.loading_request_id:
            print(f"[CoefficientChart] Игнорируем устаревшие данные (request_id={self.loader_worker.request_id}, current={self.loading_request_id})")
            # ВСЕГДА испускаем сигнал, даже для устаревших данных
            self.data_loaded.emit()
            return

        # Проверяем что виджет не был удален
        try:
            if not self.params_label or self.params_label.isHidden():
                self.data_loaded.emit()
                return
        except RuntimeError:
            # Виджет уже удален
            self.data_loaded.emit()
            return

        self.params_label.setText(f"{self.bet_type} • {self.bookmaker}")

        if data_points:
            self.data_points = data_points
            self.time_labels = time_labels
            self.value_labels = value_labels
            try:
                self.canvas.update_data(data_points, time_labels, value_labels)
            except RuntimeError:
                pass
        else:
            # Нет данных
            self.data_points = []
            self.time_labels = ["Нет данных"]
            self.value_labels = ["0.0"]
            try:
                self.canvas.update_data([], ["Нет данных"], ["0.0"])
            except RuntimeError:
                pass

        # ВСЕГДА испускаем сигнал о завершении загрузки
        self.data_loaded.emit()

    def on_data_error(self, error_message):
        """Обработка ошибки загрузки"""
        # Проверяем актуальность данных - игнорируем устаревшие ошибки
        if self.loader_worker and hasattr(self.loader_worker, 'request_id') and self.loader_worker.request_id != self.loading_request_id:
            print(f"[CoefficientChart] Игнорируем устаревшую ошибку (request_id={self.loader_worker.request_id}, current={self.loading_request_id})")
            # ВСЕГДА испускаем сигнал, даже для устаревших ошибок
            self.data_loaded.emit()
            return

        print(f"✗ Ошибка загрузки данных графика: {error_message}")

        # Проверяем что виджет не был удален
        try:
            if self.params_label and not self.params_label.isHidden():
                self.params_label.setText(f"{self.bet_type} • {self.bookmaker} • Ошибка загрузки")
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

    def update_data(self, event_id: int, bet_type: str, bookmaker: str):
        """Обновление данных графика"""
        self.event_id = event_id
        self.bet_type = bet_type
        self.bookmaker = bookmaker

        self.load_data_async()

    def set_odds_service(self, odds_service):
        """Установить сервис коэффициентов"""
        self.odds_service = odds_service
        if self.event_id:
            self.load_data_async()
