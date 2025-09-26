# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget

class GroupManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление группами")
        self.resize(500, 350)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["ID", "Название группы"])
        layout.addWidget(self.table)

        add_btn = QPushButton("Добавить группу")
        layout.addWidget(add_btn)

        self.setLayout(layout)
