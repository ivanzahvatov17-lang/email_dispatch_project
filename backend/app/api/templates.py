# backend/app/api/templates.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional
from sqlalchemy.orm import Session
from ..db import SessionLocal
from .. import models
from ..schemas import UserOut  # если нужно
from pydantic import BaseModel

router = APIRouter(prefix="/templates", tags=["templates"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class TemplateIn(BaseModel):
    name: str
    subject: Optional[str] = None
    body_html: Optional[str] = None

@router.post("/", response_model=dict)
def create_template(data: TemplateIn, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    # Простая авторизация — требуем токен (демо)
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    # В демо token проверяется в auth.tokens
    from ..api.auth import get_current_user
    user = get_current_user(token)
    tpl = models.Template(name=data.name, subject=data.subject, body_html=data.body_html, creator_id=user.id)
    db.add(tpl)
    db.commit()
    db.refresh(tpl)
    return {"id": tpl.id, "name": tpl.name}

@router.get("/", response_model=List[dict])
def list_templates(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = __import__('..api.auth', fromlist=['get_current_user'])
    from ..api.auth import get_current_user
    _ = get_current_user(token)
    rows = db.query(models.Template).all()
    return [{"id": r.id, "name": r.name, "subject": r.subject} for r in rows]

@router.get("/{tpl_id}", response_model=dict)
def get_template(tpl_id: int, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    from ..api.auth import get_current_user
    _ = get_current_user(token)
    tpl = db.query(models.Template).filter(models.Template.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"id": tpl.id, "name": tpl.name, "subject": tpl.subject, "body_html": tpl.body_html}

@router.put("/{tpl_id}", response_model=dict)
def update_template(tpl_id: int, data: TemplateIn, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    from ..api.auth import get_current_user
    _ = get_current_user(token)
    tpl = db.query(models.Template).filter(models.Template.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    tpl.name = data.name
    tpl.subject = data.subject
    tpl.body_html = data.body_html
    db.commit()
    return {"id": tpl.id, "name": tpl.name}

@router.delete("/{tpl_id}")
def delete_template(tpl_id: int, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    from ..api.auth import get_current_user
    _ = get_current_user(token)
    tpl = db.query(models.Template).filter(models.Template.id == tpl_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(tpl)
    db.commit()
    return {"status": "deleted"}
