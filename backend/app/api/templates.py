# backend/app/api/templates.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from pydantic import BaseModel

from ..api.auth import get_current_user  # единый импорт

router = APIRouter(prefix="/templates", tags=["templates"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class TemplateIn(BaseModel):
    name: str
    subject: Optional[str] = ""
    body: Optional[str] = ""  # используем единый ключ body

# --- Создание шаблона ---
@router.post("/", response_model=dict)
def create_template(data: TemplateIn, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    user = get_current_user(token)
    if not data.name:
        raise HTTPException(status_code=400, detail="Название шаблона обязательно")
    
    tpl = models.Template(
        name=data.name,
        subject=data.subject,
        body_html=data.body,
        creator_id=user.id
    )
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return {"id": tpl.id, "name": tpl.name, "subject": tpl.subject}


# --- Получение всех шаблонов ---
@router.get("/", response_model=List[dict])
def list_templates(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)
    
    rows = db.query(models.Template).all()
    return [{"id": r.id, "name": r.name, "subject": r.subject} for r in rows]


# --- Получение одного шаблона ---
@router.get("/{tpl_id}", response_model=dict)
def get_template(tpl_id: int, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)
    
    tpl = db.query(models.Template).filter(models.Template.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"id": tpl.id, "name": tpl.name, "subject": tpl.subject, "body": tpl.body_html}


# --- Обновление шаблона ---
@router.put("/{tpl_id}", response_model=dict)
def update_template(tpl_id: int, data: TemplateIn, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)
    
    tpl = db.query(models.Template).filter(models.Template.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    
    tpl.name = data.name
    tpl.subject = data.subject
    tpl.body_html = data.body
    db.commit()
    return {"id": tpl.id, "name": tpl.name, "subject": tpl.subject}


# --- Удаление шаблона ---
@router.delete("/{tpl_id}", response_model=dict)
def delete_template(tpl_id: int, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)
    
    tpl = db.query(models.Template).filter(models.Template.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(tpl)
    db.commit()
    return {"status": "deleted", "id": tpl_id}
