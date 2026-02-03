import traceback
from typing import List, Tuple

from PySide6.QtCore import QThread, Signal

from services.import_service import EventImportService, ImportValidationError


class ImportWorker(QThread):
    """Worker для асинхронного импорта событий без блокировки UI"""

    # Сигналы
    progress = Signal(int, int)  # (current, total)
    finished = Signal(int, list)  # (imported_count, errors)
    error = Signal(str)  # error_message

    def __init__(self, import_service: EventImportService, file_path: str):
        super().__init__()
        self.import_service = import_service
        self.file_path = file_path
        self._is_running = True

    def run(self):
        """Запуск импорта в отдельном потоке"""
        print(f"[ImportWorker] Начало импорта файла: {self.file_path}")

        try:
            imported_count, errors = self.import_service.import_from_file(self.file_path)
            print(f"[ImportWorker] Импорт завершен: {imported_count} событий, {len(errors)} ошибок")

            if self._is_running:
                self.finished.emit(imported_count, errors)
            else:
                print("[ImportWorker] Импорт был отменен")

        except ImportValidationError as e:
            print(f"[ImportWorker] Ошибка валидации: {e.message}")
            if self._is_running:
                self.error.emit(e.message)

        except Exception as e:
            error_msg = f"Неожиданная ошибка при импорте: {str(e)}"
            print(f"[ImportWorker] {error_msg}")
            print(f"[ImportWorker] Traceback:\n{traceback.format_exc()}")

            if self._is_running:
                self.error.emit(error_msg)

        finally:
            print("[ImportWorker] Поток импорта завершен")

    def stop(self):
        """Остановка импорта"""
        print("[ImportWorker] Запрос на остановку импорта")
        self._is_running = False
        self.wait(5000)  # Ждем максимум 5 секунд
        if self.isRunning():
            print("[ImportWorker] ВНИМАНИЕ: Поток не остановился за 5 секунд, принудительное завершение")
            self.terminate()
            self.wait()
