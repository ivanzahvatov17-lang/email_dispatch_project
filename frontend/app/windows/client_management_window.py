# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QLineEdit, QLabel, QFormLayout
)
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class AddClientDialog(QDialog):
    """Диалог для добавления нового клиента"""
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Добавить клиента")
        self.resize(400, 200)

        layout = QFormLayout()

        self.full_name_input = QLineEdit()
        self.email_input = QLineEdit()
        self.phone_input = QLineEdit()

        layout.addRow(QLabel("ФИО:"), self.full_name_input)
        layout.addRow(QLabel("Email:"), self.email_input)
        layout.addRow(QLabel("Телефон:"), self.phone_input)

        self.add_btn = QPushButton("Добавить")
        self.add_btn.clicked.connect(self.add_client)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

    def add_client(self):
        data = {
            "full_name": self.full_name_input.text(),
            "email": self.email_input.text(),
            "phone": self.phone_input.text()
        }
        headers = {"token": self.token}
        try:
            resp = requests.post(f"{BACKEND_URL}/clients/", json=data, headers=headers, timeout=5)
            if resp.status_code == 200 or resp.status_code == 201:
                QMessageBox.information(self, "Успех", "Клиент успешно добавлен")
                self.accept()  # Закрываем диалог
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить клиента: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении клиента: {e}")


class ClientManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление клиентами")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Email", "Телефон"])
        layout.addWidget(self.table)

        self.refresh_btn = QPushButton("Обновить список клиентов")
        self.refresh_btn.clicked.connect(self.load_clients)
        layout.addWidget(self.refresh_btn)

        self.add_btn = QPushButton("Добавить клиента")
        self.add_btn.clicked.connect(self.open_add_client_dialog)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

        self.load_clients()

    def load_clients(self):
        """Запрашиваем список клиентов с backend и заполняем таблицу"""
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/clients/", headers=headers, timeout=5)
            if resp.status_code == 200:
                clients = resp.json()
                self.table.setRowCount(len(clients))
                for row, client in enumerate(clients):
                    self.table.setItem(row, 0, QTableWidgetItem(str(client.get('id', ''))))
                    self.table.setItem(row, 1, QTableWidgetItem(client.get('full_name', '')))
                    self.table.setItem(row, 2, QTableWidgetItem(client.get('email', '')))
                    self.table.setItem(row, 3, QTableWidgetItem(client.get('phone', '')))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить список клиентов: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запросе клиентов: {e}")

    def open_add_client_dialog(self):
        dialog = AddClientDialog(token=self.token)
        if dialog.exec():
            self.load_clients()  # Обновляем таблицу после добавления
