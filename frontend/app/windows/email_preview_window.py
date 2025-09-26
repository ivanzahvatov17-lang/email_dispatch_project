# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTextEdit

class EmailPreviewWindow(QDialog):
    def __init__(self, subject="", body=""):
        super().__init__()
        self.setWindowTitle("Предпросмотр письма")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.subject_edit = QTextEdit(subject)
        self.subject_edit.setReadOnly(True)
        layout.addWidget(self.subject_edit)

        self.body_edit = QTextEdit(body)
        self.body_edit.setReadOnly(True)
        layout.addWidget(self.body_edit)

        self.setLayout(layout)
