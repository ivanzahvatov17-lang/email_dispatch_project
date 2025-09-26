# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class SettingsWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
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
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)

        # Загружаем текущие настройки
        self.load_settings()

    def load_settings(self):
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/settings/smtp", headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.smtp_host.setText(data.get("host", ""))
                self.smtp_port.setText(str(data.get("port", "")))
                self.smtp_user.setText(data.get("user", ""))
                self.smtp_pass.setText(data.get("password", ""))
                self.smtp_from.setText(data.get("from_email", ""))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить настройки: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке настроек: {e}")

    def save_settings(self):
        headers = {'token': self.token}
        payload = {
            "host": self.smtp_host.text(),
            "port": int(self.smtp_port.text() or 0),
            "user": self.smtp_user.text(),
            "password": self.smtp_pass.text(),
            "from_email": self.smtp_from.text()
        }
        try:
            resp = requests.post(f"{BACKEND_URL}/settings/smtp", json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                QMessageBox.information(self, "Настройки", "Настройки успешно сохранены")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить настройки: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении настроек: {e}")
