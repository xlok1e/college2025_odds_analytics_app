"""Простой виджет загрузки с текстом"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from src.styles.theme import COLORS


class LoadingOverlay(QWidget):
    """Оверлей с текстом загрузки"""

    def __init__(self, parent=None, message="Загрузка..."):
        super().__init__(parent)
        self.message = message

        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Создаем label с текстом
        self.label = QLabel("ЗАГРУЗКА...", self)
        font = QFont()
        font.setPointSize(32)
        font.setWeight(QFont.Weight.ExtraBold)
        self.label.setFont(font)
        self.label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                background: rgba(0, 0, 0, 0.7);
                border: none;
                padding: 20px 40px;
                border-radius: 8px;
            }
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Устанавливаем стиль с полупрозрачным темным фоном
        self.setStyleSheet("""
            LoadingOverlay {
                background-color: rgba(0, 0, 0, 0.8);
            }
        """)

    def showEvent(self, event):
        """При показе обновляем позицию"""
        super().showEvent(event)
        self.update_position()

    def update_position(self):
        """Обновить позицию - занимаем весь родительский виджет"""
        parent = self.parent()
        if parent and hasattr(parent, 'width') and hasattr(parent, 'height'):
            self.setGeometry(0, 0, parent.width(), parent.height())

    def resizeEvent(self, event):
        """При изменении размера обновляем позицию"""
        super().resizeEvent(event)
        self.update_position()
