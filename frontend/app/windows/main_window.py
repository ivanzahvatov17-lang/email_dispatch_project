# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from .help_window import HelpWindow
from .settings_window import SettingsWindow
from .user_management_window import UserManagementWindow
from .template_management_window import TemplateManagementWindow
from .campaign_management_window import CampaignManagementWindow
from .email_preview_window import EmailPreviewWindow
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')


class MainWindow(QMainWindow):
    def __init__(self, token: str = None):
        super().__init__()
        self.token = token
        self.setWindowTitle('Email Dispatch - Клиент (демо)')
        self.resize(900, 600)
        self.init_ui()

    def init_ui(self):
        # --- Меню ---
        menubar = self.menuBar()
        menu_file = menubar.addMenu('Файл')
        menu_settings = menubar.addMenu('Настройки')
        menu_help = menubar.addMenu('Помощь')

        # Настройки
        settings_action1 = QAction('SMTP настройки', self)
        settings_action2 = QAction('Пользователи', self)
        settings_action3 = QAction('Шаблоны', self)
        settings_action4 = QAction('Кампании', self)
        settings_action5 = QAction('О системе', self)

        menu_settings.addAction(settings_action1)
        menu_settings.addAction(settings_action2)
        menu_settings.addAction(settings_action3)
        menu_settings.addAction(settings_action4)
        menu_settings.addAction(settings_action5)

        # Подключаем слоты
        settings_action1.triggered.connect(self.open_smtp_settings)
        settings_action2.triggered.connect(self.open_user_management)
        settings_action3.triggered.connect(self.open_template_management)
        settings_action4.triggered.connect(self.open_campaign_management)
        settings_action5.triggered.connect(self.open_about)

        # Помощь
        help_action = QAction('Справка', self)
        help_action.triggered.connect(self.open_help)
        menu_help.addAction(help_action)

        # --- Центральный виджет ---
        central = QWidget()
        layout = QVBoxLayout()
        lbl = QLabel('Добро пожаловать в систему автоматических рассылок.\n\nИспользуйте меню или кнопки ниже.')
        lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(lbl)

        # Кнопки
        btn_users = QPushButton('Показать пользователей')
        btn_users.clicked.connect(self.show_users)
        layout.addWidget(btn_users)

        btn_clients = QPushButton('Показать клиентов')
        btn_clients.clicked.connect(self.show_clients)
        layout.addWidget(btn_clients)

        btn_templates = QPushButton('Показать шаблоны')
        btn_templates.clicked.connect(self.show_templates)
        layout.addWidget(btn_templates)

        btn_campaigns = QPushButton('Показать кампании')
        btn_campaigns.clicked.connect(self.show_campaigns)
        layout.addWidget(btn_campaigns)

        btn_send_campaign = QPushButton('Отправить кампанию ID=1')
        btn_send_campaign.clicked.connect(self.send_campaign)
        layout.addWidget(btn_send_campaign)

        central.setLayout(layout)
        self.setCentralWidget(central)

    # --- Методы открытия окон ---
    def open_help(self):
        hw = HelpWindow()
        hw.exec()

    def open_smtp_settings(self):
        w = SettingsWindow()
        w.exec()

    def open_user_management(self):
        w = UserManagementWindow()
        w.exec()

    def open_template_management(self):
        w = TemplateManagementWindow()
        w.exec()

    def open_campaign_management(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        w = CampaignManagementWindow(token=self.token)
        w.exec()

    def open_about(self):
        QMessageBox.information(self, "О системе", "Email Dispatch Demo\nВерсия 1.0\nАвтор: Юля")

    # --- API-запросы ---
    def show_users(self):
        self._show_api_data("/users/", "Пользователи", lambda u: f'{u["id"]}: {u["username"]} ({u.get("email","")})')

    def show_clients(self):
        self._show_api_data("/clients/", "Клиенты", lambda c: f'{c["id"]}: {c["full_name"]} ({c.get("email","")})')

    def show_templates(self):
        self._show_api_data("/templates/", "Шаблоны", lambda t: f'{t["id"]}: {t["name"]}')

    def show_campaigns(self):
        self._show_api_data("/campaigns/", "Кампании", lambda c: f'{c["id"]}: {c["name"]} [{c["status"]}]')

    def send_campaign(self):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        headers = {'token': self.token}
        try:
            resp = requests.post(f"{BACKEND_URL}/campaigns/1/start_now", headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                QMessageBox.information(self, "Кампания", f'Статус кампании: {data.get("status")}')
            else:
                QMessageBox.warning(self, "Ошибка", f'Не удалось запустить кампанию: {resp.text}')
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f'Ошибка при запуске кампании: {e}')

    def _show_api_data(self, endpoint, title, formatter):
        if not self.token:
            QMessageBox.warning(self, title, "Токен не задан")
            return
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers, timeout=5)
            if resp.status_code == 200:
                items = resp.json()
                msg = "\n".join([formatter(i) for i in items])
                QMessageBox.information(self, title, msg or 'Пусто')
            else:
                QMessageBox.warning(self, title, f'Не удалось получить данные: {resp.text}')
        except Exception as e:
            QMessageBox.critical(self, title, f'Ошибка запроса: {e}')

    def preview_email(self, campaign_id: int, client_id: int):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/emails/{campaign_id}/{client_id}", headers=headers, timeout=5)
            if resp.status_code == 200:
                email_data = resp.json()
                subject = email_data.get('subject', '')
                body = email_data.get('body', '')
                preview = EmailPreviewWindow(subject=subject, body=body)
                preview.exec()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить письмо: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке письма: {e}")
