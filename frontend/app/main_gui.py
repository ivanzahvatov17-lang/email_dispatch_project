# frontend/app/main_gui.py
# -*- coding: utf-8 -*-
"""Запуск PyQt6 GUI (клиент)."""
import sys
import os
from PyQt6.QtWidgets import QApplication
from windows.login_window import LoginWindow
from windows.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    # Окно логина — диалог; если успешный вход, откроется главное окно
    login = LoginWindow()
    if login.exec():  # при успехе QDialog.accept() -> True
        main_window = MainWindow(token=login.token)
        main_window.show()
        sys.exit(app.exec())
    else:
        # пользователь отменил / не вошёл
        sys.exit(0)

if __name__ == '__main__':
    main()
