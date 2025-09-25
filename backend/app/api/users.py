# backend/app/api/users.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import SessionLocal, engine
from .. import models
from ..schemas import UserCreate, UserOut
from ..api.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserOut)
def create_user(data: UserCreate, db: Session = Depends(get_db)):
    """Создать пользователя """
    existing = db.query(models.User).filter(models.User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь с таким логином уже существует")
    user = models.User(
        username=data.username,
        password=data.password,
        full_name=data.full_name,
        email=str(data.email) if data.email else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    """Список пользователей ."""
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    # проверка токена
    current = get_current_user(token)
    # в демо любой авторизованный пользователь может смотреть список
    users = db.query(models.User).all()
    return users

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    current = get_current_user(token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
