"""
run_gui.py
----------
Entry point for the graphical version of IntelliSort.
Run this instead of main.py to launch the window-based app
instead of the command-line version.
"""

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())