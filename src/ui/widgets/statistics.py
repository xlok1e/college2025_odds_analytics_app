from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from src.styles.theme import COLORS


class StatCard(QWidget):
    
    def __init__(self, label: str, value: str, subtitle: str = "", parent=None):
        super().__init__(parent)
        self.setup_ui(label, value, subtitle)
        
    def setup_ui(self, label: str, value: str, subtitle: str):
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['muted']}30;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 16px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(8)
        
        label_widget = QLabel(label)
        label_widget.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 11px; background: transparent; border: none; padding: 0;")
        layout.addWidget(label_widget)
        
        value_widget = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(20)
        value_font.setBold(True)
        value_widget.setFont(value_font)
        value_widget.setStyleSheet("background: transparent; border: none; padding: 0;")
        layout.addWidget(value_widget)
        
        if subtitle:
            subtitle_widget = QLabel(subtitle)
            subtitle_widget.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 11px; background: transparent; border: none; padding: 0;")
            layout.addWidget(subtitle_widget)


class Statistics(QWidget):
    
    def __init__(self, bet_type: str = "П1", parent=None):
        super().__init__(parent)
        self.bet_type = bet_type
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        
        title = QLabel("СТАТИСТИКА ПО КОЭФФИЦИЕНТУ")
        title_font = QFont()
        title_font.setPointSize(11)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        bet_label = QLabel(self.bet_type)
        bet_label.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 12px;")
        layout.addWidget(bet_label)
        
        grid = QGridLayout()
        grid.setSpacing(16)
        
        min_card = StatCard("Минимальное значение", "1.84", "15.03.2025 14:23")
        max_card = StatCard("Максимальное значение", "2.35", "15.03.2025 10:15")
        avg_card = StatCard("Среднее значение", "2.08")
        
        changes_card = StatCard("Количество изменений", "47")
        
        percent_card = QWidget()
        percent_card.setStyleSheet(f"""
            QWidget {{
                background-color: {COLORS['muted']}30;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                padding: 16px;
            }}
        """)
        percent_layout = QVBoxLayout(percent_card)
        percent_layout.setContentsMargins(16, 16, 16, 16)
        percent_layout.setSpacing(8)
        
        percent_label = QLabel("Процент изменения")
        percent_label.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 11px; background: transparent; border: none; padding: 0;")
        percent_layout.addWidget(percent_label)
        
        percent_value = QLabel("-8.5%")
        percent_font = QFont()
        percent_font.setPointSize(20)
        percent_font.setBold(True)
        percent_value.setFont(percent_font)
        percent_value.setStyleSheet(f"color: {COLORS['destructive']}; background: transparent; border: none; padding: 0;")
        percent_layout.addWidget(percent_value)
        
        percent_subtitle = QLabel("от первого до последнего значения")
        percent_subtitle.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 11px; background: transparent; border: none; padding: 0;")
        percent_layout.addWidget(percent_subtitle)
        
        grid.addWidget(min_card, 0, 0)
        grid.addWidget(max_card, 0, 1)
        grid.addWidget(avg_card, 0, 2)
        grid.addWidget(changes_card, 1, 0)
        grid.addWidget(percent_card, 1, 1, 1, 2)
        
        layout.addLayout(grid)
        
    def update_data(self, bet_type: str):
        self.bet_type = bet_type
        
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QLabel) and widget.text() in ["П1", "X", "П2", "Тотал больше 2.5", "Тотал меньше 2.5"]:
                widget.setText(bet_type)
                break
