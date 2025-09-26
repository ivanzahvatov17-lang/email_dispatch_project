# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class TemplateManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление шаблонами")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Тема"])
        layout.addWidget(self.table)

        self.add_btn = QPushButton("Добавить шаблон")
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

        # Загружаем шаблоны сразу
        self.load_templates()

    def load_templates(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/templates/", headers=headers, timeout=5)
            if resp.status_code == 200:
                templates = resp.json()
                self.table.setRowCount(len(templates))
                for row, tmpl in enumerate(templates):
                    self.table.setItem(row, 0, QTableWidgetItem(str(tmpl.get("id", ""))))
                    self.table.setItem(row, 1, QTableWidgetItem(tmpl.get("name", "")))
                    self.table.setItem(row, 2, QTableWidgetItem(tmpl.get("subject", "")))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить шаблоны: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке шаблонов: {e}")
