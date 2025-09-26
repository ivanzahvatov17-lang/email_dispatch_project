# frontend/app/windows/email_preview_window.py
# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit

class EmailPreviewWindow(QDialog):
    def __init__(self, subject: str = "", body: str = ""):
        super().__init__()
        self.setWindowTitle("Предпросмотр письма")
        self.resize(600, 400)

        layout = QVBoxLayout()

        # Поле темы письма
        self.subject_edit = QTextEdit()
        self.subject_edit.setReadOnly(True)
        self.subject_edit.setPlainText(subject)  # <-- вставляем тему письма
        layout.addWidget(self.subject_edit)

        # Поле тела письма
        self.body_edit = QTextEdit()
        self.body_edit.setReadOnly(True)
        self.body_edit.setPlainText(body)  # <-- вставляем тело письма
        layout.addWidget(self.body_edit)

        self.setLayout(layout)
