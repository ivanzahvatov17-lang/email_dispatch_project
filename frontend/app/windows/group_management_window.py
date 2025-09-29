# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox
)
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class GroupManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление группами")
        self.resize(700, 500)

        layout = QVBoxLayout()

        # Таблица групп
        self.group_table = QTableWidget()
        self.group_table.setColumnCount(3)
        self.group_table.setHorizontalHeaderLabels(["ID", "Название", "Описание"])
        layout.addWidget(self.group_table)

        # Кнопки управления группами
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Обновить список групп")
        self.refresh_btn.clicked.connect(self.load_groups)
        btn_layout.addWidget(self.refresh_btn)

        self.add_group_btn = QPushButton("Добавить группу")
        self.add_group_btn.clicked.connect(self.add_group)
        btn_layout.addWidget(self.add_group_btn)

        layout.addLayout(btn_layout)

        # Выпадающий список клиентов для добавления/удаления
        self.client_combo = QComboBox()
        layout.addWidget(self.client_combo)

        # Кнопки для управления клиентами в группе
        client_btn_layout = QHBoxLayout()
        self.add_client_btn = QPushButton("Добавить клиента в группу")
        self.add_client_btn.clicked.connect(self.add_client_to_group)
        client_btn_layout.addWidget(self.add_client_btn)

        self.remove_client_btn = QPushButton("Удалить клиента из группы")
        self.remove_client_btn.clicked.connect(self.remove_client_from_group)
        client_btn_layout.addWidget(self.remove_client_btn)

        layout.addLayout(client_btn_layout)

        self.setLayout(layout)

        # Загружаем данные сразу
        self.load_clients()
        self.load_groups()

    def _api_get(self, endpoint):
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.json()
            else:
                QMessageBox.warning(self, "Ошибка", f"Ошибка запроса: {resp.text}")
                return []
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка запроса: {e}")
            return []

    def _api_post(self, endpoint, data=None):
        headers = {'token': self.token}
        try:
            resp = requests.post(f"{BACKEND_URL}{endpoint}", headers=headers, json=data or {}, timeout=5)
            if resp.status_code in (200, 201):
                return resp.json()
            else:
                QMessageBox.warning(self, "Ошибка", f"Ошибка запроса: {resp.text}")
                return None
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка запроса: {e}")
            return None

    def load_clients(self):
        """Загружаем список всех клиентов для выпадающего списка"""
        clients = self._api_get("/clients/")
        self.client_combo.clear()
        for c in clients:
            self.client_combo.addItem(f'{c["id"]}: {c["full_name"]}', c["id"])

    def load_groups(self):
        """Загружаем список групп в таблицу"""
        groups = self._api_get("/groups/")
        self.group_table.setRowCount(len(groups))
        for row, g in enumerate(groups):
            self.group_table.setItem(row, 0, QTableWidgetItem(str(g.get('id', ''))))
            self.group_table.setItem(row, 1, QTableWidgetItem(g.get('name', '')))
            self.group_table.setItem(row, 2, QTableWidgetItem(g.get('description', '')))

    def add_group(self):
        """Добавляем группу с диалогом ввода имени и описания"""
        from PyQt6.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(self, "Добавить группу", "Название группы:")
        if ok and name:
            desc, ok2 = QInputDialog.getText(self, "Добавить группу", "Описание группы:")
            if ok2:
                data = {"name": name, "description": desc}
                res = self._api_post("/groups/", data)
                if res:
                    QMessageBox.information(self, "Группа добавлена", f"Группа '{name}' добавлена")
                    self.load_groups()

    def _get_selected_group_id(self):
        """Возвращает ID выбранной группы в таблице"""
        selected = self.group_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите группу в таблице")
            return None
        group_id_item = self.group_table.item(selected, 0)
        return int(group_id_item.text()) if group_id_item else None

    def add_client_to_group(self):
        group_id = self._get_selected_group_id()
        if group_id is None:
            return
        client_id = self.client_combo.currentData()
        if client_id is None:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента")
            return
        res = self._api_post(f"/groups/{group_id}/add_client/{client_id}")
        if res:
            QMessageBox.information(self, "Успех", f"Клиент добавлен в группу")

    def remove_client_from_group(self):
        group_id = self._get_selected_group_id()
        if group_id is None:
            return
        client_id = self.client_combo.currentD
