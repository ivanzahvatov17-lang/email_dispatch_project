# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QMessageBox
)
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


class SendCampaignWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Отправка рассылки")
        self.resize(400, 200)

        layout = QVBoxLayout()

        # Выбор кампании
        layout.addWidget(QLabel("Выберите кампанию:"))
        self.campaign_combo = QComboBox()
        layout.addWidget(self.campaign_combo)

        # Выбор группы
        layout.addWidget(QLabel("Выберите группу:"))
        self.group_combo = QComboBox()
        layout.addWidget(self.group_combo)

        # Кнопка отправки
        send_btn = QPushButton("Отправить рассылку")
        send_btn.clicked.connect(self.send_campaign)
        layout.addWidget(send_btn)

        self.setLayout(layout)

        # Загружаем данные
        self.load_campaigns()
        self.load_groups()

    def load_campaigns(self):
        try:
            resp = requests.get(f"{BACKEND_URL}/campaigns/", headers={"token": self.token}, timeout=5)
            if resp.status_code == 200:
                campaigns = resp.json()
                for c in campaigns:
                    self.campaign_combo.addItem(c["name"], c["id"])
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить кампании: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки кампаний: {e}")

    def load_groups(self):
        try:
            resp = requests.get(f"{BACKEND_URL}/groups/", headers={"token": self.token}, timeout=5)
            if resp.status_code == 200:
                groups = resp.json()
                for g in groups:
                    self.group_combo.addItem(g["name"], g["id"])
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить группы: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки групп: {e}")

    def send_campaign(self):
        campaign_id = self.campaign_combo.currentData()
        group_id = self.group_combo.currentData()
        if not campaign_id or not group_id:
            QMessageBox.warning(self, "Ошибка", "Выберите кампанию и группу")
            return

        try:
            resp = requests.post(
                f"{BACKEND_URL}/campaigns/{campaign_id}/send",
                headers={"token": self.token},
                json={"group_id": group_id},
                timeout=10
            )
            if resp.status_code == 200:
                QMessageBox.information(self, "Успех", "Кампания успешно запущена")
                self.accept()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось отправить кампанию: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при отправке: {e}")
