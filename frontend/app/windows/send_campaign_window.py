# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QListWidget, QDateTimeEdit, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import QDateTime
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


class SendCampaignWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Создание и отправка рассылки")
        self.resize(600, 500)

        layout = QVBoxLayout()

        # Название кампании
        layout.addWidget(QLabel("Название кампании"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # Шаблон
        layout.addWidget(QLabel("Шаблон"))
        self.template_box = QComboBox()
        layout.addWidget(self.template_box)

        # Вкладки: клиенты / группы
        tabs = QTabWidget()
        self.client_tab = QWidget()
        self.group_tab = QWidget()

        # Список клиентов
        cl_layout = QVBoxLayout()
        self.client_list = QListWidget()
        self.client_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        cl_layout.addWidget(self.client_list)
        self.client_tab.setLayout(cl_layout)

        # Список групп
        gr_layout = QVBoxLayout()
        self.group_list = QListWidget()
        self.group_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        gr_layout.addWidget(self.group_list)
        self.group_tab.setLayout(gr_layout)

        tabs.addTab(self.client_tab, "Клиенты")
        tabs.addTab(self.group_tab, "Группы")
        layout.addWidget(tabs)

        # Дата/время отправки
        layout.addWidget(QLabel("Время отправки (оставьте пустым для немедленной)"))
        self.datetime_edit = QDateTimeEdit()
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime_edit)

        # Кнопка
        btn = QPushButton("Создать и запустить")
        btn.clicked.connect(self.create_campaign)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        headers = {"token": self.token}
        try:
            # Шаблоны
            r = requests.get(f"{BACKEND_URL}/templates/", headers=headers, timeout=5)
            if r.status_code == 200:
                for t in r.json():
                    self.template_box.addItem(t["name"], t["id"])

            # Клиенты
            r = requests.get(f"{BACKEND_URL}/clients/", headers=headers, timeout=5)
            if r.status_code == 200:
                for c in r.json():
                    self.client_list.addItem(f'{c["id"]}: {c["full_name"]} <{c.get("email","")}>')

            # Группы
            r = requests.get(f"{BACKEND_URL}/groups/", headers=headers, timeout=5)
            if r.status_code == 200:
                for g in r.json():
                    self.group_list.addItem(f'{g["id"]}: {g["name"]} ({g.get("description","")})')

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")

    def create_campaign(self):
        name = self.name_edit.text().strip()
        template_id = self.template_box.currentData()

        # выбранные клиенты
        selected_clients = [int(item.text().split(":")[0]) for item in self.client_list.selectedItems()]
        # выбранные группы
        selected_groups = [int(item.text().split(":")[0]) for item in self.group_list.selectedItems()]

        scheduled_at = self.datetime_edit.dateTime().toString("yyyy-MM-ddTHH:mm:ss")

        if not name or not template_id or (not selected_clients and not selected_groups):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля (хотя бы один получатель)")
            return

        headers = {"token": self.token}
        payload = {
            "name": name,
            "template_id": template_id,
            "recipient_client_ids": selected_clients,
            "recipient_group_ids": selected_groups,
            "scheduled_at": scheduled_at
        }

        try:
            r = requests.post(f"{BACKEND_URL}/campaigns/", json=payload, headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                QMessageBox.information(self, "Успех", f'Кампания создана, статус: {data.get("status")}')
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать кампанию: {r.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка запроса: {e}")
