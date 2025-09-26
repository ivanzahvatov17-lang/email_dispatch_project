# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.resize(400, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("SMTP Host"))
        self.smtp_host = QLineEdit()
        layout.addWidget(self.smtp_host)

        layout.addWidget(QLabel("SMTP Port"))
        self.smtp_port = QLineEdit()
        layout.addWidget(self.smtp_port)

        layout.addWidget(QLabel("SMTP User"))
        self.smtp_user = QLineEdit()
        layout.addWidget(self.smtp_user)

        layout.addWidget(QLabel("SMTP Password"))
        self.smtp_pass = QLineEdit()
        layout.addWidget(self.smtp_pass)

        layout.addWidget(QLabel("SMTP From"))
        self.smtp_from = QLineEdit()
        layout.addWidget(self.smtp_from)

        save_btn = QPushButton("Сохранить")
        layout.addWidget(save_btn)

        self.setLayout(layout)
