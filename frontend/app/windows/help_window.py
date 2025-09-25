# frontend/app/windows/help_window.py
# -*- coding: utf-8 -*-
"""Окно 'Справка по системе' — содержит ФИО автора (требование)."""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt

class HelpWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Справка по системе')
        self.resize(480, 320)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        # Здесь укажите ФИО автора — замените на реальные данные при подготовке ВКР
        lbl_info = QLabel(
            "Система автоматических email-рассылок\n\n"
            "Автор: Захватов Иван Алексеевич\n"  # <-- Замените на реальные ФИО
            "Частное образовательное учреждение высшего образования\n"
            "«Московский университет имени С.Ю. Витте»\n\n"
            "Версия: демо\n"
        )
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        layout.addWidget(lbl_info)
        btn_close = QPushButton('Закрыть')
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)
        self.setLayout(layout)
