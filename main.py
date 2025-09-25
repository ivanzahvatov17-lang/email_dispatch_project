# main.py
# -*- coding: utf-8 -*-
"""Корневой скрипт запуска — в демонстрационной сборке запускает backend и frontend локально.
Внимание: этот скрипт подходит для разработки. В продакшне запуск backend и frontend обычно разделён."""
import threading
import time
import subprocess
import sys
import os

def start_backend():
    # Запускаем uvicorn для backend
    cwd = os.path.join(os.getcwd(), 'backend')
    cmd = [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000', '--reload']
    print("Запуск backend:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd)

def start_frontend():
    cwd = os.path.join(os.getcwd(), 'frontend')
    cmd = [sys.executable, '-m', 'PyQt6.QtWidgets']  # not used — запускаем напрямую main_gui
    # Запуск GUI
    gui_script = os.path.join(cwd, 'app', 'main_gui.py')
    print("Запуск frontend:", gui_script)
    subprocess.run([sys.executable, gui_script], cwd=cwd)

if __name__ == '__main__':
    # Запускаем backend в отдельном потоке
    t = threading.Thread(target=start_backend, daemon=True)
    t.start()
    # Ждём, чтобы backend успел подняться
    time.sleep(1.5)
    # Запускаем frontend в основном потоке
    start_frontend()
