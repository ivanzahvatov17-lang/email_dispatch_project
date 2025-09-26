# backend/app/main.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth, users
from .api import templates, campaigns  # <-- наши новые модули
from .db import engine
from .models import Base
from .scheduler import start_scheduler

app = FastAPI(title="Email Dispatch - Backend (демо)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(templates.router)
app.include_router(campaigns.router)

@app.on_event("startup")
def on_startup():
    # Создаём таблицы, если нужно
    Base.metadata.create_all(bind=engine)
    # Старт планировщика — перенесён в startup
    start_scheduler()
    # Добавление тестового пользователя (при необходимости)
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
