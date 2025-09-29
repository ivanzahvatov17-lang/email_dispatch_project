# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QMessageBox, QComboBox, QLabel
)
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


class CampaignManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление кампаниями")
        self.resize(700, 650)

        layout = QVBoxLayout()

        # Создание кампании
        create_layout = QHBoxLayout()
        self.new_name_input = QLineEdit()
        self.new_name_input.setPlaceholderText("Название новой кампании")
        create_layout.addWidget(self.new_name_input)
        self.create_btn = QPushButton("Создать кампанию")
        self.create_btn.clicked.connect(self.create_campaign)
        create_layout.addWidget(self.create_btn)
        layout.addLayout(create_layout)

        # Таблица кампаний
        self.campaign_table = QTableWidget()
        self.campaign_table.setColumnCount(3)
        self.campaign_table.setHorizontalHeaderLabels(["ID", "Название", "Статус"])
        self.campaign_table.cellClicked.connect(self.load_recipients)
        layout.addWidget(self.campaign_table)

        # Таблица участников
        self.recipient_table = QTableWidget()
        self.recipient_table.setColumnCount(3)
        self.recipient_table.setHorizontalHeaderLabels(["ID клиента", "ФИО", "Статус"])
        layout.addWidget(self.recipient_table)

        # Добавление клиента через выпадающий список
        client_layout = QHBoxLayout()
        client_layout.addWidget(QLabel("Выберите клиента:"))
        self.client_combo = QComboBox()
        client_layout.addWidget(self.client_combo)
        self.add_client_btn = QPushButton("Добавить клиента")
        self.add_client_btn.clicked.connect(self.add_client_to_campaign)
        client_layout.addWidget(self.add_client_btn)
        layout.addLayout(client_layout)

        # Кнопки действий
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить кампании")
        self.refresh_btn.clicked.connect(self.load_campaigns)
        btn_layout.addWidget(self.refresh_btn)

        self.remove_client_btn = QPushButton("Удалить клиента")
        self.remove_client_btn.clicked.connect(self.remove_client_from_campaign)
        btn_layout.addWidget(self.remove_client_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.load_clients()
        self.load_campaigns()

    def load_clients(self):
        """Загружаем всех клиентов для выпадающего списка"""
        headers = {"token": self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/clients/", headers=headers, timeout=5)
            if resp.status_code == 200:
                self.clients = resp.json()  # Сохраняем список клиентов
                self.client_combo.clear()
                for client in self.clients:
                    display_name = client.get("full_name", f"Клиент {client['id']}")
                    self.client_combo.addItem(display_name, client["id"])
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить список клиентов: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке клиентов: {e}")

    def create_campaign(self):
        name = self.new_name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название кампании")
            return
        data = {"name": name, "template_id": 1, "recipient_client_ids": []}  # template_id=1 для демо
        headers = {"token": self.token}
        try:
            resp = requests.post(f"{BACKEND_URL}/campaigns/", json=data, headers=headers, timeout=5)
            if resp.status_code == 200:
                QMessageBox.information(self, "Успех", f"Кампания '{name}' создана")
                self.new_name_input.clear()
                self.load_campaigns()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать кампанию: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при создании кампании: {e}")

    def load_campaigns(self):
        headers = {"token": self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/campaigns/", headers=headers, timeout=5)
            if resp.status_code == 200:
                campaigns = resp.json()
                self.campaign_table.setRowCount(len(campaigns))
                for row, c in enumerate(campaigns):
                    self.campaign_table.setItem(row, 0, QTableWidgetItem(str(c["id"])))
                    self.campaign_table.setItem(row, 1, QTableWidgetItem(c["name"]))
                    self.campaign_table.setItem(row, 2, QTableWidgetItem(c["status"]))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить список кампаний: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запросе кампаний: {e}")

    def load_recipients(self, row, column):
        campaign_id_item = self.campaign_table.item(row, 0)
        if not campaign_id_item:
            return
        campaign_id = int(campaign_id_item.text())
        headers = {"token": self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/campaigns/{campaign_id}/recipients", headers=headers, timeout=5)
            if resp.status_code == 200:
                recipients = resp.json()
                self.recipient_table.setRowCount(len(recipients))
                for r, rec in enumerate(recipients):
                    self.recipient_table.setItem(r, 0, QTableWidgetItem(str(rec["client_id"])))
                    self.recipient_table.setItem(r, 1, QTableWidgetItem(rec.get("full_name", f"Клиент {rec['client_id']}")))
                    self.recipient_table.setItem(r, 2, QTableWidgetItem(rec["status"]))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить участников: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запросе участников: {e}")

    def add_client_to_campaign(self):
        row = self.campaign_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите кампанию")
            return
        campaign_id = int(self.campaign_table.item(row, 0).text())
        client_id = self.client_combo.currentData()  # Берём ID выбранного клиента
        headers = {"token": self.token}
        try:
            resp = requests.post(f"{BACKEND_URL}/campaigns/{campaign_id}/add_client/{client_id}", headers=headers, timeout=5)
            if resp.status_code == 200:
                QMessageBox.information(self, "Успех", "Клиент добавлен в кампанию")
                self.load_recipients(row, 0)
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось добавить клиента: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении клиента: {e}")

    def remove_client_from_campaign(self):
        camp_row = self.campaign_table.currentRow()
        rec_row = self.recipient_table.currentRow()
        if camp_row < 0 or rec_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите кампанию и клиента")
            return
        campaign_id = int(self.campaign_table.item(camp_row, 0).text())
        client_id = int(self.recipient_table.item(rec_row, 0).text())
        headers = {"token": self.token}
        try:
            resp = requests.delete(f"{BACKEND_URL}/campaigns/{campaign_id}/remove_client/{client_id}", headers=headers, timeout=5)
            if resp.status_code == 200:
                QMessageBox.information(self, "Успех", "Клиент удален из кампании")
                self.load_recipients(camp_row, 0)
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить клиента: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при удалении клиента: {e}")
