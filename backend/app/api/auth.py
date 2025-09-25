# backend/app/api/auth.py
# -*- coding: utf-8 -*-
"""модуль авторизации """
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..schemas import TokenOut

router = APIRouter(prefix="/auth", tags=["auth"])

# Простейшее хранилище токенов в памяти (для демо)
tokens = {}

class LoginIn(BaseModel):
    username: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    """Простой логин: возвращает access_token (строка)."""
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Неверный логин/пароль")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Пользователь не активен")
    # формируем простой токен (в реальности JWT)
    token = f"token-{user.id}-{user.username}"
    tokens[token] = user.id
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = ""):
    """Простейшее получение пользователя по токену (для демо)."""
    user_id = tokens.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Невалидный токен")
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        return user
    finally:
        db.close()
