# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

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
        # здесь можно подключить слот для добавления клиента
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

        # Загружаем данные сразу
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
