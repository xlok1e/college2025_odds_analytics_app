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
from src.ui.workers.import_worker import ImportWorker


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

    def __init__(self, parent=None, db_manager=None, main_window=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт спортивных событий")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.db_manager = db_manager
        self.main_window = main_window  # Ссылка на главное окно
        self.import_service = EventImportService(db_manager) if db_manager else None
        self.import_worker = None
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

        # Прогресс бар (скрыт по умолчанию)
        self.progress_label = QLabel("")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)

        from PySide6.QtWidgets import QProgressBar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)

        layout.addStretch()

        cancel_btn = QPushButton("Отмена")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.cancel_import)
        layout.addWidget(cancel_btn)
        self.cancel_btn = cancel_btn

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

            # Быстрая предварительная валидация файла ПЕРЕД запуском worker
            validation_error = self.quick_validate_file(file_path)
            if validation_error:
                print(f"[ImportDialog] Ошибка валидации файла: {validation_error}")
                error_dialog = ErrorDialog(
                    self.parent(),
                    error_message=validation_error,
                    show_format_example=True
                )
                error_dialog.exec()
                return

            # Запускаем импорт в отдельном потоке
            self.start_import(file_path)

    def quick_validate_file(self, file_path: str) -> str:
        """Быстрая проверка файла перед запуском импорта. Возвращает текст ошибки или None."""
        import csv
        import json

        try:
            # Проверяем расширение файла
            if not (file_path.lower().endswith('.json') or file_path.lower().endswith('.csv')):
                return "Неподдерживаемый формат файла. Используйте JSON или CSV."

            # Для JSON - проверяем базовую структуру
            if file_path.lower().endswith('.json'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except json.JSONDecodeError as e:
                    return f"Ошибка парсинга JSON файла: {str(e)}"
                except UnicodeDecodeError:
                    return "Ошибка чтения файла: неверная кодировка. Используйте UTF-8."
                except Exception as e:
                    return f"Ошибка чтения файла: {str(e)}"

                # Проверяем структуру
                if not isinstance(data, dict):
                    return "JSON файл должен содержать объект (начинаться с '{')"

                if 'events' not in data:
                    return "JSON файл должен содержать поле 'events' с массивом событий"

                if not isinstance(data['events'], list):
                    return "Поле 'events' должно быть массивом (начинаться с '[')"

                if len(data['events']) == 0:
                    return "Список событий пустой. Добавьте хотя бы одно событие."

            # Для CSV - проверяем наличие заголовков
            elif file_path.lower().endswith('.csv'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        headers = reader.fieldnames

                        if not headers:
                            return "CSV файл не содержит заголовков"

                        required = ['sport', 'tournament', 'country', 'team1', 'team2', 'date']
                        missing = [field for field in required if field not in headers]

                        if missing:
                            return f"В CSV файле отсутствуют обязательные колонки: {', '.join(missing)}"

                except UnicodeDecodeError:
                    return "Ошибка чтения файла: неверная кодировка. Используйте UTF-8."
                except Exception as e:
                    return f"Ошибка чтения CSV файла: {str(e)}"

            # Файл прошел базовую проверку
            return None

        except Exception as e:
            return f"Неожиданная ошибка при проверке файла: {str(e)}"

    def start_import(self, file_path: str):
        """Запуск импорта в фоновом потоке"""
        print(f"[ImportDialog] Начало импорта файла: {file_path}")

        # Останавливаем предыдущий worker если он еще работает
        if self.import_worker and self.import_worker.isRunning():
            print("[ImportDialog] Предыдущий импорт еще выполняется, останавливаем...")
            self.import_worker.stop()
            self.import_worker = None

        # Показываем прогресс бар
        self.progress_label.setText("Импорт данных...")
        self.progress_label.setVisible(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.select_btn.setEnabled(False)
        self.cancel_btn.setText("Отмена")

        # Принудительно обновляем UI
        from PySide6.QtWidgets import QApplication
        QApplication.processEvents()

        # Создаем и запускаем worker
        self.import_worker = ImportWorker(self.import_service, file_path)
        self.import_worker.finished.connect(self.on_import_finished)
        self.import_worker.error.connect(self.on_import_error)
        self.import_worker.start()

        print("[ImportDialog] Worker запущен")

    def on_import_finished(self, imported_count: int, errors: list):
        """Обработка успешного завершения импорта"""
        print(f"[ImportDialog] Импорт завершен: {imported_count} событий, {len(errors)} ошибок")

        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.select_btn.setEnabled(True)
        self.cancel_btn.setText("Закрыть")

        # Очищаем worker
        if self.import_worker:
            self.import_worker.deleteLater()
            self.import_worker = None

        # Показываем диалоги с результатами
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

        # Закрываем диалог
        if imported_count > 0:
            self.accept()
        else:
            self.reject()

        # ПОСЛЕ закрытия диалога запускаем обновление списка событий
        if imported_count > 0:
            print("[ImportDialog] Запуск обновления списка событий после закрытия диалога...")
            if self.main_window and hasattr(self.main_window, 'refresh_events'):
                from PySide6.QtCore import QTimer
                # Небольшая задержка чтобы диалог успел закрыться
                QTimer.singleShot(100, lambda: self.main_window.refresh_events())
                print("[ImportDialog] Обновление запланировано")
            else:
                print("[ImportDialog] ВНИМАНИЕ: main_window не передан, список не будет обновлен!")

    def on_import_error(self, error_message: str):
        """Обработка ошибки импорта"""
        print(f"[ImportDialog] Ошибка импорта: {error_message}")

        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.select_btn.setEnabled(True)
        self.cancel_btn.setText("Закрыть")

        # Очищаем worker
        if self.import_worker:
            self.import_worker.deleteLater()
            self.import_worker = None

        # Определяем тип ошибки для показа соответствующего диалога
        show_example = self._should_show_example(error_message)

        # Показываем диалог с ошибкой
        error_dialog = ErrorDialog(
            self.parent(),
            error_message=error_message,
            show_format_example=show_example
        )
        error_dialog.exec()

        self.reject()

    def _should_show_example(self, error_message: str) -> bool:
        """Определяет, нужно ли показывать пример формата"""
        # Показываем пример только для ошибок формата и валидации
        validation_keywords = [
            'обязательные поля',
            'формат даты',
            'формат файла',
            'должен содержать',
            'должно быть',
            'парсинга JSON',
            'коэффициента',
            'неверное значение',
            'отсутствуют'
        ]

        error_lower = error_message.lower()
        return any(keyword.lower() in error_lower for keyword in validation_keywords)

    def cancel_import(self):
        """Отмена импорта"""
        print("[ImportDialog] Отмена импорта")

        if self.import_worker and self.import_worker.isRunning():
            self.progress_label.setText("Отмена импорта...")
            print("[ImportDialog] Останавливаем worker...")
            self.import_worker.stop()
            self.import_worker.deleteLater()
            self.import_worker = None
            print("[ImportDialog] Worker остановлен")

        self.reject()


class ErrorDialog(QDialog):

    def __init__(self, parent=None, error_message=None, show_format_example=True):
        super().__init__(parent)
        self.setWindowTitle("Ошибка импорта")
        self.setModal(True)
        self.setMinimumWidth(700)
        self.error_message = error_message or "Файл имеет неправильный формат данных"
        self.show_format_example = show_format_example

        # Устанавливаем высоту в зависимости от того, показываем ли пример
        if show_format_example:
            self.setMinimumHeight(600)
        else:
            self.setMinimumHeight(250)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
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

        # Показываем пример формата только если это ошибка валидации
        if self.show_format_example:
            desc = QLabel("Пример правильного формата данных:")
            desc.setStyleSheet(f"color: {COLORS['muted_foreground']}; margin-top: 8px;")
            layout.addWidget(desc)

        # Компактный пример JSON
        compact_example = '''{
  "events": [
    {
      "sport": "Футбол",
      "tournament": "Российская Премьер-Лига",
      "country": "Россия",
      "team1": "Зенит",
      "team2": "Спартак",
      "date": "15.03.2025 19:00",
      "bookmakers": ["1xBet", "Fonbet"],
      "coefficients": {
        "p1": 1.85,
        "x": 3.45,
        "p2": 4.20
      }
    }
  ]
}'''

        json_example = QTextEdit()
        json_example.setReadOnly(True)
        json_example.setFixedHeight(240)
        json_example.setPlainText(compact_example)
        json_example.setStyleSheet(f"""
            QTextEdit {{
                background-color: #f5f5f5;
                border: 1px solid {COLORS['border']};
                border-radius: 6px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 12px;
                line-height: 1.4;
            }}
        """)

        if self.show_format_example:
            layout.addWidget(json_example)

            # Подсказка о CSV формате
            csv_hint = QLabel(" <i>Также поддерживается CSV формат с теми же полями</i>")
            csv_hint.setTextFormat(Qt.TextFormat.RichText)
            csv_hint.setStyleSheet(f"color: {COLORS['muted_foreground']}; font-size: 11px; margin-top: 4px; padding: 4px;")
            layout.addWidget(csv_hint)
        else:
            # Для критических ошибок (БД, сеть) показываем только сообщение
            help_text = QLabel("Проверьте подключение к базе данных и повторите попытку.")
            help_text.setStyleSheet(f"color: {COLORS['muted_foreground']}; margin-top: 8px;")
            help_text.setWordWrap(True)
            layout.addWidget(help_text)

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

        # Получаем главное окно
        main_window = self.window()
        dialog = ImportDialog(self, db_manager=db_manager, main_window=main_window)
        result = dialog.exec()

        # Обновление списка событий теперь выполняется в on_import_finished
        # до закрытия диалога, поэтому здесь ничего не делаем

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
