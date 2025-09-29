# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QComboBox, QLineEdit, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class SendCampaignWindow(QDialog):
    def __init__(self, token: str, campaign_id: int = None):
        super().__init__()
        self.token = token
        self.campaign_id = campaign_id
        self.selected_clients = []
        self.setWindowTitle("Управление рассылкой")
        self.resize(600, 400)
        self.init_ui()
        self.load_groups()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Выбор группы ---
        group_layout = QHBoxLayout()
        group_layout.addWidget(QLabel("Выберите группу:"))
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.load_group_clients)
        group_layout.addWidget(self.group_combo)
        layout.addLayout(group_layout)

        # --- Список выбранных клиентов ---
        layout.addWidget(QLabel("Клиенты для рассылки:"))
        self.client_list = QListWidget()
        layout.addWidget(self.client_list)

        # --- Добавление клиента вручную ---
        add_layout = QHBoxLayout()
        self.client_input = QLineEdit()
        self.client_input.setPlaceholderText("Email клиента")
        add_layout.addWidget(self.client_input)
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.add_client)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)

        # --- Удаление выбранного клиента ---
        btn_remove = QPushButton("Удалить выбранного клиента")
        btn_remove.clicked.connect(self.remove_selected_client)
        layout.addWidget(btn_remove)

        # --- Кнопка отправки ---
        btn_send = QPushButton("Отправить рассылку")
        btn_send.clicked.connect(self.send_campaign)
        layout.addWidget(btn_send)

        self.setLayout(layout)

    def load_groups(self):
        """Загрузка групп из бэкенда"""
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/groups/", headers=headers, timeout=5)
            if resp.status_code == 200:
                self.groups = resp.json()
                self.group_combo.clear()
                for g in self.groups:
                    self.group_combo.addItem(f'{g["name"]} (ID: {g["id"]})', g["id"])
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить группы: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке групп: {e}")

    def load_group_clients(self):
        """Загрузка клиентов выбранной группы"""
        self.client_list.clear()
        group_id = self.group_combo.currentData()
        if not group_id:
            return
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/clients/?group_id={group_id}", headers=headers, timeout=5)
            if resp.status_code == 200:
                self.selected_clients = [c["email"] for c in resp.json()]
                self.refresh_client_list()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить клиентов: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке клиентов: {e}")

    def refresh_client_list(self):
        self.client_list.clear()
        for email in self.selected_clients:
            self.client_list.addItem(email)

    def add_client(self):
        email = self.client_input.text().strip()
        if email and email not in self.selected_clients:
            self.selected_clients.append(email)
            self.refresh_client_list()
            self.client_input.clear()

    def remove_selected_client(self):
        selected_items = self.client_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.selected_clients.remove(item.text())
        self.refresh_client_list()

    def send_campaign(self):
        """Отправка рассылки на выбранных клиентов"""
        group_id = self.group_combo.currentData()
        if not group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите группу")
            return
        if not self.selected_clients:
            QMessageBox.warning(self, "Ошибка", "Нет клиентов для рассылки")
            return
        headers = {'token': self.token}
        try:
            resp = requests.post(
                f"{BACKEND_URL}/campaigns/{self.campaign_id}/send",
                headers=headers,
                json={"group_id": group_id, "emails": self.selected_clients},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                QMessageBox.information(self, "Успех", f"Отправлено писем: {data.get('sent',0)}")
                self.close()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось отправить рассылку: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отправке: {e}")
