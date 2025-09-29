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
from .client_management_window import ClientManagementWindow
from .group_management_window import GroupManagementWindow
from .send_campaign_window import SendCampaignWindow
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
        menu_settings = menubar.addMenu('Настройки')
        menu_help = menubar.addMenu('Помощь')

        # Настройки и управление
        actions = {
            "SMTP настройки": self.open_smtp_settings,
            "Пользователи": self.open_user_management,
            "Клиенты": self.open_client_management,
            "Группы": self.open_group_management,
            "Шаблоны": self.open_template_management,
            "Кампании": self.open_campaign_management,
            "О системе": self.open_about
        }

        for name, func in actions.items():
            act = QAction(name, self)
            act.triggered.connect(func)
            menu_settings.addAction(act)

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

        # Кнопки быстрого доступа
        btns = [
            ("Показать пользователей", self.show_users),
            ("Показать клиентов", self.show_clients),
            ("Показать шаблоны", self.show_templates),
            ("Показать кампании", self.show_campaigns),
            ("Управление рассылкой", self.open_send_campaign)  # новая форма
        ]
        for text, func in btns:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            layout.addWidget(btn)

        central.setLayout(layout)
        self.setCentralWidget(central)

    # --- Универсальный метод открытия окна с токеном ---
    def _open_window(self, window_class, **kwargs):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        window_class(token=self.token, **kwargs).exec()

    # --- Методы открытия окон ---
    def open_user_management(self):
        self._open_window(UserManagementWindow)

    def open_client_management(self):
        self._open_window(ClientManagementWindow)

    def open_group_management(self):
        self._open_window(GroupManagementWindow)

    def open_template_management(self):
        self._open_window(TemplateManagementWindow)

    def open_campaign_management(self):
        self._open_window(CampaignManagementWindow)

    def open_smtp_settings(self):
        self._open_window(SettingsWindow)

    def open_help(self):
        HelpWindow().exec()

    def open_about(self):
        QMessageBox.information(self, "О системе", "Email Dispatch Demo\nВерсия 1.0\nАвтор: Захватов Иван Алексеевич")

    def open_send_campaign(self):
        """Открыть форму создания и управления рассылкой"""
        self._open_window(SendCampaignWindow, campaign_id=1)  # если фиксированная кампания ID=1

    # --- API-запросы ---
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

    def show_users(self):
        self._show_api_data("/users/", "Пользователи", lambda u: f'{u["id"]}: {u["username"]} ({u.get("email","")})')

    def show_clients(self):
        self._show_api_data("/clients/", "Клиенты", lambda c: f'{c["id"]}: {c["full_name"]} ({c.get("email","")})')

    def show_templates(self):
        self._show_api_data("/templates/", "Шаблоны", lambda t: f'{t["id"]}: {t["name"]}')

    def show_campaigns(self):
        self._show_api_data("/campaigns/", "Кампании", lambda c: f'{c["id"]}: {c["name"]} [{c["status"]}]')

    def send_campaign(self):
        """Открыть форму управления рассылкой (тот же метод, что и кнопка)"""
        self.open_send_campaign()

    def preview_email(self, campaign_id: int, client_id: int):
        if not self.token:
            QMessageBox.warning(self, "Ошибка", "Токен не задан")
            return
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/emails/{campaign_id}/{client_id}", headers=headers, timeout=5)
            if resp.status_code == 200:
                email_data = resp.json()
                EmailPreviewWindow(subject=email_data.get('subject', ''),
                                   body=email_data.get('body', '')).exec()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить письмо: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке письма: {e}")
