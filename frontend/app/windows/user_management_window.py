# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class UserManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление пользователями")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Username", "Full Name", "Email"])
        layout.addWidget(self.table)

        self.add_btn = QPushButton("Добавить пользователя")
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

        # Загружаем пользователей сразу
        self.load_users()

    def load_users(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/users/", headers=headers, timeout=5)
            if resp.status_code == 200:
                users = resp.json()
                self.table.setRowCount(len(users))
                for row, user in enumerate(users):
                    self.table.setItem(row, 0, QTableWidgetItem(str(user.get("id", ""))))
                    self.table.setItem(row, 1, QTableWidgetItem(user.get("username", "")))
                    self.table.setItem(row, 2, QTableWidgetItem(user.get("full_name", "")))
                    self.table.setItem(row, 3, QTableWidgetItem(user.get("email", "")))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить пользователей: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке пользователей: {e}")
