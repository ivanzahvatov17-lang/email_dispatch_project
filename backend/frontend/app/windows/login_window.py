# frontend/app/windows/login_window.py
# -*- coding: utf-8 -*-
"""Диалог входа — соответствует требованию о диалоговом окне."""
from PyQt6.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

class LoginWindow(QDialog):
    """Диалоговый экран логина. При успешной авторизации сохраняет token."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Вход в систему')
        self.resize(360, 160)
        self.token = None
        self.init_ui()

    def init_ui(self):
        self.lbl_user = QLabel('Логин:')
        self.edit_user = QLineEdit()
        self.lbl_pass = QLabel('Пароль:')
        self.edit_pass = QLineEdit()
        self.edit_pass.setEchoMode(QLineEdit.EchoMode.Password)

        self.btn_login = QPushButton('Войти')
        self.btn_login.clicked.connect(self.try_login)
        self.btn_cancel = QPushButton('Отмена')
        self.btn_cancel.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.lbl_user)
        layout.addWidget(self.edit_user)
        layout.addWidget(self.lbl_pass)
        layout.addWidget(self.edit_pass)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_cancel)
        self.setLayout(layout)

    def try_login(self):
        username = self.edit_user.text().strip()
        password = self.edit_pass.text().strip()
        if not username or not password:
            QMessageBox.warning(self, 'Ошибка', 'Введите логин и пароль')
            return
        try:
            resp = requests.post(f"{BACKEND_URL}/auth/login", json={"username": username, "password": password}, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.token = data.get('access_token')
                # Сохраняем токен в окне для передачи в MainWindow
                QMessageBox.information(self, 'Успех', 'Вход выполнен')
                self.accept()  # закрываем диалог с кодом Accepted
            else:
                QMessageBox.warning(self, 'Ошибка', f'Вход не выполнен: {resp.text}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к серверу: {e}')
