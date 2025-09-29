from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QFormLayout
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

class UserManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление пользователями")
        self.resize(600, 400)

        layout = QVBoxLayout()

        # Таблица пользователей
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Имя пользователя", "Email"])
        layout.addWidget(self.table)

        # Кнопки
        self.refresh_btn = QPushButton("Обновить список пользователей")
        self.refresh_btn.clicked.connect(self.load_users)
        layout.addWidget(self.refresh_btn)

        self.add_btn = QPushButton("Добавить пользователя")
        self.add_btn.clicked.connect(self.add_user_dialog)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)
        self.load_users()

    def load_users(self):
        headers = {'token': self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/users/", headers=headers, timeout=5)
            if resp.status_code == 200:
                users = resp.json()
                self.table.setRowCount(len(users))
                for row, user in enumerate(users):
                    self.table.setItem(row, 0, QTableWidgetItem(str(user.get('id',''))))
                    self.table.setItem(row, 1, QTableWidgetItem(user.get('username','')))
                    self.table.setItem(row, 2, QTableWidgetItem(user.get('email','')))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось получить пользователей: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка запроса: {e}")

    def add_user_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить пользователя")
        form = QFormLayout(dialog)

        username_input = QLineEdit()
        email_input = QLineEdit()
        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.EchoMode.Password)

        form.addRow("Имя пользователя:", username_input)
        form.addRow("Email:", email_input)
        form.addRow("Пароль:", password_input)

        submit_btn = QPushButton("Создать")
        form.addRow(submit_btn)

        def submit():
            headers = {'token': self.token}
            data = {
                "username": username_input.text(),
                "email": email_input.text(),
                "password": password_input.text()
            }
            try:
                resp = requests.post(f"{BACKEND_URL}/users/", headers=headers, json=data, timeout=5)
                if resp.status_code == 200:
                    QMessageBox.information(self, "Успех", "Пользователь создан")
                    dialog.close()
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось создать пользователя: {resp.text}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Ошибка запроса: {e}")

        submit_btn.clicked.connect(submit)
        dialog.exec()
