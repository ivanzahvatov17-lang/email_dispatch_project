# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem

class ClientManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление клиентами")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Email", "Телефон"])
        layout.addWidget(self.table)

        add_btn = QPushButton("Добавить клиента")
        layout.addWidget(add_btn)

        self.setLayout(layout)
