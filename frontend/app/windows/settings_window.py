# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton

class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Настройки")
        self.resize(400, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Настройка SMTP"))
        # Добавьте поля для smtp_host, smtp_port, smtp_user, smtp_pass, smtp_from

        save_btn = QPushButton("Сохранить")
        layout.addWidget(save_btn)

        self.setLayout(layout)
