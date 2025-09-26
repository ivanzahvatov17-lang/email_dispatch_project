# backend/app/scheduler.py
# -*- coding: utf-8 -*-
"""
Планировщик рассылок (APScheduler).
Функции для расписания и запуска кампаний.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .db import SessionLocal
from . import models
from .emailer import send_email_smtp
import logging

scheduler = BackgroundScheduler()

def _send_campaign_task(campaign_id: int):
    """
    Задача отправки кампании: берёт кампанию, её шаблон и получателей,
    формирует письма по шаблону (простая подстановка {{full_name}}) и отправляет через emailer.
    Результаты записываются в таблицу emails и campaign_recipients.status.
    """
    sess = SessionLocal()
    try:
        campaign = sess.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
        if not campaign:
            logging.error(f"Campaign {campaign_id} not found")
            return

        # Меняем статус кампании на running
        campaign.status = 'running'
        sess.commit()

        # Загружаем шаблон
        template = sess.query(models.Template).filter(models.Template.id == campaign.template_id).first()
        if not template:
            sess.add(models.Log(level='ERROR', message=f'Campaign {campaign_id}: template not found'))
            sess.commit()
            return

        # Получатели кампании
        recipients = sess.query(models.CampaignRecipient).filter(models.CampaignRecipient.campaign_id == campaign_id).all()
        for r in recipients:
            client = sess.query(models.Client).filter(models.Client.id == r.client_id).first()
            if not client:
                r.status = 'failed'
                sess.commit()
                continue

            subject = template.subject or ""
            # Простая подстановка переменных (можно расширить на Jinja2)
            body = (template.body_html or "").replace("{{full_name}}", client.full_name or "")

            # Отправляем
            message_id = send_email_smtp(client.email, subject, body, attachments=None)
            # Запись в Email таблицу (ассоциация)
            email_record = models.Email(
                campaign_id=campaign.id,
                client_id=client.id,
                subject=subject,
                body=body,
                status='sent' if message_id else 'failed',
                sent_at=datetime.utcnow() if message_id else None,
                message_id=message_id
            )
            sess.add(email_record)

            # Обновляем статус получателя
            r.status = 'sent' if message_id else 'failed'
            sess.commit()

        campaign.status = 'finished'
        sess.commit()
        sess.add(models.Log(level='INFO', message=f'Campaign {campaign_id} finished'))
        sess.commit()
    except Exception as e:
        sess.add(models.Log(level='ERROR', message=f'Campaign {campaign_id} send exception: {e}'))
        sess.commit()
    finally:
        sess.close()

def schedule_campaign(campaign_id: int, run_at: datetime):
    """
    Добавляет задачу отправки кампании в APScheduler.
    run_at — datetime (UTC или локальное; используйте одинаковую зону).
    """
    job_id = f"campaign_{campaign_id}"
    # Если уже есть задача с таким id — удалить (адекватная замена)
    try:
        if scheduler.get_job(job_id):
            scheduler.remove_job(job_id)
    except Exception:
        pass
    scheduler.add_job(_send_campaign_task, 'date', run_date=run_at, args=[campaign_id], id=job_id)

def start_scheduler():
    """Запустить планировщик и (при старте) автоматически расписать все кампании в статусе scheduled."""
    scheduler.start()
    # При старте — просмотреть базы и расписать кампании со статусом 'scheduled'
    sess = SessionLocal()
    try:
        scheduled = sess.query(models.Campaign).filter(models.Campaign.status == 'scheduled').all()
        for c in scheduled:
            if c.scheduled_at:
                try:
                    schedule_campaign(c.id, c.scheduled_at)
                except Exception as e:
                    sess.add(models.Log(level='ERROR', message=f"Failed scheduling campaign {c.id}: {e}"))
                    sess.commit()
    finally:
        sess.close()
