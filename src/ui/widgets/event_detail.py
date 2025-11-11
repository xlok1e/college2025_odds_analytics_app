from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import Optional

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
                background-color: {COLORS['muted']}30;
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
        
        icon = QLabel("📊")
        icon.setStyleSheet(f"""
            background-color: {COLORS['muted']};
            font-size: 32px;
            padding: 16px;
            border-radius: 32px;
            min-width: 64px;
            max-width: 64px;
            min-height: 64px;
            max-height: 64px;
        """)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon, alignment=Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Выберите событие")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel("Выберите спортивное событие из списка слева для просмотра\nдетальной информации, графиков и статистики коэффициентов")
        desc.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        return widget
        
    def create_detail_widget(self) -> QWidget:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        container = QWidget()
        scroll.setWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        card = QWidget()
        card.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        header = QWidget()
        header.setStyleSheet(f"border-bottom: 1px solid {COLORS['border']}; border-radius: 0px;")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)
        
        title = QLabel("Детальная информация")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)
        
        card_layout.addWidget(header)
        
        content = QWidget()
        content.setStyleSheet("border: none;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(24)
        
        info_section = self.create_info_section()
        content_layout.addWidget(info_section)
        
        coef_section = self.create_coefficients_section()
        content_layout.addWidget(coef_section)
        
        params_section = self.create_params_section()
        content_layout.addWidget(params_section)
        
        self.chart = CoefficientChart(self.selected_bet_type, self.selected_bookmaker)
        self.chart.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        content_layout.addWidget(self.chart)
        
        self.statistics = Statistics(self.selected_bet_type)
        self.statistics.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
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
        
        content_layout.addWidget(delete_section)
        
        card_layout.addWidget(content)
        layout.addWidget(card)
        
        return scroll
        
    def create_info_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['muted']}30;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        title = QLabel("ОСНОВНАЯ ИНФОРМАЦИЯ")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("background: transparent; border: none; padding: 0;")
        layout.addWidget(title)
        
        grid = QGridLayout()
        grid.setSpacing(16)
        
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
        
        match_layout = QVBoxLayout()
        match_label = QLabel("Матч")
        match_label.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 12px; background: transparent; border: none; padding: 0;")
        match_layout.addWidget(match_label)
        
        match_value = QLabel(f"{self.current_event.team1} - {self.current_event.team2}")
        match_font = QFont()
        match_font.setPointSize(13)
        match_font.setBold(True)
        match_value.setFont(match_font)
        match_value.setStyleSheet("background: transparent; border: none; padding: 0;")
        match_layout.addWidget(match_value)
        
        grid.addLayout(match_layout, 3, 0, 1, 2)
        
        layout.addLayout(grid)
        
        return section
        
    def create_coefficients_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(section)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        header_layout = QHBoxLayout()
        
        title = QLabel("КОЭФФИЦИЕНТЫ И РАСЧЕТЫ")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("background: transparent; border: none; padding: 0;")
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
        table.setStyleSheet("background: transparent; border: none;")
        
        header = table.horizontalHeader()
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
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
            table.setItem(row, 0, QTableWidgetItem(outcome))
            table.setItem(row, 1, QTableWidgetItem(f"{c:.2f}"))
            table.setItem(row, 2, QTableWidgetItem(f"{p:.2f}%"))
            table.setItem(row, 3, QTableWidgetItem(f"{rp:.2f}%"))
            table.setItem(row, 4, QTableWidgetItem(f"{rc:.2f}"))
        
        layout.addWidget(table)
        
        return section
        
    def create_params_section(self) -> QWidget:
        section = QWidget()
        section.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['muted']}30;
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
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("background: transparent; border: none; padding: 0;")
        layout.addWidget(title)
        
        selectors_layout = QGridLayout()
        selectors_layout.setSpacing(16)
        
        bookmaker_label = QLabel("Букмекер")
        bookmaker_label.setStyleSheet("background: transparent; border: none; padding: 0;")
        bookmaker_label_font = QFont()
        bookmaker_label_font.setBold(True)
        bookmaker_label.setFont(bookmaker_label_font)
        selectors_layout.addWidget(bookmaker_label, 0, 0)
        
        self.bookmaker_combo = QComboBox()
        self.bookmaker_combo.addItem("Все букмекеры")
        for bm in self.current_event.bookmakers:
            self.bookmaker_combo.addItem(bm)
        self.bookmaker_combo.currentTextChanged.connect(self.on_params_changed)
        selectors_layout.addWidget(self.bookmaker_combo, 1, 0)
        
        bet_type_label = QLabel("Тип ставки")
        bet_type_label.setStyleSheet("background: transparent; border: none; padding: 0;")
        bet_type_label_font = QFont()
        bet_type_label_font.setBold(True)
        bet_type_label.setFont(bet_type_label_font)
        selectors_layout.addWidget(bet_type_label, 0, 1)
        
        self.bet_type_combo = QComboBox()
        self.bet_type_combo.addItems(["П1", "X", "П2", "Тотал больше 2.5", "Тотал меньше 2.5"])
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
