# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget

class TemplateManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление шаблонами")
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Тема"])
        layout.addWidget(self.table)

        add_btn = QPushButton("Добавить шаблон")
        layout.addWidget(add_btn)

        self.setLayout(layout)
