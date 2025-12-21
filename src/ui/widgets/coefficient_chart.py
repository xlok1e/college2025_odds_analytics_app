from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.styles.theme import COLORS


class ChartCanvas(QWidget):
    """Виджет для рисования графика"""
    def __init__(self, data_points, time_labels, value_labels, parent=None):
        super().__init__(parent)
        self.data_points = data_points
        self.time_labels = time_labels
        self.value_labels = value_labels
        self.setMinimumHeight(250)

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

            for x, y, value in scaled_points:
                if value != 1.84:
                    painter.setBrush(QColor(COLORS['chart_1']))
                    painter.setPen(QPen(QColor(COLORS['card']), 2))
                    painter.drawEllipse(QPointF(x, y), 5, 5)
                else:
                    painter.setBrush(QColor(COLORS['destructive']))
                    painter.setPen(QPen(QColor(COLORS['card']), 2))
                    painter.drawEllipse(QPointF(x, y), 6, 6)


class CoefficientChart(QWidget):
    def __init__(self, bet_type: str = "П1", bookmaker: str = "1xBet", parent=None):
        super().__init__(parent)
        self.bet_type = bet_type
        self.bookmaker = bookmaker

        self.data_points = [
            (40, 60, 2.25),
            (120, 55, 2.30),
            (200, 70, 2.15),
            (280, 120, 1.84),
            (360, 110, 1.90),
            (440, 90, 2.05),
            (520, 100, 1.95),
            (580, 85, 2.10)
        ]

        self.time_labels = ["10:00", "12:00", "14:00", "16:00"]
        self.value_labels = ["2.5", "2.3", "2.1", "1.9", "1.7"]

        from PySide6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.setMinimumHeight(350)
        self.setup_ui()

    def setup_ui(self):
        # Основной layout без отступов
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Контейнер с рамкой
        container = QWidget()
        container.setStyleSheet(f"""
            background-color: {COLORS['card']};
            border: 1px solid {COLORS['border']};
            border-radius: 8px;
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Заголовок
        title = QLabel("ГРАФИК ИЗМЕНЕНИЯ КОЭФФИЦИЕНТА")
        title.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 14px; font-weight: 600;")
        layout.addWidget(title)

        # Параметры
        params = QLabel(f"{self.bet_type} • {self.bookmaker}")
        params.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 12px;")
        layout.addWidget(params)

        # Добавляем canvas для рисования графика
        self.canvas = ChartCanvas(self.data_points, self.time_labels, self.value_labels)
        layout.addWidget(self.canvas)

        main_layout.addWidget(container)

    def update_data(self, bet_type: str, bookmaker: str):
        self.bet_type = bet_type
        self.bookmaker = bookmaker

        # Находим контейнер и обновляем label внутри него
        main_widget = self.layout().itemAt(0).widget()
        if main_widget:
            for i in range(main_widget.layout().count()):
                widget = main_widget.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and "•" in widget.text():
                    widget.setText(f"{bet_type} • {bookmaker}")
                    break

        self.canvas.update()
