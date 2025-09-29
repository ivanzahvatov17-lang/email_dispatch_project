from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, QMessageBox
import requests
import os

BACKEND_URL = os.getenv('BACKEND_URL', 'http://127.0.0.1:8000')

class TemplateManagementWindow(QDialog):
    def __init__(self, token: str):
        super().__init__()
        self.token = token
        self.setWindowTitle("Управление шаблонами")
        self.resize(600, 400)
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Тема"])
        layout.addWidget(self.table)

        self.refresh_btn = QPushButton("Обновить список")
        self.refresh_btn.clicked.connect(self.load_templates)
        layout.addWidget(self.refresh_btn)

        self.add_btn = QPushButton("Добавить шаблон")
        self.add_btn.clicked.connect(self.add_template)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)
        self.load_templates()

    def load_templates(self):
        headers = {"token": self.token}
        try:
            resp = requests.get(f"{BACKEND_URL}/templates/", headers=headers)
            if resp.status_code == 200:
                templates = resp.json()
                self.table.setRowCount(len(templates))
                for row, tpl in enumerate(templates):
                    self.table.setItem(row, 0, QTableWidgetItem(str(tpl["id"])))
                    self.table.setItem(row, 1, QTableWidgetItem(tpl["name"]))
                    self.table.setItem(row, 2, QTableWidgetItem(tpl["subject"]))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить шаблоны: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def add_template(self):
        from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QPushButton
        dlg = QDialog(self)
        dlg.setWindowTitle("Новый шаблон")
        layout = QFormLayout(dlg)

        name_edit = QLineEdit()
        subject_edit = QLineEdit()
        body_edit = QTextEdit()

        layout.addRow("Название:", name_edit)
        layout.addRow("Тема:", subject_edit)
        layout.addRow("Тело письма:", body_edit)

        btn = QPushButton("Создать")
        layout.addWidget(btn)

        def create():
            data = {
                "name": name_edit.text(),
                "subject": subject_edit.text(),
                "body": body_edit.toPlainText()
            }
            headers = {"token": self.token}
            resp = requests.post(f"{BACKEND_URL}/templates/", json=data, headers=headers)
            if resp.status_code == 200 or resp.status_code == 201:
                QMessageBox.information(self, "Успех", "Шаблон создан")
                dlg.accept()
                self.load_templates()
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось создать шаблон: {resp.text}")

        btn.clicked.connect(create)
        dlg.exec()
