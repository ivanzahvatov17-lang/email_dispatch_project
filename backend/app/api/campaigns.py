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

import smtplib
from email.mime.text import MIMEText

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


class CampaignSendIn(BaseModel):
    group_id: Optional[int] = None
    emails: Optional[List[str]] = []


# --- Создать кампанию ---
@router.post("/", response_model=dict)
def create_campaign(data: CampaignIn, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    user = get_current_user(token)

    tpl = db.query(models.Template).filter(models.Template.id == data.template_id).first()
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")

    campaign = models.Campaign(
        name=data.name,
        template_id=tpl.id,
        creator_id=user.id,
        scheduled_at=data.scheduled_at,
        status="scheduled" if data.scheduled_at else "draft",
    )
    db.add(campaign)
    db.commit()
    db.refresh(campaign)

    # Добавляем получателей
    for cid in data.recipient_client_ids:
        client = db.query(models.Client).filter(models.Client.id == cid).first()
        if client:
            cr = models.CampaignRecipient(
                campaign_id=campaign.id,
                client_id=client.id,
                status="pending"
            )
            db.add(cr)
    db.commit()

    if data.scheduled_at:
        schedule_campaign(campaign.id, data.scheduled_at)

    return {"id": campaign.id, "status": campaign.status}


# --- Запустить кампанию немедленно ---
@router.post("/{campaign_id}/start_now")
def start_campaign_now(campaign_id: int, token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    schedule_campaign(campaign.id, datetime.utcnow())
    campaign.status = "scheduled"
    db.commit()
    return {"status": "scheduled"}


# --- Список кампаний ---
@router.get("/", response_model=List[dict])
def list_campaigns(token: Optional[str] = Header(None), db: Session = Depends(get_db)):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    rows = db.query(models.Campaign).all()
    return [
        {
            "id": r.id,
            "name": r.name,
            "status": r.status,
            "scheduled_at": r.scheduled_at.isoformat() if r.scheduled_at else None,
        }
        for r in rows
    ]


# --- Отправить кампанию выбранной группе или по списку email ---
@router.post("/{campaign_id}/send")
def send_campaign_to_group(
    campaign_id: int,
    data: CampaignSendIn,
    token: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    if token is None:
        raise HTTPException(status_code=401, detail="Требуется токен")
    _ = get_current_user(token)

    campaign = db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Кампания не найдена")

    template = db.query(models.Template).filter(models.Template.id == campaign.template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не найден")

    # --- Собираем список email ---
    clients_emails = []

    # 1. Если передали group_id, достаём клиентов из группы
    if data.group_id:
        group = db.query(models.Group).filter(models.Group.id == data.group_id).first()
        if not group:
            raise HTTPException(status_code=404, detail="Группа не найдена")
        group_clients = db.query(models.Client).join(models.clients_groups).filter(
            models.clients_groups.c.group_id == group.id
        ).all()
        clients_emails.extend([c.email for c in group_clients])

    # 2. Добавляем email из body запроса
    if data.emails:
        clients_emails.extend(data.emails)

    if not clients_emails:
        raise HTTPException(status_code=400, detail="Нет клиентов для рассылки")

    # --- SMTP настройки ---
    settings = {s.key: s.value for s in db.query(models.Setting).all()}
    required = ["SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SMTP_FROM"]
    for r in required:
        if r not in settings:
            raise HTTPException(status_code=500, detail=f"Отсутствует настройка: {r}")

    # --- Отправка писем ---
    try:
        server = smtplib.SMTP(settings["SMTP_HOST"], int(settings["SMTP_PORT"]))
        server.starttls()
        server.login(settings["SMTP_USER"], settings["SMTP_PASS"])

        sent = 0
        for email in clients_emails:
            msg = MIMEText(template.body, "html", "utf-8")
            msg["Subject"] = template.subject
            msg["From"] = settings["SMTP_FROM"]
            msg["To"] = email

            server.sendmail(settings["SMTP_FROM"], email, msg.as_string())
            sent += 1

        server.quit()
        campaign.status = "completed"
        db.commit()

        return {"status": "success", "sent": sent, "campaign_id": campaign.id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при отправке: {e}")
