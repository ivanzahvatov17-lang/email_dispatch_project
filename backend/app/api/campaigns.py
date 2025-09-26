# backend/app/api/campaigns.py
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
from ..db import SessionLocal
from .. import models
from ..scheduler import schedule_campaign
from ..api.auth import get_current_user

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class CampaignIn(BaseModel):
    name: str
    template_id: int
    recipient_client_ids: List[int] = []
    scheduled_at: Optional[datetime] = None  # ISO format expected

@router.post("/", response_model=dict)
def create_campaign(data: CampaignIn, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    user = get_current_user(token)
    # Проверка шаблона
    tpl = db.query(models.Template).filter(models.Template.id == data.template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    campaign = models.Campaign(name=data.name, template_id=tpl.id, creator_id=user.id,
                               scheduled_at=data.scheduled_at, status='scheduled' if data.scheduled_at else 'draft')
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    # Добавляем получателей
    for cid in data.recipient_client_ids:
        client = db.query(models.Client).filter(models.Client.id == cid).first()
        if client:
            cr = models.CampaignRecipient(campaign_id=campaign.id, client_id=client.id, status='pending')
            db.add(cr)
    db.commit()
    # Если есть scheduled_at — записываем задачу в планировщик
    if data.scheduled_at:
        schedule_campaign(campaign.id, data.scheduled_at)
    return {"id": campaign.id, "status": campaign.status}

@router.post("/{campaign_id}/start_now")
def start_campaign_now(campaign_id: int, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """
    Немедленно запустить кампанию (вызовет ту же логику, что и планировщик).
    Мы просто ставим задачу на ближайшее время.
    """
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    user = get_current_user(token)
    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    # ставим задачу на сейчас
    schedule_campaign(campaign.id, datetime.utcnow())
    campaign.status = 'scheduled'
    db.commit()
    return {"status": "scheduled"}

@router.get("/", response_model=List[dict])
def list_campaigns(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)
    rows = db.query(models.Campaign).all()
    return [{"id": r.id, "name": r.name, "status": r.status, "scheduled_at": r.scheduled_at.isoformat() if r.scheduled_at else None} for r in rows]
