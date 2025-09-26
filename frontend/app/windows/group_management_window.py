# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class GroupManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление группами")
        self.resize(500, 350)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Название группы"])
        layout.addWidget(self.table)

        self.add_btn = QPushButton("Добавить группу")
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

        # Загружаем данные сразу
        self.load_groups()

    def load_groups(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/groups/", headers=headers, timeout=5)
            if resp.status_code == 200:
                groups = resp.json()
                self.table.setRowCount(len(groups))
                for row, group in enumerate(groups):
                    self.table.setItem(row, 0, QTableWidgetItem(str(group.get("id", ""))))
                    self.table.setItem(row, 1, QTableWidgetItem(group.get("name", "")))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить группы: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке групп: {e}")
