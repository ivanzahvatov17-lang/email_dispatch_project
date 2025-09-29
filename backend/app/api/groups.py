# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from ..db import SessionLocal
from .. import models
from ..schemas import GroupCreate, GroupOut, GroupUpdate
from ..api.auth import get_current_user

router = APIRouter(prefix="/groups", tags=["groups"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Создать группу ---
@router.post("/", response_model=GroupOut)
def create_group(data: GroupCreate, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    group = models.Group(
        name=data.name,
        description=data.description
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group

# --- Список групп ---
@router.get("/", response_model=List[GroupOut])
def list_groups(db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    groups = db.query(models.Group).all()
    return groups

# --- Получить группу по ID ---
@router.get("/{group_id}", response_model=GroupOut)
def get_group(group_id: int, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")
    return group

# --- Обновить группу ---
@router.put("/{group_id}", response_model=GroupOut)
def update_group(group_id: int, data: GroupUpdate, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    group.name = data.name or group.name
    group.description = data.description or group.description
    db.commit()
    db.refresh(group)
    return group

# --- Удалить группу ---
@router.delete("/{group_id}")
def delete_group(group_id: int, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    db.delete(group)
    db.commit()
    return {"status": "deleted", "group_id": group_id}

# --- Добавить клиента в группу ---
@router.post("/{group_id}/add_client/{client_id}")
def add_client_to_group(group_id: int, client_id: int, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not group or not client:
        raise HTTPException(status_code=404, detail="Группа или клиент не найдены")

    if client in group.clients:
        raise HTTPException(status_code=400, detail="Клиент уже в группе")

    group.clients.append(client)
    db.commit()
    return {"status": "added", "group_id": group_id, "client_id": client_id}

# --- Удалить клиента из группы ---
@router.delete("/{group_id}/remove_client/{client_id}")
def remove_client_from_group(group_id: int, client_id: int, db: Session = Depends(get_db), token: Optional[str] = Header(None)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not group or not client:
        raise HTTPException(status_code=404, detail="Группа или клиент не найдены")

    if client not in group.clients:
        raise HTTPException(status_code=400, detail="Клиент не состоит в группе")

    group.clients.remove(client)
    db.commit()
    return {"status": "removed", "group_id": group_id, "client_id": client_id}
