# backend/app/db.py
# -*- coding: utf-8 -*-
"""Подключение к базе данных. По умолчанию использует SQLite для упрощённого локального запуска.
Для проверки в ВКР используйте PostgreSQL — в README описано, как восстановить дамп db_dump.sql."""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Читаем переменную окружения DATABASE_URL, если задана.
DATABASE_URL = os.getenv('DATABASE_URL', '')  # например: postgresql://user:pass@localhost:5432/dbname

if not DATABASE_URL:
    # Для удобства локальной разработки — sqlite (файл db.sqlite)
    DATABASE_URL = "sqlite:///./db.sqlite"

# echo=False — не выводим SQL по умолчанию
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
