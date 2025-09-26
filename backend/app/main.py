# backend/app/main.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Подключаем все наши API-модули
from .api import auth, users, clients
from .api import templates, campaigns

from .db import engine, SessionLocal
from .models import Base, User
from .scheduler import start_scheduler
from .api import settings  # импорт
from .api import groups  # импорт нового модуля



app = FastAPI(title="Email Dispatch - Backend ")

# Настройка CORS для фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можно ограничить фронтенд-доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clients.router)       # <-- добавлено
app.include_router(templates.router)
app.include_router(campaigns.router)
app.include_router(settings.router)
app.include_router(groups.router)

@app.on_event("startup")
def on_startup():
    # Создаём таблицы, если их ещё нет
    Base.metadata.create_all(bind=engine)

    # Старт планировщика
    start_scheduler()

    # Добавление тестового пользователя admin, если его нет
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == 'admin').first()
        if not admin:
            admin = User(
                username='admin',
                password='admin',  # для демо, хеширование в реальном проекте обязательно
                full_name='Администратор',
                email='admin@example.com',
                is_active=True
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()
