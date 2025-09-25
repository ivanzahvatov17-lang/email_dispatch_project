# frontend/app/windows/main_window.py
# -*- coding: utf-8 -*-
"""Главное окно приложения — демонстрация панели навигации, доступа к настройкам и справке."""
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QMenuBar, QMessageBox
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from .help_window import HelpWindow
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

class MainWindow(QMainWindow):
    def __init__(self, token: str = None):
        super().__init__()
        self.token = token
        self.setWindowTitle('Email Dispatch - Клиент (демо)')
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        # Меню
        menubar = self.menuBar()
        menu_file = menubar.addMenu('Файл')
        menu_settings = menubar.addMenu('Настройки')
        menu_help = menubar.addMenu('Помощь')

        # Пример пунктов меню (минимум 5 в настройках можно добавить)
        settings_action1 = QAction('SMTP настройки', self)
        settings_action2 = QAction('Пользователи', self)
        settings_action3 = QAction('Экспорт', self)
        settings_action4 = QAction('Журнал', self)
        settings_action5 = QAction('О системе', self)

        menu_settings.addAction(settings_action1)
        menu_settings.addAction(settings_action2)
        menu_settings.addAction(settings_action3)
        menu_settings.addAction(settings_action4)
        menu_settings.addAction(settings_action5)

        help_action = QAction('Справка', self)
        help_action.triggered.connect(self.open_help)
        menu_help.addAction(help_action)

        # Центральный виджет
        central = QWidget()
        layout = QVBoxLayout()
        lbl = QLabel('Добро пожаловать в систему автоматических рассылок.\n\nИспользуйте меню для навигации.')
        lbl.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(lbl)

        # Кнопки для примера: показать пользователей (делает запрос к API)
        btn_users = QPushButton('Показать список пользователей (API)')
        btn_users.clicked.connect(self.show_users)
        layout.addWidget(btn_users)

        central.setLayout(layout)
        self.setCentralWidget(central)

    def open_help(self):
        hw = HelpWindow()
        hw.exec()

    def show_users(self):
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/users/", headers=headers, timeout=5)
            if resp.status_code == 200:
                users = resp.json()
                msg = '\n'.join([f"{u['id']}: {u['username']} ({u.get('email','')})" for u in users])
                QMessageBox.information(self, 'Пользователи', msg or 'Пусто')
            else:
                QMessageBox.warning(self, 'Ошибка', f'Не удалось получить список: {resp.text}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при запросе: {e}')
