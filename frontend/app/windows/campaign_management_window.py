# -*- coding: utf-8 -*-
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTableWidget

class CampaignManagementWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление кампаниями")
        self.resize(700, 400)

        layout = QVBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Название", "Шаблон", "Статус"])
        layout.addWidget(self.table)

        start_btn = QPushButton("Запустить кампанию")
        layout.addWidget(start_btn)

        self.setLayout(layout)
