import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from ui.main_window import MainWindow


class Application:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_application()
        self.main_window = None
        
    def setup_application(self):
        self.app.setApplicationName("Анализ коэффициентов букмекерских контор")
        self.app.setOrganizationName("Odds")
        self.app.setApplicationVersion("1.0.0")
        
        self.app.setStyle("Fusion")
        
        self.load_stylesheet()
        
    def load_stylesheet(self):
        qss_path = os.path.join(os.path.dirname(__file__), 'styles', 'styles.qss')
        if os.path.exists(qss_path):
            with open(qss_path, 'r', encoding='utf-8') as f:
                self.app.setStyleSheet(f.read())
        
    def run(self):
        self.main_window = MainWindow()
        self.main_window.show()
        return self.app.exec()


def main():
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
