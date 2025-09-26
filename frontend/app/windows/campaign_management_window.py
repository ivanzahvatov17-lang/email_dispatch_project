# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

class CampaignManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление кампаниями")
        self.resize(700, 400)

        layout = QVBoxLayout()

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Шаблон", "Статус"])
        layout.addWidget(self.table)

        # Кнопка запуска кампании
        self.start_btn = QPushButton("Запустить кампанию")
        self.start_btn.clicked.connect(self.start_selected_campaign)
        layout.addWidget(self.start_btn)

        self.setLayout(layout)

        # Загружаем кампании при открытии окна
        self.load_campaigns()

    def load_campaigns(self):
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/campaigns/", headers=headers, timeout=5)
            if resp.status_code == 200:
                campaigns = resp.json()
                self.table.setRowCount(len(campaigns))
                for row, c in enumerate(campaigns):
                    self.table.setItem(row, 0, QTableWidgetItem(str(c['id'])))
                    self.table.setItem(row, 1, QTableWidgetItem(c['name']))
                    template_name = c.get('template_name', '—')  # если API возвращает template_name
                    self.table.setItem(row, 2, QTableWidgetItem(template_name))
                    self.table.setItem(row, 3, QTableWidgetItem(c['status']))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить кампании: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запросе: {e}")

    def start_selected_campaign(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Внимание", "Выберите кампанию для запуска")
            return

        campaign_id = self.table.item(selected, 0).text()
        headers = {'token': self.token}
        try:
            resp = requests.post(f"{BACKEND_URL}/campaigns/{campaign_id}/start_now", headers=headers, timeout=5)
            if resp.status_code == 200:
                QMessageBox.information(self, "Успех", "Кампания запущена")
                self.load_campaigns()  # обновляем статус
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось запустить кампанию: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при запуске кампании: {e}")
