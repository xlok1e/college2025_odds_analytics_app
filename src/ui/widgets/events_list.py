from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QLabel, QDialog, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from typing import List, Optional

from src.models.event import Event
from src.styles.theme import COLORS


class ImportDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт спортивных событий")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Заголовок
        title = QLabel("Импорт спортивных событий")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Описание
        desc = QLabel("Выберите файл данных:")
        desc_font = QFont()
        desc_font.setPointSize(12)
        desc.setFont(desc_font)
        layout.addWidget(desc)
        
        self.select_btn = QPushButton("Выбрать файл")
        self.select_btn.clicked.connect(self.select_file)
        layout.addWidget(self.select_btn)
        
        info = QLabel("Поддерживаемые форматы: JSON, CSV")
        info.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 12px;")
        layout.addWidget(info)
        
        layout.addStretch()
        
        cancel_btn = QPushButton("Отмена")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "Data Files (*.json *.csv);;All Files (*)"
        )
        
        if file_path:
            import random
            if random.random() > 0.5:
                QMessageBox.information(self, "Успех", f"Выбран файл: {file_path}")
                self.accept()
            else:
                self.reject()
                error_dialog = ErrorDialog(self.parent())
                error_dialog.exec()


class ErrorDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ошибка импорта")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)
        
        header_layout = QHBoxLayout()
        
        error_label = QLabel("⚠")
        error_label.setStyleSheet(f"""
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
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(error_label)
        
        title_layout = QVBoxLayout()
        title = QLabel("Ошибка импорта данных")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Файл имеет неправильный формат данных")
        subtitle.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        desc = QLabel("Данные должны соответствовать следующей структуре:")
        layout.addWidget(desc)
        
        example = QLabel('''<pre style="background-color: #f5f5f5; padding: 12px; border-radius: 6px; font-family: monospace; font-size: 11px;">
{
  "events": [
    {
      "id": 1,
      "sport": "Футбол",
      "tournament": "Российская Премьер-Лига",
      "country": "Россия",
      "team1": "Зенит",
      "team2": "Спартак",
      "date": "15.03.2025 19:00",
      "recordsCount": 142,
      "bookmakers": ["1xBet", "Fonbet"],
      "coefficients": {
        "p1": 1.85,
        "x": 3.45,
        "p2": 4.20
      }
    }
  ]
}
</pre>''')
        example.setTextFormat(Qt.TextFormat.RichText)
        example.setWordWrap(True)
        layout.addWidget(example)
        
        fields_label = QLabel("Обязательные поля:")
        fields_font = QFont()
        fields_font.setBold(True)
        fields_label.setFont(fields_font)
        layout.addWidget(fields_label)
        
        fields = QLabel("""
• <b>sport</b> - вид спорта<br>
• <b>tournament</b> - название турнира<br>
• <b>team1, team2</b> - названия команд<br>
• <b>date</b> - дата и время события<br>
• <b>coefficients</b> - объект с коэффициентами
        """)
        fields.setTextFormat(Qt.TextFormat.RichText)
        fields.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        layout.addWidget(fields)
        
        layout.addStretch()
        
        close_btn = QPushButton("Закрыть")
        close_btn.setProperty("class", "secondary")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)


class EventsList(QWidget):
    
    event_selected = Signal(int)  
    
    def __init__(self, events: List[Event], parent=None):
        super().__init__(parent)
        self.events = events
        self.selected_event_id: Optional[int] = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        card = QWidget()
        card.setObjectName("eventsCard")
        card.setStyleSheet(f"""
            QWidget#eventsCard {{
                background-color: {COLORS['card']};
                border: 1px solid {COLORS['border']};
                border-bottom: none;
                border-radius: 8px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)
        
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 16)
        
        title = QLabel("Спортивные события")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setStyleSheet("border: none; font-size: 18px")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        import_btn = QPushButton("Импорт данных")
        import_btn.clicked.connect(self.show_import_dialog)
        header_layout.addWidget(import_btn)
        
        card_layout.addWidget(header)
        
        if len(self.events) == 0:
            empty_widget = self.create_empty_state()
            card_layout.addWidget(empty_widget)
        else:
            self.table = self.create_table()
            card_layout.addWidget(self.table)
        
        layout.addWidget(card)
        
    def create_empty_state(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 64, 24, 64)
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
        
        title = QLabel("События отсутствуют")
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel("Вы можете импортировать данные о спортивных событиях")
        desc.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc)
        
        import_btn = QPushButton("Импортировать данные")
        import_btn.clicked.connect(self.show_import_dialog)
        import_btn.setMaximumWidth(200)
        layout.addWidget(import_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return widget
        
    def create_table(self) -> QTableWidget:
        table = QTableWidget()
        table.setColumnCount(5)
        table.setRowCount(len(self.events))
        table.setHorizontalHeaderLabels([
            "Вид спорта", "Турнир", "Команды", "Дата", "Записей"
        ])
        
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setStyleSheet(f"background-color: {COLORS['card']};")
        
        for row, event in enumerate(self.events):
            table.setItem(row, 0, QTableWidgetItem(event.sport))
            table.setItem(row, 1, QTableWidgetItem(event.tournament))
            table.setItem(row, 2, QTableWidgetItem(f"{event.team1} - {event.team2}"))
            table.setItem(row, 3, QTableWidgetItem(event.date))
            table.setItem(row, 4, QTableWidgetItem(str(event.records_count)))
            
            table.item(row, 0).setData(Qt.ItemDataRole.UserRole, event.id)
        
        table.itemSelectionChanged.connect(self.on_selection_changed)
        
        return table
        
    def on_selection_changed(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            event_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            self.selected_event_id = event_id
            self.event_selected.emit(event_id)
            
    def show_import_dialog(self):
        dialog = ImportDialog(self)
        dialog.exec()
        
    def select_event(self, event_id: int):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).data(Qt.ItemDataRole.UserRole) == event_id:
                self.table.selectRow(row)
                break
