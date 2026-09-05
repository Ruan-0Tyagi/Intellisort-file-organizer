"""
gui/main_window.py
-------------------
Job: The visible window of the application. Lets the user pick a
folder, preview what would happen, organize it for real, or undo
the last session. This file only handles DISPLAY and USER CLICKS -
the actual file logic still lives in core/ and database/, same as
the command-line version. The GUI just calls those same functions.
"""

from pathlib import Path

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QTextEdit, QLabel, QFileDialog, QMessageBox
)

from core.scanner import scan_folder
from core.categorizer import get_category
from core.mover import move_file
from core.grouper import group_files_by_topic
from database.history import (
    init_db, new_session_id, log_move, get_last_session_id, undo_session,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IntelliSort - Intelligent File Organizer")
        self.setMinimumSize(700, 500)

        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        folder_row = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Choose a folder to organize...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_folder)
        folder_row.addWidget(self.folder_input)
        folder_row.addWidget(browse_btn)
        layout.addLayout(folder_row)

        button_row = QHBoxLayout()
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.preview)
        organize_btn = QPushButton("Organize")
        organize_btn.clicked.connect(self.organize)
        undo_btn = QPushButton("Undo Last")
        undo_btn.clicked.connect(self.undo)
        button_row.addWidget(preview_btn)
        button_row.addWidget(organize_btn)
        button_row.addWidget(undo_btn)
        layout.addLayout(button_row)

        self.status_label = QLabel("Ready.")
        layout.addWidget(self.status_label)

        self.results_area = QTextEdit()
        self.results_area.setReadOnly(True)
        layout.addWidget(self.results_area)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select folder to organize")
        if folder:
            self.folder_input.setText(folder)

    def _get_target_folder(self) -> Path | None:
        folder_text = self.folder_input.text().strip()
        if not folder_text:
            QMessageBox.warning(self, "No folder selected", "Please choose a folder first.")
            return None
        return Path(folder_text)

    def preview(self):
        target = self._get_target_folder()
        if target is None:
            return

        try:
            files = scan_folder(target)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        topic_groups = group_files_by_topic(files)
        lines = [f"Found {len(files)} file(s). Preview (nothing moved yet):\n"]

        for topic, grouped_files in topic_groups.items():
            if len(grouped_files) >= 2:
                for f in grouped_files:
                    lines.append(f"  {f.name}  ->  {topic}/")
            else:
                f = grouped_files[0]
                category = get_category(f)
                lines.append(f"  {f.name}  ->  {category}/")

        self.results_area.setPlainText("\n".join(lines))
        self.status_label.setText(f"Preview ready - {len(files)} file(s) found.")

    def organize(self):
        target = self._get_target_folder()
        if target is None:
            return

        confirm = QMessageBox.question(
            self, "Confirm Organize",
            f"This will move files inside:\n{target}\n\nContinue?",
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            files = scan_folder(target)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            return

        init_db(target)
        session_id = new_session_id()
        topic_groups = group_files_by_topic(files)

        lines = []
        moved_count = 0

        for topic, grouped_files in topic_groups.items():
            if len(grouped_files) >= 2:
                for f in grouped_files:
                    destination = move_file(f, target, topic)
                    log_move(target, session_id, f, destination)
                    lines.append(f"Moved: {f.name} -> {topic}/{destination.name}")
                    moved_count += 1
            else:
                f = grouped_files[0]
                category = get_category(f)
                destination = move_file(f, target, category)
                log_move(target, session_id, f, destination)
                lines.append(f"Moved: {f.name} -> {category}/{destination.name}")
                moved_count += 1

        self.results_area.setPlainText("\n".join(lines))
        self.status_label.setText(f"Done! Organized {moved_count} file(s). Session: {session_id}")

    def undo(self):
        target = self._get_target_folder()
        if target is None:
            return

        session_id = get_last_session_id(target)
        if session_id is None:
            QMessageBox.information(self, "Nothing to undo", "No history found for this folder.")
            return

        restored = undo_session(target, session_id)
        self.results_area.setPlainText(f"Restored {restored} file(s) to their original location.")
        self.status_label.setText(f"Undo complete - {restored} file(s) restored.")