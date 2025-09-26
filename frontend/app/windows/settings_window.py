import json
import requests
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class SettingsWindow(QDialog):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.setWindowTitle("Настройки")
        self.resize(400, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("SMTP Host"))
        self.smtp_host = QLineEdit()
        layout.addWidget(self.smtp_host)

        layout.addWidget(QLabel("SMTP Port"))
        self.smtp_port = QLineEdit()
        layout.addWidget(self.smtp_port)

        layout.addWidget(QLabel("SMTP User"))
        self.smtp_user = QLineEdit()
        layout.addWidget(self.smtp_user)

        layout.addWidget(QLabel("SMTP Password"))
        self.smtp_pass = QLineEdit()
        layout.addWidget(self.smtp_pass)

        layout.addWidget(QLabel("SMTP From"))
        self.smtp_from = QLineEdit()
        layout.addWidget(self.smtp_from)

        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        try:
            resp = requests.get(f"http://127.0.0.1:8000/settings/smtp", headers={"token": self.token})
            if resp.status_code == 200:
                data = json.loads(resp.json()["value"])
                self.smtp_host.setText(data.get("host",""))
                self.smtp_port.setText(str(data.get("port","")))
                self.smtp_user.setText(data.get("user",""))
                self.smtp_pass.setText(data.get("pass",""))
                self.smtp_from.setText(data.get("from",""))
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить настройки: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке: {e}")

    def save_settings(self):
        data = {
            "host": self.smtp_host.text(),
            "port": int(self.smtp_port.text()),
            "user": self.smtp_user.text(),
            "pass": self.smtp_pass.text(),
            "from": self.smtp_from.text()
        }
        try:
            resp = requests.post(f"http://127.0.0.1:8000/settings/smtp",
                                 headers={"token": self.token},
                                 json={"value": json.dumps(data)})
            if resp.status_code == 200:
                QMessageBox.information(self, "Настройки", "Сохранено успешно")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить: {resp.text}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {e}")
