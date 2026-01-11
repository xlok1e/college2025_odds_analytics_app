from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QFont,
)
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QStyledItemDelegate,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.import_service import EventImportService, ImportValidationError
from src.models.event import Event
from src.styles.theme import COLORS


class HoverDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.hover_row = -1

    def set_hover_row(self, row):
        self.hover_row = row

    def paint(self, painter, option, index):
        if index.row() == self.hover_row:
            painter.fillRect(option.rect, QColor(245, 245, 245, 250))

        super().paint(painter, option, index)


class ImportDialog(QDialog):

    def __init__(self, parent=None, db_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт спортивных событий")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.db_manager = db_manager
        self.import_service = EventImportService(db_manager) if db_manager else None
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
            if not self.import_service:
                QMessageBox.warning(self, "Ошибка", "Сервис импорта не инициализирован")
                return

            try:
                # Импорт событий
                imported_count, errors = self.import_service.import_from_file(file_path)

                if errors:
                    # Показываем ошибки, но также сообщаем об успешно импортированных
                    error_msg = f"Импортировано событий: {imported_count}\n\nОшибки:\n"
                    error_msg += "\n".join(errors[:10])  # Показываем первые 10 ошибок
                    if len(errors) > 10:
                        error_msg += f"\n... и еще {len(errors) - 10} ошибок"

                    QMessageBox.warning(self, "Частичный импорт", error_msg)
                else:
                    QMessageBox.information(
                        self,
                        "Успех",
                        f"Успешно импортировано событий: {imported_count}"
                    )

                if imported_count > 0:
                    self.accept()
                else:
                    self.reject()

            except ImportValidationError as e:
                self.reject()
                error_dialog = ErrorDialog(self.parent(), error_message=e.message)
                error_dialog.exec()
            except Exception as e:
                self.reject()
                error_dialog = ErrorDialog(
                    self.parent(),
                    error_message=f"Неожиданная ошибка: {str(e)}"
                )
                error_dialog.exec()


class ErrorDialog(QDialog):

    def __init__(self, parent=None, error_message=None):
        super().__init__(parent)
        self.setWindowTitle("Ошибка импорта")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        self.error_message = error_message or "Файл имеет неправильный формат данных"
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

        subtitle = QLabel(self.error_message)
        subtitle.setStyleSheet(f"color: {COLORS['muted_foreground']};")
        subtitle.setWordWrap(True)
        title_layout.addWidget(subtitle)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        desc = QLabel("Данные должны соответствовать следующей структуре:")
        layout.addWidget(desc)

        # Создаем табы для JSON и CSV примеров
        json_label = QLabel("<b>Формат JSON:</b>")
        layout.addWidget(json_label)

        json_example = QTextEdit()
        json_example.setReadOnly(True)
        json_example.setMaximumHeight(200)
        json_example.setPlainText(EventImportService.get_format_example_json())
        json_example.setStyleSheet(f"""
            QTextEdit {{
                background-color: #f5f5f5;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-family: monospace;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        layout.addWidget(json_example)

        csv_label = QLabel("<b>Формат CSV:</b>")
        csv_label.setStyleSheet("margin-top: 8px;")
        layout.addWidget(csv_label)

        csv_example = QTextEdit()
        csv_example.setReadOnly(True)
        csv_example.setMaximumHeight(100)
        csv_example.setPlainText(EventImportService.get_format_example_csv())
        csv_example.setStyleSheet(f"""
            QTextEdit {{
                background-color: #f5f5f5;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-family: monospace;
                font-size: 11px;
                padding: 8px;
            }}
        """)
        layout.addWidget(csv_example)

        fields_label = QLabel("Обязательные поля:")
        fields_font = QFont()
        fields_font.setBold(True)
        fields_label.setFont(fields_font)
        layout.addWidget(fields_label)

        fields = QLabel("""
• <b>sport</b> - вид спорта<br>
• <b>tournament</b> - название турнира<br>
• <b>country</b> - страна<br>
• <b>team1, team2</b> - названия команд<br>
• <b>date</b> - дата и время события (формат: DD.MM.YYYY HH:MM)<br>
• <b>bookmakers</b> - список букмекеров (опционально)<br>
• <b>coefficients</b> - объект с коэффициентами p1, x, p2 (опционально)
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
        self.table: Optional[QTableWidget] = None
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addStretch()

        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(24, 24, 24, 24)
        center_layout.setSpacing(8)

        title = QLabel("События отсутствуют")
        title.setStyleSheet("border: none; font-size: 20px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(title)

        desc = QLabel("Вы можете импортировать данные о спортивных событиях")
        desc.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 14px; border: none;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        center_layout.addWidget(desc)

        layout.addWidget(center_widget)
        layout.addStretch()

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

        self.hover_delegate = HoverDelegate(table)
        table.setItemDelegate(self.hover_delegate)

        table.setMouseTracking(True)

        def mouseMoveEvent(event):
            pos = event.position().toPoint()
            row = table.rowAt(pos.y())
            self.hover_delegate.set_hover_row(row)
            table.viewport().update()
            QTableWidget.mouseMoveEvent(table, event)

        def leaveEvent(event):
            self.hover_delegate.set_hover_row(-1)
            table.viewport().update()
            QTableWidget.leaveEvent(table, event)

        table.mouseMoveEvent = mouseMoveEvent
        table.leaveEvent = leaveEvent

        table.setStyleSheet(f"""
		        QTableWidget {{
		            outline: none;  /* Убирает обводку фокуса у таблицы */
		        }}
	          QTableWidget::item:first {{
	              border-left: 1px solid {COLORS['border']};
	          }}
	          QTableWidget::item:last {{
	              border-right: 1px solid {COLORS['border']};
	          }}
	      """)

        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setStyleSheet(f"background-color: {COLORS['card']}; border-right: 1px solid {COLORS['border']}; border-left: 1px solid {COLORS['border']}")

        for row, event in enumerate(self.events):
            item0 = QTableWidgetItem(event.sport)
            item0.setData(Qt.ItemDataRole.UserRole, event.id)
            table.setItem(row, 0, item0)
            table.setItem(row, 1, QTableWidgetItem(event.tournament))
            table.setItem(row, 2, QTableWidgetItem(f"{event.team1} - {event.team2}"))
            table.setItem(row, 3, QTableWidgetItem(event.date))
            table.setItem(row, 4, QTableWidgetItem(str(event.records_count)))

        table.itemSelectionChanged.connect(self.on_selection_changed)

        return table

    def on_selection_changed(self):
        if not self.table:
            return
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            item = self.table.item(row, 0)
            if item:
                event_id = item.data(Qt.ItemDataRole.UserRole)
                self.selected_event_id = event_id
                self.event_selected.emit(event_id)

    def show_import_dialog(self):
        # Получаем db_manager из главного окна приложения
        main_window = self.window()
        db_manager = getattr(main_window, 'db_manager', None) if main_window else None

        if not db_manager:
            QMessageBox.warning(
                self,
                "Ошибка",
                "Не удалось получить подключение к базе данных"
            )
            return

        dialog = ImportDialog(self, db_manager=db_manager)
        result = dialog.exec()

        # Если импорт успешен, обновляем список событий
        if result == QDialog.DialogCode.Accepted:
            if hasattr(main_window, 'refresh_events') and callable(getattr(main_window, 'refresh_events')):
                main_window.refresh_events()  # type: ignore

    def select_event(self, event_id: int):
        if not self.table:
            return
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == event_id:
                self.table.selectRow(row)
                break

    def set_events(self, events: List[Event]):
        self.events = events
        self.selected_event_id = None

        layout = self.layout()
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            # Пересоздаем содержимое card
            card = QWidget()
            card.setObjectName("eventsCard")
            card.setStyleSheet(f"""
                QWidget#eventsCard {{
                    background-color: {COLORS['card']};
                    border: 1px solid {COLORS['border']};
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
