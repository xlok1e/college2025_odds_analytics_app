from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from src.models.event import Event as EventModel
from src.styles.theme import COLORS
from src.ui.widgets.coefficient_chart import CoefficientChart
from src.ui.widgets.statistics import Statistics


class DeleteConfirmDialog(QDialog):

    def __init__(self, event: EventModel, parent=None):
        super().__init__(parent)
        self.event = event
        self.setWindowTitle("Подтверждение удаления")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        header_layout = QHBoxLayout()

        icon = QLabel("🗑")
        icon.setStyleSheet(f"""
            background-color: {COLORS['destructive']}20;
            color: {COLORS['destructive']};
            font-size: 24px;
            padding: 8px;
            border-radius: 20px;
            min-width: 40px;
            max-width: 40px;
            min-height: 40px;
            max-height: 40px;
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(icon)

        title_layout = QVBoxLayout()
        title = QLabel("Подтверждение удаления")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)

        subtitle = QLabel("Это действие нельзя отменить")
        subtitle.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        info_widget = QWidget()
        info_widget.setStyleSheet(f"""
            QWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 16px;
            }}
        """)
        info_layout = QVBoxLayout(info_widget)

        question = QLabel("Вы действительно хотите удалить событие?")
        question.setStyleSheet(f"color: {COLORS['muted_foreground']}; background: transparent; border: none; padding: 0;")
        info_layout.addWidget(question)

        event_name = QLabel(f"{self.event.team1} - {self.event.team2}")
        event_font = QFont()
        event_font.setPointSize(13)
        event_font.setBold(True)
        event_name.setFont(event_font)
        event_name.setStyleSheet("background: transparent; border: none; padding: 0;")
        info_layout.addWidget(event_name)

        event_date = QLabel(self.event.date)
        event_date.setStyleSheet(f"color: {COLORS['muted_foreground']}; background: transparent; border: none; padding: 0;")
        info_layout.addWidget(event_date)

        layout.addWidget(info_widget)

        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        delete_btn = QPushButton("Удалить")
        delete_btn.setProperty("class", "destructive")
        delete_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(delete_btn)

        layout.addLayout(buttons_layout)


class EventDetail(QWidget):
    event_deleted = Signal()

    def __init__(self, event: Optional[EventModel] = None, parent=None):
        super().__init__(parent)
        self.current_event = event
        self.selected_bookmaker = "1xBet"
        self.selected_bet_type = "П1"
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        if self.current_event is None:
            empty_widget = self.create_empty_state()
            main_layout.addWidget(empty_widget)
        else:
            detail_widget = self.create_detail_widget()
            main_layout.addWidget(detail_widget)

        self.setLayout(main_layout)

    def create_empty_state(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(48, 48, 48, 48)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Выберите событие")
        title.setStyleSheet("border: none; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        desc = QLabel("Выберите спортивное событие из списка слева для просмотра детальной информации, графиков и статистики коэффициентов")
        desc.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 14px; border: none;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)

        return widget

    def create_detail_widget(self) -> QWidget:
        # Обертка с обводкой и закругленными углами
        wrapper = QWidget()
        wrapper.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(0, 0, 0, 0)
        wrapper_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        container.setStyleSheet("QWidget { background: transparent; }")
        scroll.setWidget(container)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        card = QWidget()
        card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        card.setMaximumWidth(9999)
        card.setStyleSheet("QWidget { background: transparent; border: none; }")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet(f"border-bottom: 1px solid {COLORS['border']}; border-radius: 0px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        title = QLabel("Детальная информация")
        title.setStyleSheet('font-size: 16px; border: none; font-weight: 600;')
        header_layout.addWidget(title)

        card_layout.addWidget(header)

        content = QWidget()
        content.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        content.setStyleSheet("border: none;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(24)

        info_section = self.create_info_section()
        content_layout.addWidget(info_section)

        coef_section = self.create_coefficients_section()
        content_layout.addWidget(coef_section)

        params_section = self.create_params_section()
        content_layout.addWidget(params_section)

        self.chart = CoefficientChart(self.selected_bet_type, self.selected_bookmaker)
        self.chart.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.chart.setMinimumWidth(0)
        content_layout.addWidget(self.chart)

        self.statistics = Statistics(self.selected_bet_type)
        self.statistics.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.statistics.setMinimumWidth(0)
        content_layout.addWidget(self.statistics)

        warning = self.create_warning_section()
        content_layout.addWidget(warning)

        delete_section = QWidget()
        delete_section.setStyleSheet(f"border-top: 1px solid {COLORS['border']}; padding-top: 16px; border-radius: 0px;")
        delete_layout = QVBoxLayout(delete_section)
        delete_layout.setContentsMargins(0, 16, 0, 0)

        delete_btn = QPushButton("Удалить событие")
        delete_btn.setProperty("class", "destructive")
        delete_btn.clicked.connect(self.show_delete_dialog)
        delete_layout.addWidget(delete_btn)

        card_layout.addWidget(content)
        card_layout.addWidget(delete_section)

        layout.addWidget(card)
        wrapper_layout.addWidget(scroll)

        return wrapper

    def create_info_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Матч (крупный текст сверху)
        match_value = QLabel(f"{self.current_event.team1} - {self.current_event.team2}")
        match_value.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 20px; font-weight: bold;")
        layout.addWidget(match_value)

        title = QLabel("ОСНОВНАЯ ИНФОРМАЦИЯ")
        title.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 14px; font-weight: 600;")
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setHorizontalSpacing(12)
        grid.setVerticalSpacing(12)

        fields = [
            ("Вид спорта", self.current_event.sport, 0, 0),
            ("Турнир", self.current_event.tournament, 0, 1),
            ("Страна", self.current_event.country, 1, 0),
            ("Дата и время", self.current_event.date, 1, 1),
            ("Записей коэффициентов", str(self.current_event.records_count), 2, 0),
            ("Букмекеры", ", ".join(self.current_event.bookmakers), 2, 1),
        ]

        for label_text, value_text, row, col in fields:
            field_layout = QVBoxLayout()
            field_layout.setSpacing(4)

            label = QLabel(label_text)
            label.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 12px; background: transparent; border: none; padding: 0;")
            field_layout.addWidget(label)

            value = QLabel(value_text)
            value_font = QFont()
            value_font.setBold(True)
            value.setFont(value_font)
            value.setStyleSheet("background: transparent; border: none; padding: 0;")
            field_layout.addWidget(value)

            grid.addLayout(field_layout, row, col)

        layout.addLayout(grid)

        return section

    def create_coefficients_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 24)
        layout.setSpacing(12)

        header_layout = QHBoxLayout()

        title = QLabel("КОЭФФИЦИЕНТЫ И РАСЧЕТЫ")
        title.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 14px; font-weight: 600;")
        header_layout.addWidget(title)

        header_layout.addStretch()

        coef = self.current_event.coefficients
        if coef.x > 0:
            margin = ((1 / coef.p1 + 1 / coef.x + 1 / coef.p2 - 1) * 100)
        else:
            margin = ((1 / coef.p1 + 1 / coef.p2 - 1) * 100)

        margin_label = QLabel(f"Маржа: <span style='color: {COLORS['accent']}; font-weight: bold;'>{margin:.2f}%</span>")
        margin_label.setTextFormat(Qt.TextFormat.RichText)
        margin_label.setStyleSheet("background: transparent; border: none; padding: 0;")
        header_layout.addWidget(margin_label)

        layout.addLayout(header_layout)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setRowCount(3)
        table.setHorizontalHeaderLabels([
            "Исход", "Коэф.", "Вероятность", "Реальная вер.", "Реальный коэф."
        ])

        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)

        # Убираем скроллбары
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Устанавливаем фиксированную высоту таблицы
        header_height = 40
        row_height = 50
        total_height = header_height + row_height * 3
        table.setFixedHeight(total_height)
        table.setMinimumHeight(total_height)
        table.setMaximumHeight(total_height)

        table.setStyleSheet("""
            QTableWidget {
                background: transparent;
                border: none;
            }
            QTableWidget::item {
                padding: 0px;
                margin: 0px;
                font-size: 16px;
            }
        """)
        table.setContentsMargins(0, 0, 0, 0)

        header = table.horizontalHeader()
        header.setMinimumHeight(header_height)
        header.setMaximumHeight(header_height)
        header.setStyleSheet(f"""
            QHeaderView::section {{
                background-color: transparent;
                color: {COLORS['muted_foreground']};
                padding: 8px;
                border: none;
                font-size: 10px;
                font-weight: 600;
                height: {header_height}px;
            }}
        """)
        # Устанавливаем режим изменения размера колонок
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Исход
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Коэф.
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # Вероятность
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # Реальная вер.
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Реальный коэф.

        # Устанавливаем высоту строк
        v_header = table.verticalHeader()
        v_header.setDefaultSectionSize(row_height)
        v_header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        coef = self.current_event.coefficients
        prob1 = (1 / coef.p1) * 100
        probX = (1 / coef.x) * 100 if coef.x > 0 else 0
        prob2 = (1 / coef.p2) * 100

        if coef.x > 0:
            sum_prob = 1 / coef.p1 + 1 / coef.x + 1 / coef.p2
        else:
            sum_prob = 1 / coef.p1 + 1 / coef.p2

        real_prob1 = (1 / coef.p1 / sum_prob) * 100
        real_probX = (1 / coef.x / sum_prob) * 100 if coef.x > 0 else 0
        real_prob2 = (1 / coef.p2 / sum_prob) * 100

        real_coef1 = 1 / (1 / coef.p1 / sum_prob)
        real_coefX = 1 / (1 / coef.x / sum_prob) if coef.x > 0 else 0
        real_coef2 = 1 / (1 / coef.p2 / sum_prob)

        rows_data = [
            ("П1", coef.p1, prob1, real_prob1, real_coef1),
            ("X", coef.x, probX, real_probX, real_coefX),
            ("П2", coef.p2, prob2, real_prob2, real_coef2),
        ]

        for row, (outcome, c, p, rp, rc) in enumerate(rows_data):
            outcome_item = QTableWidgetItem(outcome)
            outcome_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 0, outcome_item)

            coef_item = QTableWidgetItem(f"{c:.2f}")
            coef_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 1, coef_item)

            prob_item = QTableWidgetItem(f"{p:.2f}%")
            prob_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 2, prob_item)

            real_prob_item = QTableWidgetItem(f"{rp:.2f}%")
            real_prob_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 3, real_prob_item)

            real_coef_item = QTableWidgetItem(f"{rc:.2f}")
            real_coef_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            table.setItem(row, 4, real_coef_item)

        layout.addWidget(table)

        return section

    def create_params_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)

        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Заголовок
        title = QLabel("ПАРАМЕТРЫ ДЛЯ АНАЛИЗА")
        title.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 14px; font-weight: 600;")
        layout.addWidget(title)

        selectors_layout = QGridLayout()
        selectors_layout.setSpacing(6)

        bookmaker_label = QLabel("Букмекер")
        bookmaker_label.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 14px; font-weight: 500;")
        bookmaker_label_font = QFont()
        bookmaker_label_font.setBold(True)
        bookmaker_label.setFont(bookmaker_label_font)
        selectors_layout.addWidget(bookmaker_label, 0, 0)

        self.bookmaker_combo = QComboBox()
        self.bookmaker_combo.addItem("Все букмекеры")
        for bm in self.current_event.bookmakers:
            self.bookmaker_combo.addItem(bm)
        self.bookmaker_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0px 12px;
                min-height: 30px;
                color: {COLORS['foreground']};
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {COLORS['muted_foreground']};
                width: 0;
                height: 0;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 0px;
                selection-background-color: {COLORS['muted']};
                selection-color: {COLORS['foreground']};
                padding: 6px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['muted']};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['muted']};
            }}
        """)
        self.bookmaker_combo.currentTextChanged.connect(self.on_params_changed)
        selectors_layout.addWidget(self.bookmaker_combo, 1, 0)

        bet_type_label = QLabel("Тип ставки")
        bet_type_label.setStyleSheet("background: transparent; border: none; padding: 0; font-size: 14px; font-weight: 500;")
        bet_type_label_font = QFont()
        bet_type_label_font.setBold(True)
        bet_type_label.setFont(bet_type_label_font)
        selectors_layout.addWidget(bet_type_label, 0, 1)

        self.bet_type_combo = QComboBox()
        self.bet_type_combo.addItems(["П1", "X", "П2", "Тотал больше 2.5", "Тотал меньше 2.5"])
        self.bet_type_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {COLORS['secondary']};
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 0px 12px;
                min-height: 30px;
                color: {COLORS['foreground']};
            }}
            QComboBox:hover {{
                border-color: {COLORS['primary']};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid {COLORS['muted_foreground']};
                width: 0;
                height: 0;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 0px;
                selection-background-color: {COLORS['muted']};
                selection-color: {COLORS['foreground']};
                padding: 6px;
                outline: none;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 8px 12px;
                background-color: transparent;
                border: none;
                border-radius: 0px;
            }}
            QComboBox QAbstractItemView::item:selected {{
                background-color: {COLORS['muted']};
            }}
            QComboBox QAbstractItemView::item:hover {{
                background-color: {COLORS['muted']};
            }}
        """)
        self.bet_type_combo.currentTextChanged.connect(self.on_params_changed)
        selectors_layout.addWidget(self.bet_type_combo, 1, 1)

        layout.addLayout(selectors_layout)

        return section

    def create_warning_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['warning_bg']};
                border: 1px solid {COLORS['warning_border']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)

        layout = QHBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        icon = QLabel("⚠")
        icon.setStyleSheet(f"""
            background-color: {COLORS['warning_border']};
            color: {COLORS['warning_text']};
            font-size: 20px;
            padding: 8px;
            border-radius: 16px;
            min-width: 32px;
            max-width: 32px;
            min-height: 32px;
            max-height: 32px;
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        text_layout = QVBoxLayout()

        title = QLabel("Обнаружены резкие изменения")
        title_font = QFont()
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet(f"color: {COLORS['warning_text']}; background: transparent; border: none; padding: 0;")
        text_layout.addWidget(title)

        changes = QLabel(
            "• 15.03.2025 14:23 - падение на 12.5% за 45 минут (2.10 → 1.84)\n"
            "• 15.03.2025 16:45 - рост на 15.2% за 30 минут (1.84 → 2.12)"
        )
        changes.setStyleSheet(f"color: {COLORS['warning_text']}; background: transparent; border: none; padding: 0; font-size: 12px;")
        text_layout.addWidget(changes)

        layout.addLayout(text_layout)

        return section

    def on_params_changed(self):
        self.selected_bookmaker = self.bookmaker_combo.currentText()
        self.selected_bet_type = self.bet_type_combo.currentText()

        self.chart.update_data(self.selected_bet_type, self.selected_bookmaker)
        self.statistics.update_data(self.selected_bet_type)

    def show_delete_dialog(self):
        dialog = DeleteConfirmDialog(self.current_event, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.event_deleted.emit()

    def set_event(self, event: Optional[EventModel]):
        self.current_event = event

        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            if self.current_event is None:
                empty_widget = self.create_empty_state()
                layout.addWidget(empty_widget)
            else:
                detail_widget = self.create_detail_widget()
                layout.addWidget(detail_widget)
