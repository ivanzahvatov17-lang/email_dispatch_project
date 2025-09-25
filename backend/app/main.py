# backend/app/main.py
# -*- coding: utf-8 -*-
"""Запуск FastAPI-приложения."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, users
from .db import engine
from .models import Base

app = FastAPI(title="Email Dispatch - Backend (демо)")

# Разрешаем CORS для локального фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # для демонстрации — в продакшн сузьте
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(users.router)

@app.on_event("startup")
def on_startup():
    # Создаём таблицы, если их нет (для упрощённого локального запуска)
    Base.metadata.create_all(bind=engine)
    # При первом старте можно добавить тестового пользователя, если его нет
    from .db import SessionLocal
    from . import models
    db = SessionLocal()
    try:
        admin = db.query(models.User).filter(models.User.username == 'admin').first()
        if not admin:
            admin = models.User(username='admin', password='admin', full_name='Администратор', email='admin@example.com', is_active=True)
            db.add(admin)
            db.commit()
    finally:
        db.close()
